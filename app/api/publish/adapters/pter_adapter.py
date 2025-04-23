import re

from utils.logs import logger
from .base import SiteAdapter

class PterAdapter(SiteAdapter):
    def __init__(self, config,proxies):
        super().__init__(config,proxies=proxies)
        self.url = 'https://pterclub.com'
        self.headers.update({
        'Host': 'pterclub.com',
        'Referer': 'https://pterclub.com/upload.php',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Origin': 'https://pterclub.com',

    })
        self.type = '404'
        self.xpath = '//a[@class="faqlink"]/@href'

        self.medium_map = {
            'WEB-DL': '5'
        }

        self.region_map = {
            'china': '1'
        }

    def build_description(self, publish):
        links = [publish.screenshot1_link, publish.screenshot2_link, publish.screenshot3_link,
                     publish.screenshot4_link, publish.screenshot5_link]
        return f"""{self.reference}
[img]{publish.cover}[/img]
[img]{self.groupIcon}[/img]
{publish.publish_info}
[img]{self.videoInfoIcon}[/img]
[hide=MediaInfo]{publish.mediaInfo}[/hide]
[img]{self.screenshotIcon}[/img]
{''.join(f"[img]{link}[/img]" for link in links if link)}
[img]{publish.video_screenshot_link}[/img]"""

    def format_main_title(self, title: str, media_info: str) -> str:
        main_title = title.replace('.', ' ')
        main_title = (main_title
                      .replace('H264', 'h.264')
                      .replace('H265', 'h.265')
                      .replace('H 264', 'h.264')
                      .replace('H 265', 'h.265')
                      )
        writing_library = re.search(r'Writing.*library.*:(.*)',
                                    media_info)
        if writing_library:
            if 'x264' in writing_library.group(1):
                logger.info("Writing library中存在x264")
                main_title = main_title.replace('H.264', 'x264')
            if 'x265' in writing_library.group(1):
                logger.info("Writing library中存在x265")
                main_title = main_title.replace('H.265', 'x265')
        return main_title

    def build_upload_data(self, publish):
        return {
            'name': self.format_main_title(publish.main_title, publish.mediaInfo),
            'small_descr': publish.sub_title,
            # 类型 电视剧
            'type': self.type,
            # 媒介 web_dl
            'source_sel': self.medium_map.get(publish.film_source,'5'),
            # 地区 大陆
            'team_sel': self.region_map.get('china','1'),
            # 国语
            'guoyu': 'yes',
            # 中字
            'zhongzi': 'yes',
            # 匿名
            'uplver': 'yes',
            # 禁转
            'jinzhuan': 'yes',
        }
