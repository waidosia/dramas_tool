import asyncio
from datetime import datetime

from flask import Blueprint, request

import utils.util
from app.extension import db
from app.models.publish import Publish
from app.services.media import get_media_info
from app.services.rename import standard_name
from app.services.torrent import create_torrent
from utils import util

publish_api = Blueprint('publish_api', __name__)

@publish_api.route('', methods=['POST'])
async def publish():
    data = request.json
    if data is None:
        return util.json_params_error("信息缺失")
    # 存放数据
    # 处理年份
    year = datetime.fromisoformat(data['year']).year
    # pub = Publish(
    # cn_name=data['cnName'],
    # en_name = data['enName'],
    # year =  year,
    # season = data['season'],
    # film_source =  data['filmSource'],
    # source = data['source'],
    # team =  data['team'],
    # cover=   data['cover'],
    # pt_gen=  data['ptGen'],
    # introduction = data['introduction'],
    # category = ','.join(data['category']),
    # )

    # db.session.add(pub)
    # db.session.commit()

    # 重命名(同步任务)
    res = standard_name(data['videoFolder'], data['cnName'], data['enName'], data['year'],
                        data['season'], data['category'], data['source'], data['filmSource'], data['team'])

    tasks_list = [
        asyncio.create_task(torrent(data['videoFolder'])),
        asyncio.create_task(media(res['firstFileName'])),
        ]
    await asyncio.gather(*tasks_list)
    return util.json_success("成功")

async def torrent(videoFolder):
    print(create_torrent(videoFolder, "temp/torrent"))


async def media(firstFileName):
    print(get_media_info(firstFileName))