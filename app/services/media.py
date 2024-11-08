import json
import logging
import os

from pymediainfo import MediaInfo

# 预定义每种 track 类型的属性标签列表
TRACK_ATTRIBUTES = {
    "General": [
        ("other_unique_id", "Unique ID"),
        ("complete_name", "Complete name"),
        ("other_format", "Format"),
        ("format_version", "Format version"),
        ("other_file_size", "File size"),
        ("other_duration", "Duration"),
        ("other_overall_bit_rate_mode", "Overall bit rate mode"),
        ("other_overall_bit_rate", "Overall bit rate"),
        ("other_frame_rate", "Frame rate"),
        ("movie_name", "Movie name"),
        ("encoded_date", "Encoded date"),
        ("writing_application", "Writing application"),
        ("writing_library", "Writing library"),
        ("comment", "Comment"),
    ],
    "Video": [
        ("track_id", "ID"),
        ("other_format", "Format"),
        ("format_info", "Format/Info"),
        ("other_duration", "Duration"),
        ("other_bit_rate", "Bit rate"),
        ("other_width", "Width"),
        ("other_height", "Height"),
        ("other_display_aspect_ratio", "Display aspect ratio"),
        ("other_frame_rate", "Frame rate"),
        ("color_space", "Color space"),
        ("other_bit_depth", "Bit depth"),
        ("scan_type", "Scan type"),
        ("other_stream_size", "Stream size"),
        ("other_writing_library", "Writing library"),
    ],
    "Audio": [
        ("track_id", "ID"),
        ("other_format", "Format"),
        ("other_duration", "Duration"),
        ("other_bit_rate", "Bit rate"),
        ("other_channel_s", "Channel(s)"),
        ("other_sampling_rate", "Sampling rate"),
        ("other_compression_mode", "Compression mode"),
        ("other_stream_size", "Stream size"),
        ("title", "Title"),
        ("other_language", "Language"),
        ("default", "Default"),
        ("forced", "Forced"),
    ],
    "Text": [
        ("other_track_id", "ID"),
        ("other_format", "Format"),
        ("codec_id", "Codec ID"),
        ("other_duration", "Duration"),
        ("other_bit_rate", "Bit rate"),
        ("other_frame_rate", "Frame rate"),
        ("count_of_elements", "Count of elements"),
        ("other_stream_size", "Stream size"),
        ("title", "Title"),
        ("other_language", "Language"),
        ("default", "Default"),
        ("forced", "Forced"),
    ]
}


def get_media_info(file_path):
    logging.info("开始获取视频信息")

    if not os.path.exists(file_path):
        logging.error("文件路径不存在")
        return False, "视频文件路径不存在"

    original_working_directory = os.getcwd()
    parent_directory = os.path.abspath(os.path.join(file_path, os.pardir))
    relative_file_path = os.path.relpath(file_path, parent_directory)
    os.chdir(parent_directory)
    logging.info(f"切换到新的工作目录 {parent_directory}")

    try:
        media_info = MediaInfo.parse(relative_file_path)
        data = json.loads(media_info.to_json())

        output = ""
        for track in data["tracks"]:
            track_type = track["track_type"]
            if track_type in TRACK_ATTRIBUTES:
                output += handle_track(track, track_type)

        return True, output

    except OSError as e:
        logging.error(f"文件路径错误: {e}")
        return False, f"文件路径错误: {e}"

    except Exception as e:
        logging.error(f"无法解析文件: {e}")
        return False, f"无法解析文件: {e}"

    finally:
        os.chdir(original_working_directory)
        logging.info("恢复工作目录")


def handle_track(track, track_type):
    output = f"{track_type}\n"
    attributes = TRACK_ATTRIBUTES[track_type]

    for key, label in attributes:
        value = track[key][0] if isinstance(track.get(key), list) else track.get(key)
        if value is not None:
            output += f"{label:36}: {value}\n"

    output += "\n" + "-" * 50 + "\n\n"
    return output
