from threading import Thread
from flask import Blueprint, request

from app.api.publish.adapters.agsvpt_adapter import AgsvptAdapter
from app.api.publish.adapters.dream_adapter import DreamAdapter
from app.api.publish.adapters.kylin_adapter import KylinAdapter
from app.api.publish.adapters.leaves_adapter import LeavesAdapter
from app.api.publish.adapters.pter_adapter import PterAdapter
from app.api.publish.adapters.tju_adapter import TjuAdapter
from app.api.publish.downloader.qb_downloader import QbDownloader
from app.api.publish.downloader.tr_downloader import TrDownloader
from app.extension import db
from app.models.configuration import Site, Config, Downloader
from app.models.publish import Publish, PublishForDownloader
from utils import util
from utils.logs import logger
import traceback

publish_downloader_api = Blueprint('publish_downloader_api', __name__)

SITE_ADAPTERS = {
    1: TjuAdapter, 2: AgsvptAdapter, 3: PterAdapter,
    4: LeavesAdapter, 5: KylinAdapter, 6: DreamAdapter
}

@publish_downloader_api.route('', methods=['POST'])
def upload_downloader():
    data = request.get_json()
    publish = Publish.query.get(data['publish_id'])
    site = Site.query.filter_by(type=data['site_type']).first()

    if not site:
        return util.json_server_error("未配置cookie，无法做种")

    config = Config.query.get(1)
    if not config:
        return util.json_params_error("查询发种配置失败")

    record = PublishForDownloader.query.filter_by(
        publish_id=data['publish_id'], site_type=data['site_type']
    ).first()

    if not record:
        record = PublishForDownloader(
            publish_id=data['publish_id'],
            site_type=data['site_type'],
            downloader_id=config.downloader_id,
            status=2
        )
        db.session.add(record)
        db.session.commit()
    else:
        logger.info("该记录已存在，不重复插入")

    Thread(target=seeding, args=(publish.id, site.id, data['torrent_id'], record.id)).start()
    return util.json_success("任务开始执行", "200")


@publish_downloader_api.route('batch', methods=['POST'])
def batch():
    data = request.get_json()
    publish = Publish.query.get(data['publish_id'])

    config = Config.query.get(1)
    if not config:
        return util.json_params_error("查询发种配置失败")

    for ss in data['sites']:
        site = Site.query.filter_by(type=ss['site_type']).first()

        if not site:
            return util.json_server_error("未配置cookie，无法做种")
        record = PublishForDownloader.query.filter_by(
            publish_id=data['publish_id'], site_type=ss['site_type']
        ).first()

        if not record:
            record = PublishForDownloader(
                publish_id=data['publish_id'],
                site_type=ss['site_type'],
                downloader_id=config.downloader_id,
                status=2
            )
            db.session.add(record)
            db.session.commit()
        else:
            logger.info("该记录已存在，不重复插入")
        Thread(target=seeding, args=(publish.id, site.id, ss['torrent_id'], record.id)).start()
    return util.json_success("任务开始执行", "200")




def get_downloader_client(downloader_cfg):
    if downloader_cfg.type == 1:
        return QbDownloader(downloader_cfg.url, downloader_cfg.user, downloader_cfg.password)
    elif downloader_cfg.type == 2:
        return TrDownloader(downloader_cfg.url, downloader_cfg.user, downloader_cfg.password)
    return None


def get_site_adapter(site, proxies):
    adapter_cls = SITE_ADAPTERS.get(site.type)
    return adapter_cls(site, proxies) if adapter_cls else None


def seeding(publish_id, site_id, torrent_id, record_id):
    from app import create_app  # 延迟导入避免循环依赖
    app = create_app()
    with app.app_context():
        try:
            publish = Publish.query.get(publish_id)
            site = Site.query.get(site_id)
            config = Config.query.get(1)
            downloader_cfg = Downloader.query.get(config.downloader_id)

            if not all([publish, site, config, downloader_cfg]):
                raise ValueError("获取数据库对象失败")

            downloader_client = get_downloader_client(downloader_cfg)
            if not downloader_client:
                raise ValueError("未知的下载器类型")

            ok,msg = downloader_client.login()
            if not ok:
                raise ValueError("下载器登录失败")

            proxies = {'http': config.proxy_url, 'https': config.proxy_url}
            adapter = get_site_adapter(site, proxies)
            if not adapter:
                raise ValueError("未识别的站点类型")

            ok, text = adapter.get_torrent_detail_page(f'{adapter.url}/details.php?id={torrent_id}', adapter.headers)
            if not ok:
                raise ValueError("获取种子详情页失败")

            ok, download_link = adapter.parse(text, adapter.xpath)
            if not ok:
                raise ValueError("解析种子下载链接失败")

            if adapter.url not in download_link:
                download_link = f'{adapter.url}{download_link}'


            ok, msg, torrent_hash = downloader_client.add_torrent_url(download_link, downloader_cfg.seeding_path)
            if not ok:
                logger.warning('在线添加失败，尝试下载种子')
                ok, path = adapter.get_torrent_file(download_link, config.torrent_path, adapter.headers)
                if not ok:
                    raise ValueError("种子下载失败，无法通过文件添加")
                ok, msg, torrent_hash = downloader_client.add_torrent_file(path, downloader_cfg.seeding_path)
                if not ok:
                    raise ValueError("种子文件添加失败")

            update_publish_record(record_id, 1, '做种成功', torrent_hash)
        except Exception as e:
            logger.error(f"发种任务异常：{e}\n{traceback.format_exc()}")
            update_publish_record(record_id, 0, str(e), '')


def update_publish_record(record_id, status, msg, torrent_hash):
    record = PublishForDownloader.query.get(record_id)
    if record:
        record.status = status
        record.error_msg = msg
        record.torrent_hash = torrent_hash
        db.session.commit()
