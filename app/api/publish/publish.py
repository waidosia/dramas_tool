from flask import Blueprint, request

import utils.util
from utils import util

publish_api = Blueprint('publish_api', __name__)

@publish_api.route('/', methods=['POST'])
def publish():
    data = request.json
    if data is None:
        return util.json_params_error("信息缺失")
    print(data)
    return util.json_success("成功")