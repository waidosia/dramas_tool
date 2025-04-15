import base64
import json
import os
import queue
import threading
from datetime import datetime

import requests
from flask import Blueprint, request, Response, stream_with_context, current_app

from app.extension import db
from app.models.configuration import Config, PtGen, ImageHost, Screenshot
from app.models.publish import Publish
from app.models.task import Task, TaskLog
from app.services.media import get_media_info
from app.services.ptgen import fetch_ptgen_data
from app.services.rename import standard_name
from app.services.screenshot import get_thumbnails, extract_complex_keyframes
from app.services.torrent import create_torrent
from app.services.upload import upload_screenshot
from utils import util
from utils.tool import chinese_name_to_pinyin

publish_api = Blueprint('publish_api', __name__)

@publish_api.route('', methods=['POST'])
def publish():
    # 获取文件（如果存在的话）
    file = request.files.get('file')

    # 初始化表单数据
    form_data = request.form.to_dict()

    if file:
        # 将文件内容转换为字节流
        file_bytes = file.read()

        # 将字节流转换为 Base64 编码，并存入 form_data
        form_data['file_data'] = base64.b64encode(file_bytes).decode('utf-8')

    # 开始处理逻辑
    task = Task(
        status='created',
        form_data=json.dumps(form_data)
    )
    db.session.add(task)
    db.session.commit()

    # 启动后台任务（异步）
    run_task(task.id, form_data)

    return util.json_success("成功", data={'task_id':task.id})


@publish_api.route('/stream_log/<int:task_id>', methods=['GET'])
def stream_log(task_id):
    q = task_queues.get(task_id)
    if not q:
        return Response({"data": "任务不存在\n\n"}, mimetype="text/event-stream")

    def event_stream():
        while True:
            data = q.get()
            yield f"data: {json.dumps(data)}\n\n"

            if data.get("level") == "CLOSE":
                task = Task.query.get(task_id)
                yield f"data: ''\n\n"
                yield f"event: close\ndata: {task.status}\n\n"
                break

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream"
    )



task_queues = {}

def run_task(task_id, form_data):
    q = queue.Queue()
    task_queues[task_id] = q
    app  = current_app._get_current_object()
    thread = threading.Thread(target=handle_task, args=(app,task_id, form_data, q))
    thread.start()

def log(task_id, q, message, level="INFO", step="general",data=None):
    # 数据库持久化
    log_entry = TaskLog(task_id=task_id, message=message, level=level, step=step)
    db.session.add(log_entry)
    db.session.commit()

    # 推送到前端
    if q:
        q.put({'step': step, 'level': level, 'message': message,'data': data})

