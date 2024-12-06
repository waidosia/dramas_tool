import asyncio
import os
from datetime import datetime

from flask import Blueprint, request

import utils.util
from app.extension import db
from app.models.configuration import Config, ImageHost, Screenshot
from app.models.publish import Publish
from app.services.media import get_media_info
from app.services.rename import standard_name
from app.services.screenshot import auto_upload
from app.services.torrent import create_torrent
from utils import util

publish_api = Blueprint('publish_api', __name__)

@publish_api.route('', methods=['POST'])
def publish():
    data = request.json
    if data is None:
        return util.json_params_error("信息缺失")
    # 处理年份
    year = datetime.fromisoformat(data['year']).year


    # db.session.add(pub)
    # db.session.commit()

    # 获取发布配置,图床配置，代理设置
    configuration = Config.query.get(1)
    if configuration is None:
        return util.json_params_error("查询发布配置失败，联系管理员吧")
    img_host = ImageHost.query.get(configuration.image_host_id)
    if img_host is None:
        return util.json_params_error("ID不存在")
    screens = Screenshot.query.all()[0]
    if screens is None:
        return util.json_params_error("获取截图配置失效")


    # 重命名(同步任务)
    res = standard_name(data['videoFolder'], data['cnName'], data['enName'], year,
                        data['season'], data['category'], data['source'], data['filmSource'], data['team'])

    results = asyncio.run(run_tasks(data, img_host, configuration, screens, res))

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
    main_title = res['mainTitle'],
    sub_title = res['subTitle'],
    torrent_path = results[0],
    torrent = open(results[0], 'rb').read(),
    video_screenshot_link = results[2]['thumbnail'],
    mediaInfo = results[1],
    first_file_name = res['firstFileName']
    )

    for i,v in enumerate(results[2]['extracted']):
        setattr(pub, f"screenshot{i+1}_link", v)


    if data['publishInfo']:
        setattr(pub, 'publish_info', data['publishInfo'])
    else:
        setattr(pub, 'publish_info', f'''
◎片　　名　{data['cnName']}
◎年　　代　{year}
◎产　　地　大陆
◎类　　别　{','.join(data['category'])}
◎语　　言　国语
◎简　　介　{data['introduction']}''')

    db.session.add(pub)
    db.session.commit()

    return util.json_success("成功",pub.id)


async def run_tasks(data, img_host, configuration, screens, res):
    tasks = [
        torrent(data['videoFolder']),
        media(res['firstFileName']),
        screenshot(img_host, configuration.proxy_url, screens, res['firstFileName'])
    ]
    return await asyncio.gather(*tasks)

async def torrent(videoFolder):
    return create_torrent(videoFolder, "temp/torrent")


async def media(firstFileName):
    return get_media_info(firstFileName)

async def screenshot(img,proxy,screen,firstFileName):
    return auto_upload(img, proxy, screen, firstFileName)