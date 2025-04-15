from flask_sqlalchemy import SQLAlchemy

from utils.logs import log_config

db = SQLAlchemy()

# 初始化拓展
def config_extensions(app):
    db.init_app(app)
    log_config()
