from flask import request, Blueprint
from app.extension import db
from app.models.configuration import Site
from utils import util

site_api = Blueprint('site', __name__)

@site_api.route("",methods=['GET'])
def get_site():
    all_sites = Site.query.all()
    all_sites_dict = [site.to_dict() for site in all_sites]
    return util.json_success("成功", all_sites_dict)

@site_api.route("",methods=['POST'])
def add_site():
    data = request.get_json()
    site = Site(**data)
    try:
        db.session.add(site)
        db.session.commit()
    except Exception as e:
        # 如果是唯一索引冲突引发的异常
        if "UNIQUE constraint" in str(e):
            return util.json_params_error("该站点已存在.")
        else:
            return util.json_server_error("未知错误")
    return util.json_success("成功", site.to_dict())



@site_api.route("/<int:site_id>",methods=['PUT'])
def update_site(site_id):
    data = request.get_json()
    site = Site.query.get(site_id)
    if site is None:
        return util.json_params_error("ID不存在")
    for key, value in data.items():
        if hasattr(site, key):
            setattr(site, key, value)

    db.session.commit()
    return util.json_success("成功", site.to_dict())

@site_api.route("/<int:site_id>",methods=['DELETE'])
def delete_site(site_id):
    site = Site.query.get(site_id)
    if site is None:
        return util.json_params_error("ID不存在")
    db.session.delete(site)
    db.session.commit()
    return util.json_success("成功", None)
