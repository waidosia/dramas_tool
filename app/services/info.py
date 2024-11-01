import os


# 获取指定目录下的所有目录
def get_all_dir(path) -> (int,list[dict[str, str]]):
    """
     获取指定目录下的所有文件夹，包括子文件夹
    :param path: 指定的目录。配置文件中指定
    :return:
    :rtype: tuple[int,list[dict[str, str]]] int 为错误码，字典实例，包含文件夹名称与文件夹绝对路径
    """
    # 判断path是否存在，不存在，则返回err
    if not os.path.isdir(path):
        return 1,[]

    folders = []
    # 递归遍历 root_dir
    for dir_path, dir_names, filenames in os.walk(path):
        for dirname in dir_names:
            folder_path = os.path.join(dir_path, dirname)
            # 添加文件夹名称和绝对路径到结果列表
            folders.append({
                'name': dirname,
                'path': folder_path
            })
    return 0,folders
