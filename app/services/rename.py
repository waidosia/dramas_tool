# 生成标准命名与重命名
import os
import logging
import re
from moviepy.editor import VideoFileClip



# 生成标准文件命名
# file_name = f"{first_chinese_name}.{first_english_name}.{year} S{season}E??.{width}.{source}.{format}.{hdr_format}.{commercial_name}{channel_layout}-{team}"
# 生成标准文件夹命名
# folder_name = f"{first_chinese_name}.{first_english_name}.{year} S{season}.{width}.{source}.{format}.{hdr_format}.{commercial_name}{channel_layout}-{team}"
# 标准命名,返回文件夹的名称
def standard_name(folder_path,cnName,enName,year,season,team):
    # 获取第一集的信息
    video_files = get_video_files(folder_path)
    if len(video_files) == 0:
        return ''
    # 选择第一个视频，获取长宽



def get_video_info(video_path):
    with VideoFileClip(video_path) as video:
        width = video.w
        height = video.h
        # 取较小值来处理横竖屏
        min_dimension = min(width, height)
        # 格式化分辨率为 xxxP
        resolution_str = f"{min_dimension}P"
        resolution = (width, height)
        # video_codec = video.reader.codec
        # audio_codec = video.audio.codec if video.audio else None

    return {
        "width": width,
        "height": height,
        "resolution":   resolution_str,
        # "video_codec": video_codec,
        # "audio_codec": audio_codec,
    }






# 获取文件夹中的视频文件列表
def get_video_files(folder_path) -> list:
    try:
        # 要查找的视频文件扩展名列表
        VIDEO_EXTENSIONS = [".mp4", ".m4v", ".avi", ".flv", ".mkv", ".mpeg", ".mpg", ".rm", ".rmvb", ".ts", ".m2ts"]
        # 检查文件夹路径是否有效和可访问
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            logging.warn(f"文件夹不存在或不可访问")
            return []
        # 初始化一个空列表来存储文件路径
        video_files = []
        # 遍历文件夹中的条目
        for entry in os.scandir(folder_path):
            if entry.is_file() and entry.name.lower().endswith(tuple(VIDEO_EXTENSIONS)):
                video_files.append(entry.path)
        # 对文件列表进行排序
        video_files.sort()
        return video_files

    except Exception as e:
        logging.error(f"获取视频文件列表失败，错误原因: {e}")
        return []




# 从文件名中提取集数，并返回重命名后的文件列表
def rename_video_files(video_files, file_name) -> list:
    renamed_files = []
    for video_file in video_files:
        _, file_base = os.path.split(video_file)
        episode_number = get_episode_number(file_base)
        if episode_number is None:
            logging.error("提取集数失败，退出")
            return []
        episode_number = str(episode_number).zfill(len(str(len(video_files))))
        renamed_file = rename_file_with_same_extension(video_file, file_name.replace('??', episode_number))
        if renamed_file is not None:
            renamed_files.append(renamed_file)
    return renamed_files

# 从文件名中提取集数，
def get_episode_number(file_base) -> str or None:
    match_e = re.search(r'E(\d+)', file_base)
    if match_e:
        return match_e.group(1)
    else:
        match_digits = re.search(r'(\d+)', file_base)
        if match_digits:
            return match_digits.group(1)
    return None


def rename_file_with_same_extension(old_name, new_name_without_extension):
    if not os.path.exists(old_name):
        logging.error(f"未找到文件: '{old_name}'")
        return ''

    file_dir, file_base = os.path.split(old_name)
    file_name, file_extension = os.path.splitext(file_base)
    new_name = os.path.join(file_dir, new_name_without_extension + file_extension)
    os.rename(old_name, new_name)
    logging.info(f"{old_name} 文件成功重命名为 {new_name}")
    return str(new_name)


def rename_directory_if_needed(video_path, file_name) -> str:
    directory_path = os.path.dirname(video_path)
    if 'E??' in file_name:
        rename_dir = rename_directory(directory_path, file_name.replace('E??', ''))
        return rename_dir


def rename_directory(current_dir, new_name):
    if not os.path.exists(current_dir) or not os.path.isdir(current_dir):
        return ''
    parent_dir = os.path.dirname(current_dir)
    new_dir = os.path.join(parent_dir, new_name)
    os.rename(current_dir, new_dir)
    return str(new_dir)

if __name__ == '__main__':
    info = get_video_info(r"D:\BaiduNetdiskDownload\16.庆余年之帝王业（52集）舒童 李子峰\1.mp4")
    print(info)