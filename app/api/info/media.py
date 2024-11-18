from flask import Blueprint, request

from app.services.media import get_media_info
from utils import util

media_api = Blueprint('media', __name__)

@media_api.route("",methods=['POST'])
def get_media():
    data = request.json
    media = get_media_info(data['firstFileName'])
    if media != '':
        return util.json_success("成功",media)
    else:
        return util.json_server_error("服务器错误")


