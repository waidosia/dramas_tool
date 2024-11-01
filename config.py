import os
import yaml

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def load_yaml_config():
    config_file = os.path.join(BASE_DIR, 'configs/app.yaml')
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

class Config:
    # 加载 YAML 配置文件
    yaml_config = load_yaml_config()

    # Flask应用基础配置
    DEBUG = yaml_config['app']['debug']
    HOST = yaml_config['app']['host']
    PORT = yaml_config['app']['port']

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = yaml_config['database']['uri']
    SQLALCHEMY_TRACK_MODIFICATIONS = yaml_config['database']['track_modifications']
    SQLALCHEMY_COMMIT_ON_TEARDOWN = yaml_config['database']['commit_on_teardown']

    # 工具自身配置
    PATH = yaml_config['setting']['path']

