# 获取主标题，副标题，以及重命名文件夹
from flask import Blueprint, request

from app.services.rename import standard_name
from utils import util

rename_api = Blueprint('rename_api', __name__)

@rename_api.route('',methods=['POST'])
def rename():
    # 接收参数，获取主标题等
    data = request.json
    if data is None:
        return util.json_params_error("参数错误")
    res = standard_name(data['videoFolder'],data['cnName'],data['enName'],data['year'],
                  data['season'],data['category'],data['source'],data['filmSource'],data['team'])
    if res is None:
        return util.json_server_error("服务器错误")
    print(res)
    return util.json_success("成功",res)






