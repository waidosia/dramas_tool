import os
from torf import Torrent

def create_torrent(folder_path, torrent_path) -> str:
    if not os.path.exists(folder_path):
        return ''

    # 检查路径是否指向一个非空目录或一个文件
    if os.path.isdir(folder_path) and not os.listdir(folder_path):
        return ''

    # 构造完整的torrent文件路径
    torrent_file_name = os.path.basename(folder_path.rstrip("/\\")) + '.torrent'
    torrent_file_path = os.path.join(torrent_path, torrent_file_name)

    torrent_truth_path = os.path.join(os.getcwd(), torrent_file_name)

    # 确保torrent文件的目录存在
    os.makedirs(os.path.dirname(torrent_truth_path), exist_ok=True)

    # 如果目标 Torrent 文件已存在，则删除它
    if os.path.exists(torrent_truth_path):
        os.remove(torrent_truth_path)

    # 创建 Torrent 对象
    t = Torrent(path=folder_path, trackers=[''])

    # 生成和写入 Torrent 文件
    t.generate()
    t.write(torrent_truth_path)

    return str(torrent_file_path)
