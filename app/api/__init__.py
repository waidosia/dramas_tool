from app.api.info import info_api
from app.api.info import downloader_api
from app.api.info import img_host_api
from app.api.info import pt_gen_api
from app.api.info import screenshot_api
from app.api.info import site_api
from app.api.publish import rename_api
from app.api.upload import upload_api
DEFAULT_BLUEPRINT = [
    (info_api, '/api/info'),
    (downloader_api, '/api/downloader'),
    (img_host_api, '/api/img'),
    (pt_gen_api, '/api/ptgen'),
    (screenshot_api, '/api/screenshot'),
    (site_api, '/api/site'),
    (upload_api, '/api/upload'),
    (rename_api, '/api/rename'),

]

def config_blueprint(app):
    for blueprint, prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blueprint, url_prefix=prefix)