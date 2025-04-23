import logging
import os

from flask import Blueprint, request

import app
from app.extension import db
from app.models.configuration import Config
from app.services.info import get_all_dir
from utils import util

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

info_api = Blueprint('info', __name__)


@info_api.route('/get_path')
def get_path():
    logging.debug("获取所有短剧目录")
    path = os.path.join(app.Config.PATH)
    is_exist,dir_map = get_all_dir(path)
    if not is_exist:
        # 文件夹不存在，返回错误
        logging.error("目录不存在，请检查配置文件")
        return util.json_server_error("文件夹不存在，请检查配置文件")
    else:
        return util.json_success("成功",dir_map)


@info_api.route("/",methods=['GET'])
def get_configuration():
    configuration = Config.query.get(1)
    if configuration is None:
        return util.json_params_error("查询失败，联系管理员吧")
    return util.json_success("成功", configuration.to_dict())


@info_api.route("/<int:config_id>",methods=['PUT'])
def update_configuration(config_id):
    data = request.get_json()
    configuration = Config.query.get(config_id)
    if configuration is None:
        return util.json_params_error("更新失败，联系管理员吧")
    for key, value in data.items():
        if hasattr(configuration, key):
            setattr(configuration, key, value)
    db.session.commit()
    return util.json_success("成功", configuration.to_dict())




