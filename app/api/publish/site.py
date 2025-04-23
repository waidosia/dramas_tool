from flask import request, Blueprint
from threading import Thread

from app.api.publish.adapters.agsvpt_adapter import AgsvptAdapter
from app.api.publish.adapters.dream_adapter import DreamAdapter
from app.api.publish.adapters.kylin_adapter import KylinAdapter
from app.api.publish.adapters.leaves_adapter import LeavesAdapter
from app.api.publish.adapters.pter_adapter import PterAdapter
from app.api.publish.adapters.tju_adapter import TjuAdapter
from app.extension import db
from app.models.configuration import Site, Config
from app.models.publish import Publish, PublishForSite
from utils import util
from utils.logs import logger

publish_site_api = Blueprint('publish_site_api', __name__)


def get_adapter(site, proxies):
    adapter_map = {
        1: TjuAdapter,
        2: AgsvptAdapter,
        3: PterAdapter,
        4: LeavesAdapter,
        5: KylinAdapter,
        6: DreamAdapter
    }
    adapter_cls = adapter_map.get(site.type)
    return adapter_cls(site, proxies) if adapter_cls else None


def update_publish_record(record_id, status, msg, torrent_id):
    record = PublishForSite.query.get(record_id)
    if record:
        record.status = status
        record.error_msg = msg
        record.torrent_id = torrent_id
        db.session.commit()


def start_publish_thread(publish_id, site_id, record_id):
    thread = Thread(target=upload, args=(publish_id, site_id, record_id))
    thread.start()



@publish_site_api.route('', methods=['POST'])
def upload_site():
    data = request.get_json()
    publish = Publish.query.get(data['publish_id'])
    site = Site.query.filter_by(type=data['site_type']).first()

    if not site:
        return util.json_server_error("未配置cookie,无法发种")

    config = Config.query.get(1)
    if not config:
        return util.json_params_error("查询发种配置失败")

    publish_for_site = PublishForSite.query.filter_by(
        publish_id=publish.id,
        site_type=site.type
    ).first()

    if not publish_for_site:
        publish_for_site = PublishForSite(
            publish_id=publish.id,
            site_type=site.type,
            status=2
        )
        db.session.add(publish_for_site)
        db.session.commit()
    else:
        logger.info(f"记录已存在，跳过插入：publish_id={publish.id}, site_type={site.type}")

    start_publish_thread(publish.id, site.id, publish_for_site.id)

    return util.json_success("任务开始执行", "200")


@publish_site_api.route('/batch', methods=['POST'])
def upload_sites_batch():
    data = request.get_json()
    publish_id = data.get('publish_id')
    site_types = data.get('site_types', [])

    publish = Publish.query.get(publish_id)
    if not publish:
        return util.json_params_error("找不到指定的发布记录")

    config = Config.query.get(1)
    if not config:
        return util.json_params_error("查询发种配置失败")

    for site_type in site_types:
        site = Site.query.filter_by(type=site_type).first()
        if not site:
            logger.warning(f"站点类型 {site_type} 未配置，跳过")
            continue

        publish_for_site = PublishForSite.query.filter_by(
            publish_id=publish_id,
            site_type=site_type
        ).first()

        if not publish_for_site:
            publish_for_site = PublishForSite(
                publish_id=publish_id,
                site_type=site_type,
                status=2
            )
            db.session.add(publish_for_site)
            db.session.commit()
        else:
            logger.info(f"站点 {site_type} 记录已存在，跳过")

        start_publish_thread(publish.id, site.id, publish_for_site.id)

    return util.json_success("任务已启动执行", "200")



def upload(publish_id: int, site_id: int, record_id: int):
    from app import create_app
    app = create_app()

    with app.app_context():
        try:
            publish = Publish.query.get(publish_id)
            site = Site.query.get(site_id)
            config = Config.query.get(1)

            if not all([publish, site, config]):
                logger.error("缺少必要数据库对象")
                update_publish_record(record_id, 0, '获取数据库对象失败', 0)
                return

            proxies = {'http': config.proxy_url, 'https': config.proxy_url}
            pt_adapter = get_adapter(site, proxies)

            if not pt_adapter:
                update_publish_record(record_id, 0, '未识别的站点类型', 0)
                return

            ok, msg = pt_adapter.get_homepage(f"{pt_adapter.url}/index.php", pt_adapter.headers)
            if not ok:
                update_publish_record(record_id, 0, '主页获取失败，可能是网络或 cookie 过期', 0)
                return

            ok, torrent_id = pt_adapter.publish(publish)
            if not ok:
                update_publish_record(record_id, 0, '发布失败', 0)
                return

            update_publish_record(record_id, 1, '', torrent_id)

        except Exception as e:
            logger.exception("发种任务发生异常")
            update_publish_record(record_id, 0, str(e), 0)
