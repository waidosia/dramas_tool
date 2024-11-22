import logging
import os
import random

import cv2
import numpy as np

from utils import filename


def extract_complex_keyframes(video_path, output_path, num_images, some_threshold, start_pct, end_pct, min_interval_pct=0.01):

    os.makedirs(output_path, exist_ok=True)
    # 加载视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return ''

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps

    # 计算起止时间帧编号
    start_frame = int(total_frames * start_pct)
    end_frame = int(total_frames * end_pct)
    min_interval = duration * min_interval_pct


    # 初始化变量
    extracted_images = []
    last_keyframe_time = -min_interval

    # 生成随机时间戳
    timestamps = sorted(random.sample(range(start_frame, end_frame), num_images))

    for timestamp in timestamps:
        # 跳转到特定帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, timestamp)
        ret, frame = cap.read()
        if not ret:
            continue

        current_time = timestamp / fps
        if current_time >= last_keyframe_time + min_interval:
            std_dev = np.std(frame)

            if std_dev > some_threshold:
                frame_path = os.path.join(output_path, f"{timestamp}.png")
                cv2.imwrite(frame_path, frame)
                extracted_images.append(frame_path)
                last_keyframe_time = current_time

    cap.release()
    return extracted_images




def get_thumbnails(video_path, output_path, cols, rows, start_pct, end_pct):
    video_capture = None
    os.makedirs(output_path,exist_ok=True)

    try:
        video_capture = cv2.VideoCapture(video_path)

        if not video_capture.isOpened():
            raise Exception("Error: 无法打开视频文件")

        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        # 计算开始和结束帧
        start_frame = int(total_frames * start_pct)
        end_frame = int(total_frames * end_pct)

        # 计算每张截取图像的时间间隔
        interval = (end_frame - start_frame) // (rows * cols)

        images = []

        for i, _ in enumerate(range(rows * cols)):
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
        if len(images) < (rows * cols):
            logging.warning(f"只能获取 {len(images)} 张图像，小于预期的 {rows * cols} 张")

        resized_images = [cv2.resize(image, (0, 0), fx=1.0 / cols, fy=1.0 / cols) for image in images]

        border_size = 5
        concatenated_image = np.ones((rows * (resized_images[0].shape[0] + 2 * border_size),
                                      cols * (resized_images[0].shape[1] + 2 * border_size), 3), dtype=np.uint8) * 255

        for i, image in enumerate(resized_images):
            y_offset = i // cols * (image.shape[0] + 2 * border_size) + border_size
            x_offset = i % cols * (image.shape[1] + 2 * border_size) + border_size
            concatenated_image[y_offset:y_offset + image.shape[0],
            x_offset:x_offset + image.shape[1]] = image

        sv_path = str(os.path.join(output_path,filename.send_file_name()+".png"))
        cv2.imwrite(sv_path, concatenated_image)

    except Exception as e:
        print(f"发生异常: {e}")
        return False, str(e)

    finally:
        video_capture.release()

    print(f"拼接后的图像已保存到{sv_path}")
    return True, sv_path