def handle_task(app,task_id, form_data, q):
    print(form_data)
    with app.app_context():
        task = None
        try:
            task = Task.query.get(task_id)
            task.status = 'running'
            db.session.commit()

            # 开始处理步骤（先按照顺序处理，暂不考虑并发）
            configuration = Config.query.get(1)
            if configuration is None:
                log(task_id, q, "获取发布配置失败", level="ERROR", step="ptgen")
                return
            # 从表单数据入手.
            # 1、判断是否存在豆瓣链接，如果存在则尝试开始PTGEN
            if form_data['ptGen'] != '':
                # 存在豆瓣链接
                log(task_id, q, "开始获取豆瓣信息...", step="ptgen")
                ptgen = PtGen.query.get(configuration.pt_gen_id)
                if ptgen is None or not ptgen.is_available:
                    log(task_id, q, "PTGEN未设置或未启用", level="ERROR", step="ptgen")
                    return

                # 获取ptgen信息
                success,res = fetch_ptgen_data(ptgen.url,form_data['ptGen'])
                if not success:
                    log(task_id, q, "获取豆瓣信息信息失败", level="ERROR", step="ptgen")
                    return

                log(task_id, q, "获取豆瓣信息成功", level="SUCCESS", step="ptgen")
                form_data['cover'] = res.poster
                form_data['cnName'] = res.cnName
                # 处理英文名称
                form_data['enName'] = chinese_name_to_pinyin(res.cnName)
                form_data['year'] = res.year
                form_data['introduction'] = res.introduction
                form_data['category'] = res.category
                form_data['publishInfo'] = res.format

            # 2、上传封面
            log(task_id, q, "开始上传封面...", step="upload_cover")
            img_host = ImageHost.query.get(configuration.image_host_id)
            if img_host is None or not img_host.is_available:
                log(task_id, q, "图床未设置或未启用", level="ERROR", step="upload_cover")
                return
            # 可能是一个文件名
            if form_data['cover'] != '' and form_data['cover'].startswith('http'):
                # 在线链接 请求在线地址，返回地址
                res = requests.get(form_data['cover'])
                if res.status_code == 200:
                    content = res.content
                else:
                    log(task_id, q, "获取在线封面失败", level="ERROR", step="upload_cover")
                    return
                success,res = upload_screenshot(img_host, content, configuration.proxy_url)
                if not success:
                    log(task_id, q, "上传在线封面失败", level="ERROR", step="upload_cover")
                    return
                form_data['cover'] = res
                log(task_id, q, "上传在线封面成功", level="SUCCESS", step="upload_cover")
            elif 'file_data' in form_data:
                # 本地图片
                file_bytes = base64.b64decode(form_data['file_data'])
                success,res = upload_screenshot(img_host, file_bytes, configuration.proxy_url)
                if not success:
                    log(task_id, q, "上传本地封面失败", level="ERROR", step="upload_cover")
                    return
                form_data['cover'] = res
                log(task_id, q, "上传本地封面成功", level="SUCCESS", step="upload_cover")
            else:
                # 没有封面
                log(task_id, q, "缺少封面", level="ERROR", step="upload_cover")
                return

            form_data['cover'] = res
            # 3、截图
            log(task_id, q, "开始截取视频帧...", step="screenshots")
            all_screens = Screenshot.query.all()
            all_screen_dict = [screen.to_dict() for screen in all_screens]
            if len(all_screen_dict) == 0:
                log(task_id, q, "无法获取截图的配置", level="ERROR", step="screenshots")
                return
            all_screen_dict = all_screen_dict[0]
            # 拿到文件夹的第一个视频
            first_video_path = get_first_video_path(form_data['videoFolder'])
            if first_video_path is None:
                log(task_id, q, "无法定位视频首集路径", level="ERROR", step="screenshots")
                return

            success,extracted_images = extract_complex_keyframes(
                first_video_path,all_screen_dict
            )
            if not success:
                log(task_id, q, "截取视频帧失败", level="ERROR", step="screenshots")
                return
            log(task_id, q, "截取视频帧成功", level="SUCCESS", step="screenshots")
            # 4、上传截图视频帧
            log(task_id, q, "开始上传视频帧...", step="upload_screenshots")

            images = {}
            for v in extracted_images:
                # 读取文件内容,调用上传脚本
                f = open(v,'rb')
                success, res = upload_screenshot(img_host, f.read(), configuration.proxy_url)
                if not success:
                    log(task_id, q, "上传视频帧失败", level="ERROR", step="upload_screenshots")
                f.close()
                images[v] = res


            log(task_id, q, "上传视频帧成功", level="SUCCESS", step="upload_screenshots")
            form_data['screenshotLink'] = [value for key, value in images.items()]

            if all_screen_dict['del_local_img']:
                log(task_id, q, "开始删除本地视频帧...", step="upload_screenshots")
                for v in extracted_images:
                    os.remove(v)
                log(task_id, q, "删除本地视频帧成功", level="SUCCESS", step="upload_screenshots")

            # 5、缩略图
            if all_screen_dict['is_thumbnail']:
                log(task_id, q, "开始获取缩略图...", step="thumbnail")
                success,thumbnails = get_thumbnails(first_video_path,all_screen_dict)
                if not success:
                    log(task_id, q, "获取缩略图失败", level="ERROR", step="thumbnail")
                    return
                log(task_id, q, "获取缩略图成功", level="SUCCESS", step="thumbnail")
            # 6、上传缩略图
                log(task_id, q, "开始上传缩略图...", step="upload_thumbnail")
                f = open(thumbnails, 'rb')
                success, res = upload_screenshot(img_host, f.read(), configuration.proxy_url)
                if not success:
                    log(task_id, q, "上传缩略图失败", level="ERROR", step="upload_thumbnail")
                f.close()

                log(task_id, q, "上传缩略图成功", level="SUCCESS", step="upload_thumbnail")
                form_data['videoScreenshotLink'] = res

                if all_screen_dict['del_local_img']:
                    log(task_id, q, "开始删除本地缩略图...", step="upload_screenshots")
                    os.remove(thumbnails)
                    log(task_id, q, "删除本地缩略图成功", level="SUCCESS", step="upload_screenshots")
            # 7、 重命名
            log(task_id, q, "开始重命名...", step="rename")
            format_str = '%a %b %d %Y %H:%M:%S GMT%z (%Z)'
            year = datetime.strptime(form_data['year'], format_str).year
            res = standard_name(
                form_data['videoFolder'], form_data['cnName'], form_data['enName'],
                year,form_data['season'], form_data['category'], form_data['source'],
                form_data['filmSource'], form_data['team']
                )
            if res is None:
                log(task_id, q, "重命名失败", level="ERROR", step="rename")
                return
            if form_data['ptGen'] == '':
                publish_info =  f'''◎片　　名　{form_data['cnName']}
◎年　　代　{year}
◎产　　地　大陆
◎类　　别　{form_data['category']}
◎语　　言　国语
◎简　　介　{form_data['introduction']}'''

            log(task_id, q, "重命名完成", level="SUCCESS", step="rename")
            form_data['mainTitle'] = res['mainTitle']
            form_data['subTitle'] = res['subTitle']
            form_data['videoFolder'] =  res['newFolderPath']
            form_data['firstFileName'] = res['firstFileName']
            form_data['publishInfo'] = publish_info
            # 8、获取 Media 信息
            log(task_id, q, "开始获取 Media 信息...", step="media")
            media = get_media_info(form_data['firstFileName'])
            if media == '':
                log(task_id, q, "Media 信息获取失败", level="ERROR", step="media")
                return
            log(task_id, q, "Media 信息获取完成", level="SUCCESS", step="media")
            form_data['mediaInfo'] = media
            # 9、制作种子
            log(task_id, q, "开始制作种子...", step="torrent")
            torrent = create_torrent(form_data['videoFolder'], "temp/torrent")
            if torrent is None:
                log(task_id, q, "种子制作失败", level="ERROR", step="torrent")
            log(task_id, q, "种子制作完成", level="SUCCESS", step="torrent")
            form_data['torrentPath'] = torrent

            log(task_id, q, "任务完成", level="SUCCESS", step="done")

            form_data['file_data'] = None
            log(task_id,q,"请核对信息",level="INSPECT",step="done",data=form_data)
            task.status = 'completed'
        except Exception as e:
            log(task_id, q, f"任务失败: {str(e)}", level="ERROR", step="error")
            task.status = 'failed'
        finally:
            db.session.commit()
            q.put({'level': 'CLOSE', 'message': '任务结束'})
            task_queues.pop(task_id, None)

