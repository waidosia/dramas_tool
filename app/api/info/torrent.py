from flask import Blueprint, request

from app.models.configuration import Config
from app.services.torrent import create_torrent
from utils import util

torrent_api = Blueprint('torrent', __name__)

torrent_api.route("",methods=['POST'])
def torrent():
    # 生成一个torrent对象
    data = request.json
    # 根据豆瓣地址生成ptgen
    configuration = Config.query.get(1)
    if configuration is None:
        return util.json_params_error("查询发布配置失败，联系管理员吧")
    path = create_torrent(data['folder_path'],'./temp/torrent')
    return util.json_success("成功",path)

