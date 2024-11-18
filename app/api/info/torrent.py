
from flask import Blueprint, request

from app.models.configuration import Config
from app.services.torrent import create_torrent
from utils import util

torrent_api = Blueprint('torrent', __name__)

@torrent_api.route("",methods=['POST'])
def torrent():
    # 生成一个torrent对象
    data = request.json
    path = create_torrent(data['videoFolder'],"temp/torrent")
    return util.json_success("成功",path)

