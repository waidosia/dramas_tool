import requests
from flask import Blueprint, request

from app.models.configuration import Config, ImageHost
from app.services.upload import upload_screenshot
from utils import util
from utils.util import json_success, json_server_error

upload_api = Blueprint('upload', __name__)

@upload_api.route('', methods=['POST'])
def upload():
    file = request.files['file']
    if file is None:
        return util.json_params_error("未找到文件")
    # 查询发布配置中,启用的图床与代理
    configuration = Config.query.get(1)
    if configuration is None:
        return util.json_params_error("查询发布配置失败，联系管理员吧")
    img_host = ImageHost.query.get(configuration.image_host_id)
    if img_host is None or not img_host.is_available:
        return util.json_params_error("找不到指定的图床或图床不可用，联系管理员吧")

    success,res = upload_screenshot(img_host, file.read(),configuration.proxy_url)
    if success:
        return json_success("成功",res)
    else:
        return json_server_error("服务器内部错误")

@upload_api.route('/link', methods=['POST'])
def upload_link():
    # 取data中的数据
    data = request.json
    if data is None:
        return util.json_params_error("未获取到文件")

    # 请求，拿到在线图片的字节流
    res = requests.get(data['url'])
    if res.status_code == 200:
        content = res.content
    else:
        return util.json_params_error("在线图片链接不可访问")
    # 查询发布配置中,启用的图床与代理
    configuration = Config.query.get(1)
    if configuration is None:
        return util.json_params_error("查询发布配置失败，联系管理员吧")
    img_host = ImageHost.query.get(configuration.image_host_id)
    if img_host is None or not img_host.is_available:
        return util.json_params_error("找不到指定的图床或图床不可用，联系管理员吧")

    success,res = upload_screenshot(img_host, content,configuration.proxy_url)
    if success:
        return json_success("成功",res)
    else:
        return json_server_error("服务器内部错误")

