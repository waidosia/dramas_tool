import abc
import os
import time
from urllib.parse import unquote

import requests
from lxml import etree

from app.models.publish import Publish
from utils.logs import logger


class SiteAdapter:
    def __init__(self, config,proxies):
        self.config = config  # Site 配置
        self.proxies = proxies if config.is_proxy else None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36',
            'Cookie': config.cookie,
        }
        self.url = config.url
        self.reference = '[quote][size=4]因组内调整，之后新发布，均禁止[color=Red]转载 [color=Black]谢谢！！[/size][/quote]'
        self.groupIcon = 'https://img.pterclub.com/images/2024/01/10/GodDramas-.png'
        self.videoInfoIcon = 'https://img.pterclub.com/images/2024/01/10/49401952f8353abd4246023bff8de2cc.png'
        self.screenshotIcon = 'https://img.pterclub.com/images/2024/01/10/3a3a0f41d507ffa05df76996a1ed69e7.png'


    def _build_headers(self, extra_headers: dict = None) -> dict:
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _make_request(self, url: str, headers: dict, allow_redirects=True) -> requests.Response:
        return requests.get(url, headers=headers, timeout=10, allow_redirects=allow_redirects, proxies=self.proxies)

    def _make_post_request(self, url: str, extra_headers: dict, data: dict, files: any, allow_redirects=True) -> requests.Response:
        headers = self._build_headers(extra_headers)
        return requests.post(url, headers=headers, data=data, files=files,timeout=10, allow_redirects=allow_redirects, proxies=self.proxies)

    def get_homepage(self, url: str, extra_headers: dict = None) -> (bool, str):
        headers = self._build_headers(extra_headers)
        try:
            logger.info(f'开始获取 {self.config.name} 主页')
            response = self._make_request(url, headers, allow_redirects=False)

            if response.status_code == 200:
                logger.info(f'获取 {self.config.name} 主页成功')
                return True, response.text
            elif response.status_code == 302:
                location = response.headers.get('Location', '')
                if 'login.php' in location:
                    logger.info(f'{self.config.name} cookie过期')
                    return False, 'cookie过期'
                else:
                    logger.warning(f'重定向到: {location}')
                    return False, f'重定向到: {location}'
            else:
                logger.error(f'主页请求失败, 状态码: {response.status_code}')
                return False, f'状态码: {response.status_code}'
        except Exception as e:
            logger.exception(f'请求 {self.config.name} 主页失败: {e}')
            return False, '请求失败'

    def get_torrent_detail_page(self, url: str, extra_headers: dict = None) -> (bool, any):
        headers = self._build_headers(extra_headers)
        try:
            response = self._make_request(url, headers)
            if response.status_code == 200:
                text = response.text
                return True, text
            else:
                logger.error(f'详情页请求失败, 状态码: {response.status_code}')
                return False, f'状态码: {response.status_code}'
        except Exception as e:
            logger.exception(f'详情页请求失败: {e}')
            return False, '请求失败'

    def get_torrent_file(self, url: str, save_dir: str, extra_headers: dict = None) -> (bool, str):
        headers = self._build_headers(extra_headers)
        try:
            response = self._make_request(url, headers)
            if response.status_code == 200:
                content_disp = response.headers.get('Content-Disposition', '')
                if 'filename=' not in content_disp:
                    return False, '未包含文件名'

                filename = content_disp.split('filename=')[1].split(';')[0].replace('"', '')
                decoded_filename = filename.encode('latin-1').decode('utf-8')
                decoded_filename = unquote(decoded_filename)
                save_path = os.path.join(save_dir, decoded_filename)

                with open(save_path, 'wb') as f:
                    f.write(response.content)

                logger.info(f'下载种子成功: {decoded_filename}')
                return True, save_path
            else:
                logger.error(f'下载种子失败, 状态码: {response.status_code}')
                return False, f'状态码: {response.status_code}'
        except Exception as e:
            logger.exception(f'下载种子异常: {e}')
            return False, '下载失败'

    def publish(self, publish: Publish):
        """发布种子，子类实现发布逻辑"""
        logger.info(f"开始发布到站点：{self.config.name}")
        data = self.build_upload_data(publish)
        data['descr'] = self.build_description(publish)

        filename = os.path.basename(publish.torrent_path)
        files = {'file': (filename, publish.torrent, 'application/x-bittorrent')}

        upload_url = f"{self.url}/takeupload.php"

        response = self._make_post_request(upload_url, self.headers, data=data, files=files, allow_redirects=False)
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            torrent_id = redirect_url.split('id=')[1].split('&')[0]
            time.sleep(1)
            return True, torrent_id
        else:
            return False, None

    def parse(self, html: str,path: str) -> (bool, str):
        tree = etree.HTML(html)
        result = tree.xpath(path)
        if result:
            url = result[0]
            url = url.replace("\n", "").replace("\r", "").strip()
            logger.info(f'{self.config.name}种子下载地址成功: {result}')
            return True, url
        else:
            logger.info(f'{self.config.name}种子下载地址失败')
            return False, f'{self.config.name}种子下载地址失败'



    @abc.abstractmethod
    def build_description(self, publish):
        pass

    @abc.abstractmethod
    def build_upload_data(self, publish):
        pass

    @abc.abstractmethod
    def format_main_title(self, title: str, media_info: str) -> str:
        pass

