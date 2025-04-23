import re
import socket
from abc import ABC, abstractmethod
from utils.logs import logger


class BaseDownloader(ABC):
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.client = None

        # 解析 host 和 port
        match = re.match(r"(?:http[s]?://)?([^:/]+)(?::(\d+))", host)
        if match:
            self.hostname = match.group(1)
            self.port = int(match.group(2) or 80)
        else:
            raise ValueError(f"无法解析地址 {host}")

    def test_connection(self) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((self.hostname, self.port))
            s.shutdown(2)
            s.close()
            logger.info(f"{self.host} 地址通")
            return True
        except Exception as e:
            logger.error(f"无法连接到 {self.host}, 错误信息: {e}")
            return False

    @abstractmethod
    def login(self) -> (bool, str):
        pass

    @abstractmethod
    def add_torrent_url(self, torrent_urls: list, path: str) -> (bool, str):
        pass

    @abstractmethod
    def add_torrent_file(self, torrent_paths: list, path: str) -> (bool, str):
        pass

    @abstractmethod
    def logot(self):
        pass
