from flask import request, Blueprint
from app.extension import db
from app.models.configuration import Screenshot
from utils import util

screenshot_api = Blueprint('screenshot', __name__)


@screenshot_api.route("",methods=['GET'])
def get_screenshot():
    all_screens = Screenshot.query.all()
    all_screen_dict = [screen.to_dict() for screen in all_screens]
    return util.json_success("成功", all_screen_dict)


@screenshot_api.route("/<int:screenshot_id>",methods=['PUT'])
def update_screenshot(screenshot_id):
    data = request.get_json()
    screen = Screenshot.query.get(screenshot_id)
    if screen is None:
        return util.json_params_error("更新失败，联系管理员吧")
    for key, value in data.items():
        if hasattr(screen, key):
            setattr(screen, key, value)
    db.session.commit()
    return util.json_success("成功", screen.to_dict())