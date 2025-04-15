import os.path

from flask import Blueprint, request, send_file

from utils import util

download_api = Blueprint('download', __name__)

@download_api.route('/', methods=['GET'])
def download_file():
    filepath = request.args.get('path')
    path = os.getcwd()
    filepath= os.path.join(path, filepath)
    print(filepath)
    try:
        return send_file(filepath, as_attachment=True)
    except PermissionError:
        return util.json_server_error('无权限')
    except Exception as e:
        print(e)
        return util.json_server_error('服务器错误')
