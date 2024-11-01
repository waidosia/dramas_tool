# 获取指定的图床信息
from flask import request, Blueprint

from app.extension import db
from app.models.configuration import ImageHost
from utils import util

img_host_api = Blueprint('img', __name__)

@img_host_api.route('/<int:img_host_id>',methods=['GET'])
def get_img_host(img_host_id):
    img_host = ImageHost.query.get(img_host_id)
    if img_host is None:
        return util.json_params_error("ID不存在")
    return util.json_success("成功",img_host.to_dict())

# 获取所有的图床信息
@img_host_api.route('',methods=['GET'])
def get_img_host_all():
    # 获取携带参数
    is_available = request.args.get('is_available', default=None, type=bool)
    if is_available is not None:
        all_hosts = ImageHost.query.filter_by(is_available=is_available).all()
    else:
        all_hosts = ImageHost.query.all()
    all_hosts_dict = [host.to_dict() for host in all_hosts]
    return util.json_success("成功",all_hosts_dict)

# 更新指定的图床信息
@img_host_api.route('/<int:img_host_id>', methods=['PUT'])
def update_img_host(img_host_id):
    data = request.get_json()
    img_host = ImageHost.query.get(img_host_id)

    if img_host is None:
        return util.json_params_error("ID不存在")

    # 遍历请求中的数据，动态设置属性
    for key, value in data.items():
        if hasattr(img_host, key):
            setattr(img_host, key, value)

    db.session.commit()

    return util.json_success("成功", img_host.to_dict())

