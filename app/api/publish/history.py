import flask
from flask import request


from app.models.publish import Publish
from utils import util

history_api = flask.Blueprint('history_api', __name__)

@history_api.route('/', methods=['GET'])
def get_publish_history():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    query = Publish.query.paginate(page=page, per_page=size)
    data = [
        item.to_dict() for item in query.items
    ]
    return util.json_success("成功",{
        'data': data,
        'total': query.total
    })
