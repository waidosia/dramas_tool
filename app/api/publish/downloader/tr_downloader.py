from transmission_rpc import Client as trClient

from utils.logs import logger
from .base import BaseDownloader


class TrDownloader(BaseDownloader):
    def login(self) -> (bool, str):
        try:
            self.client = trClient(host=self.hostname, port=self.port, username=self.username, password=self.password)
            logger.info(f"Transmission版本号：{self.client.server_version}")
            return True, "登录成功"
        except Exception as e:
            return False, f"无法连接到 {self.host}, 错误信息: {e}"

    def logot(self):
        pass


    def add_torrent_url(self, torrent_url, path) -> (bool, str):
        try:
            res = self.client.add_torrent(torrent_url, download_dir=path)
        except Exception as e:
            logger.error(f'{torrent_url} 添加失败: {e}')
            return False,f'{torrent_url} 添加失败' , None
        return True, "链接添加成功",res.hashString

    def add_torrent_file(self, torrent_path, path) -> (bool, str):
        try:
            res = self.client.add_torrent(torrent_path, download_dir=path)
        except Exception as e:
            logger.error(f'{torrent_path} 添加失败: {e}')
            return False, f'{torrent_path} 添加失败', None
        return True, "文件添加成功",res.hashString
