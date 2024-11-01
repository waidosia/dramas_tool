from flask import request, Blueprint
from app.extension import db
from app.models.configuration import Downloader
from utils import util

downloader_api = Blueprint('downloader', __name__)


@downloader_api.route("/<int:downloader_id>",methods=['GET'])
def get_downloader(downloader_id):
    downloader = Downloader.query.get(downloader_id)
    if downloader is None:
        return util.json_params_error("ID不存在")
    return util.json_success("成功", downloader.to_dict())


@downloader_api.route("",methods=['GET'])
def get_downloader_all():
    all_downloaders = Downloader.query.all()
    all_downloaders_dict = [downloader.to_dict() for downloader in all_downloaders]
    return util.json_success("成功", all_downloaders_dict)

@downloader_api.route("",methods=['POST'])
def add_downloader():
    data = request.get_json()
    downloader = Downloader(**data)
    db.session.add(downloader)
    db.session.commit()

    return util.json_success("成功", downloader.to_dict())


@downloader_api.route("/<int:downloader_id>",methods=['PUT'])
def update_downloader(downloader_id):
    data = request.get_json()
    downloader = Downloader.query.get(downloader_id)
    if downloader is None:
        return util.json_params_error("ID不存在")
        # 遍历请求中的数据，动态设置属性
    for key, value in data.items():
        if hasattr(downloader, key):
            setattr(downloader, key, value)
    db.session.commit()
    return util.json_success("成功", downloader.to_dict())



@downloader_api.route("/<int:downloader_id>",methods=['DELETE'])
def delete_downloader(downloader_id):
    downloader = Downloader.query.get(downloader_id)
    if downloader is None:
        return util.json_params_error("ID不存在")
    db.session.delete(downloader)
    db.session.commit()
    return util.json_success("成功", None)
