import logging
import os
import random

import cv2
import numpy as np

from app.models.configuration import Screenshot, ImageHost
from app.services.upload import upload_screenshot
from utils import filename


def extract_complex_keyframes(video_path,screenshot, min_interval_pct=0.01):

    os.makedirs(screenshot.dir, exist_ok=True)
    # 加载视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return ''

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps

    # 计算起止时间帧编号
    start_frame = int(total_frames * screenshot.starting_point)
    end_frame = int(total_frames * screenshot.end_point)
    min_interval = duration * min_interval_pct

    # 初始化变量
    extracted_images = []
    last_keyframe_time = -min_interval

    # 生成随机时间戳
    timestamps = sorted(random.sample(range(start_frame, end_frame), screenshot.num))

    for timestamp in timestamps:
        # 跳转到特定帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, timestamp)
        ret, frame = cap.read()
        if not ret:
            continue

        current_time = timestamp / fps
        if current_time >= last_keyframe_time + min_interval:
            std_dev = np.std(frame)

            if std_dev > screenshot.complexity:
                frame_path = os.path.join(screenshot.dir, f"{filename.send_file_name()}.png")
                cv2.imwrite(frame_path, frame)
                extracted_images.append(frame_path)
                last_keyframe_time = current_time

    cap.release()
    return extracted_images




def get_thumbnails(video_path, screenshot):
    video_capture = None
    os.makedirs(screenshot.dir,exist_ok=True)

    try:
        video_capture = cv2.VideoCapture(video_path)

        if not video_capture.isOpened():
            return ''

        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        # 计算开始和结束帧
        start_frame = int(total_frames * screenshot.starting_point)
        end_frame = int(total_frames * screenshot.end_point)

        # 计算每张截取图像的时间间隔
        interval = (end_frame - start_frame) // (screenshot.thumbnail_horizontal * screenshot.thumbnail_vertical)

        images = []

        for i, _ in enumerate(range(screenshot.thumbnail_horizontal * screenshot.thumbnail_vertical)):
            frame_number = start_frame + i * interval
            if frame_number >= end_frame:
                break

            video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = video_capture.read()

            if not ret:
                logging.warning(f"无法读取第 {i + 1} 张图像")
                continue

            images.append(frame)

        # 处理图像数量小于预期的情况
        if len(images) < (screenshot.thumbnail_horizontal * screenshot.thumbnail_vertical):
            logging.warning(f"只能获取 {len(images)} 张图像，小于预期的 {screenshot.thumbnail_horizontal * screenshot.thumbnail_vertical} 张")

        resized_images = [cv2.resize(image, (0, 0), fx=1.0 / screenshot.thumbnail_vertical, fy=1.0 / screenshot.thumbnail_vertical) for image in images]

        border_size = 5
        concatenated_image = np.ones((screenshot.thumbnail_horizontal * (resized_images[0].shape[0] + 2 * border_size),
                                      screenshot.thumbnail_vertical * (resized_images[0].shape[1] + 2 * border_size), 3), dtype=np.uint8) * 255

        for i, image in enumerate(resized_images):
            y_offset = i // screenshot.thumbnail_vertical * (image.shape[0] + 2 * border_size) + border_size
            x_offset = i % screenshot.thumbnail_vertical * (image.shape[1] + 2 * border_size) + border_size
            concatenated_image[y_offset:y_offset + image.shape[0],
            x_offset:x_offset + image.shape[1]] = image

        sv_path = str(os.path.join(screenshot.dir,filename.send_file_name()+".png"))
        cv2.imwrite(sv_path, concatenated_image)

    except Exception as e:
        print(f"发生异常: {e}")
        return False, str(e)

    finally:
        video_capture.release()

    return sv_path


def auto_upload(imageHost,proxyUrl,screenshot,video_path):
    # 自动上传图片
    extracted_images = extract_complex_keyframes(video_path, screenshot)

    img = {}
    if screenshot.is_thumbnail:
        sv_path = get_thumbnails(video_path, screenshot)
        if sv_path:
            f = open(sv_path,'rb')
            data = upload_screenshot(imageHost,f.read(),proxyUrl)
            if data['url'] == '':
                print(f'{sv_path}图片上传失败')
            else:
                img['thumbnail'] = data['url']

    pic = []
    for extracted in extracted_images:
        f = open(extracted, 'rb')
        data = upload_screenshot(imageHost,f.read(),proxyUrl)
        if data['url'] == '':
            print(f'{extracted}图片上传失败')
        else:
            pic.append(data['url'])
    img['extracted'] = pic

    print(img)

    return img

if __name__ == '__main__':
    s = Screenshot()
    s.dir = 'temp/pic'
    s.num = 3
    s.complexity = 0.02
    s.is_thumbnail = True
    s.thumbnail_horizontal = 4
    s.thumbnail_vertical = 4
    s.starting_point = 0.12
    s.end_point = 0.92
    s.auto_upload = True
    s.del_local_img = True

    i = ImageHost()
    i.name = 'pixhost'
    i.url = 'https://api.pixhost.to/images'
    i.is_available = True
    i.is_proxy = False

    s = auto_upload(i,'',s,r"D:\BaiduNetdiskDownload\R-人中之凤（68集）姚宇晨\人中之凤.ren.zhong.zhi.feng.2024.S01.608p.WEB-DL.AVC.AAC-GodDramas\人中之凤.ren.zhong.zhi.feng.2024.S01E01.608p.WEB-DL.AVC.AAC-GodDramas.mp4")