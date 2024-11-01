# 生成标准命名与重命名
import os
import logging
import re
import shutil

from pymediainfo import MediaInfo

from utils.festival import get_festival_blessing

# 标准命名,返回文件夹的名称
def standard_name(folder_path,cnName,enName,year,season,category,source,film_source='WEB-DL',team='GodDramas'):
    # 获取第一集的信息
    if season < 10:
        season = '0' + str(season)
    festival = get_festival_blessing()
    file_name = "{cnName}.{enName}.{year}.S{season}E???.{resolution}.{source}.{video_codec}.{audio_codec}-{team}"
    folder_name = "{cnName}.{enName}.{year}.S{season}.{resolution}.{source}.{video_codec}.{audio_codec}-{team}"
    video_files = get_video_files(folder_path)
    if len(video_files) == 0:
        return ''
    # 选择第一个视频，获取长宽
    video_info = get_video_info(video_files[0])
    if video_info is None:
        return ''
    file_name = file_name.format(cnName=cnName,enName=enName,year=year,season=season,
                                 resolution=video_info['resolution'],source=film_source,video_codec=video_info['video_codec'],
                                 audio_codec=video_info['audio_codec'],team=team)
    folder_name = folder_name.format(cnName=cnName, enName=enName, year=year, season=season,
                                   resolution=video_info['resolution'],source=film_source,video_codec=video_info['video_codec'],
                                   audio_codec=video_info['audio_codec'],team=team)
    main_title = folder_name.replace('.',' ')
    second_title = f"{cnName} | 全{len(video_files)}集 | {year}年 | {source} | 类型：{'/'.join(category)} {festival} "
    # 获取所有的视频文件，提取集数，拼接新名称，重命名
    video_files =  rename_video_files(video_files,file_name)
    if len(video_files) == 0:
        return {}
    # 重命名文件夹，返回新文件夹名称
    new_folder_path = rename_directory(folder_path,folder_name)
    return {
        'new_folder_path': new_folder_path,
        'first_file_name': video_files[0],
        'main_title' : main_title,
        'second_title' : second_title,
    }





def get_video_info(video_path):
    media_info = MediaInfo.parse(video_path)
    video_codec = None
    audio_codec = None
    width = None
    height = None

    for track in media_info.tracks:
        if track.track_type == 'Video':
            width = track.width
            height = track.height
            # 检测 x264 关键字
            if 'x264' in track.writing_library:
                video_codec = 'x264'  # 检测到 x264
            else:
                video_codec = track.format
        elif track.track_type == 'Audio':
            audio_codec = track.format

        elif track.track_type == 'Audio':
            audio_codec = track.format

    # 确定分辨率格式
    if width and height:
        min_dimension = min(width, height)
        resolution_str = f"{min_dimension}p"
    else:
        resolution_str = None

    return {
        "width": width,
        "height": height,
        "resolution": resolution_str,
        "video_codec": video_codec,
        "audio_codec": audio_codec,
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
        renamed_file = rename_file_with_same_extension(video_file, file_name.replace('???',episode_number))
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
    new_name = str(os.path.join(file_dir, new_name_without_extension + file_extension))
    shutil.move(old_name, new_name)
    logging.info(f"{old_name} 文件成功重命名为 {new_name}")
    return str(new_name)


def rename_directory(current_dir, new_name):
    if not os.path.exists(current_dir) or not os.path.isdir(current_dir):
        return ''
    parent_dir = os.path.dirname(current_dir)
    new_dir = str(os.path.join(parent_dir, new_name))
    shutil.move(current_dir, new_dir)
    return str(new_dir)