@publish_api.route('/save', methods=['POST'])
def save():
    # 保存信息
    data = request.json
    if data is None:
        return util.json_params_error("信息缺失")

    format_str = '%a %b %d %Y %H:%M:%S GMT%z (%Z)'
    year = datetime.strptime(data['year'], format_str).year

    pub = Publish(
    cn_name=data['cnName'],
    en_name = data['enName'],
    year =  year,
    season = data['season'],
    film_source =  data['filmSource'],
    source = data['source'],
    team =  data['team'],
    cover=   data['cover'],
    pt_gen=  data['ptGen'],
    introduction = data['introduction'],
    category = ','.join(data['category']),
    main_title = data['mainTitle'],
    sub_title = data['subTitle'],
    torrent_path = data['torrentPath'],
    torrent = open(data['torrentPath'], 'rb').read(),
    video_screenshot_link = data['videoScreenshotLink'],
    mediaInfo = data['mediaInfo'],
    first_file_name = data['firstFileName'],
    publish_info = data['publishInfo']
    )

    for i,v in enumerate(data['screenshotLink']):
        setattr(pub, f"screenshot{i+1}_link", v)

    db.session.add(pub)
    db.session.commit()

    return util.json_success("成功",pub.id)



def get_first_video_path(folder_path):
    # 定义常见视频文件扩展名
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = []

    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(video_extensions):
                # 获取文件的绝对路径
                file_path = os.path.join(root, file)
                video_files.append(file_path)

    # 按文件名排序
    video_files.sort()

    # 如果有视频文件，返回第一个视频的绝对路径
    if video_files:
        return video_files[0]
    else:
        return None

