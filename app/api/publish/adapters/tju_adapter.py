from .base import SiteAdapter

class TjuAdapter(SiteAdapter):
    def __init__(self, config,proxies):
        super().__init__(config,proxies=proxies)
        self.url = 'https://tjupt.org'
        self.headers.update({
        'Host': 'tjupt.org',
        'Referer': 'https://tjupt.org/upload.php',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    })
        self.type = '412'

        self.xpath = '//a[@id="direct_link"]/@href'

    def build_description(self, publish):
        links = [publish.screenshot1_link, publish.screenshot2_link, publish.screenshot3_link,
                     publish.screenshot4_link, publish.screenshot5_link]
        return f"""{self.reference}
        [img]{publish.cover}[/img]
[img]{self.groupIcon}[/img]
{publish.publish_info}
[img]{self.videoInfoIcon}[/img]
[mediainfo]{publish.mediaInfo}[/mediainfo]
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
            'referid': '',
            'type': self.type,
            'cname': publish.cn_name,
            'ename': self.format_main_title(publish.main_title, publish.mediaInfo),
            'district': '大陆',
            'small_descr': publish.sub_title,
            'uplver': 'yes',
            'internal_team': 'yes',
            'exclusive': 'yes',
        }
