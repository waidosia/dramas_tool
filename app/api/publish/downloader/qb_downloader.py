import time

from qbittorrentapi import Client
from qbittorrentapi import LoginFailed

from utils.logs import logger
from .base import BaseDownloader


class QbDownloader(BaseDownloader):
    def login(self) -> (bool, str):
        try:
            self.client = Client(host=self.host, username=self.username, password=self.password)
            self.client.auth_log_in()
            logger.info(f"qbittorrent版本号：{self.client.app.version}")
            return True, "登录成功"
        except LoginFailed:
            return False, "登陆失败, 请检查地址或账号密码"
        except Exception as e:
            return False, f"登陆失败, 错误信息: {e}"

    def logot(self):
        self.client.auth_log_out()

    def add_torrent_url(self, torrent_url, path) -> (bool, str):
        res = self.client.torrents_add(urls=torrent_url, is_paused=True, savepath=path, is_skip_checking=True)
        if res != 'Ok.':
            logger.error(f'{torrent_url} 添加失败')
            return False, f'{torrent_url} 添加失败', None

        time.sleep(5)  # 等待 qbittorrent 写入
        torrents = self.client.torrents_info()
        if torrents:
            latest = sorted(torrents, key=lambda x: x['added_on'], reverse=True)[0]
            return True, "链接添加成功", latest['hash']
        return False, "未能获取hash", None


    def add_torrent_file(self, torrent_path, path) -> (bool, str):
        res = self.client.torrents_add(torrent_files=torrent_path, is_paused=True, savepath=path, is_skip_checking=True)
        if res != 'Ok.':
            logger.error(f'{torrent_path} 添加失败')
            return False, f'{torrent_path} 添加失败', None

        time.sleep(1)
        torrents = self.client.torrents_info()
        if torrents:
            latest = sorted(torrents, key=lambda x: x['added_on'], reverse=True)[0]
            return True, "文件添加成功", latest['hash']

        return False, "未能获取hash", None
