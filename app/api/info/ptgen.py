from flask import request, Blueprint
from app.extension import db
from app.models.configuration import PtGen, Config
from app.services.ptgen import fetch_ptgen_data
from utils import util
from utils.util import json_success, json_server_error

pt_gen_api = Blueprint('ptgen', __name__)

@pt_gen_api.route("/<int:ptgen_id>",methods=['GET'])
def get_ptgen(ptgen_id):
    ptgen = PtGen.query.get(ptgen_id)
    if ptgen is None:
        return util.json_params_error("ID不存在")
    return util.json_success("成功", ptgen.to_dict())

@pt_gen_api.route("",methods=['GET'])
def get_ptgen_all():
    is_available = request.args.get('is_available', default=None, type=bool)
    if is_available is not None:
        ptgens = PtGen.query.filter_by( is_available=is_available).all()
    else:
        ptgens = PtGen.query.all()
    all_ptgens_dict = [ptgen.to_dict() for ptgen in ptgens]
    return util.json_success("成功", all_ptgens_dict)

@pt_gen_api.route("",methods=['POST'])
def add_ptgen():
    data = request.get_json()
    ptgen = PtGen(**data)
    db.session.add(ptgen)
    db.session.commit()
    return util.json_success("成功", ptgen.to_dict())

@pt_gen_api.route("/<int:ptgen_id>",methods=['PUT'])
def update_ptgen(ptgen_id):
    data = request.get_json()
    ptgen = PtGen.query.get(ptgen_id)
    if ptgen is None:
        return util.json_params_error("ID不存在")
    for key, value in data.items():
        if hasattr(ptgen, key):
            setattr(ptgen, key, value)
    db.session.commit()
    return util.json_success("成功", ptgen.to_dict())

@pt_gen_api.route("/<int:ptgen_id>",methods=['DELETE'])
def delete_ptgen(ptgen_id):
    ptgen = PtGen.query.get(ptgen_id)
    if ptgen is None:
        return util.json_params_error("ID不存在")
    db.session.delete(ptgen)
    db.session.commit()
    return util.json_success("成功", None)

@pt_gen_api.route("/send",methods=['POST'])
def send_ptgen():
    data = request.json
    # 根据豆瓣地址生成ptgen
    configuration = Config.query.get(1)
    if configuration is None:
        return util.json_params_error("查询发布配置失败，联系管理员吧")
    ptgen = PtGen.query.get(configuration.pt_gen_id)
    if ptgen is None or not ptgen.is_available:
        return util.json_params_error("找不到指定的PTGEN或PTGEN不可用，联系管理员吧")
    res = fetch_ptgen_data(ptgen.url,data['url'])
    if res['code'] == 200:
        return json_success("成功",res['data'])
    elif res['code'] == 400:
        return json_success("上传失败")
    else:
        return json_server_error("服务器内部错误")
