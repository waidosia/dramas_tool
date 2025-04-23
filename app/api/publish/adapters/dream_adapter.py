from app.models.configuration import Site
from app.models.publish import Publish
from .base import SiteAdapter

class DreamAdapter(SiteAdapter):
    def __init__(self, config,proxies):
        super().__init__(config,proxies=proxies)
        self.url = 'https://zmpt.cc'
        self.headers.update({
            'Referer': f'{self.url}/index.php',
        })
        self.type = '427'
        self.xpath = '//*[@id="content"]/text()'

        self.resolution_map = {
            '480P': '7',
            '720P': '8',
            '1080P': '1',
            '2160P': '5',
            '4K': '5',
        }
        self.team_map = {
            'GodDramas': '10',
        }

        self.medium_map = {
            'WEB-DL': '10'
        }


    def build_description(self, publish):
        links = [publish.screenshot1_link, publish.screenshot2_link, publish.screenshot3_link,
                     publish.screenshot4_link, publish.screenshot5_link]
        return f"""{self.reference}
[img]{publish.cover}[/img]
[img]{self.groupIcon}[/img]
{publish.publish_info}
[img]{self.videoInfoIcon}[/img]
[quote]{publish.mediaInfo}[/quote]
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
        return main_title

    def build_upload_data(self, publish):
        return {
            'name': self.format_main_title(publish.main_title, publish.mediaInfo),
            'small_descr': publish.sub_title,
            # 类型 短剧
            'type': self.type,
            # 媒介 web_dl
            'medium_sel[4]': self.medium_map.get(publish.film_source,'10'),
            # 分辨率
            'standard_sel[4]': self.resolution_map.get(publish.resolution, '0'),
            # 制作组
            'team_sel[4]': self.team_map.get(publish.team, '10'),
            # 标签 紧转 国语 中字 完结 驻站 冰种
            'tags[4][]': [1,17, 5, 6, 13, 12],
            # 匿名发布
            'uplver': 'yes',

        }
