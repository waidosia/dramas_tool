from .base import SiteAdapter

class LeavesAdapter(SiteAdapter):
    def __init__(self, config,proxies):
        super().__init__(config,proxies=proxies)
        self.url = 'https://leaves.red'
        self.headers.update({
        'Host': 'leaves.red',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })

        self.type = '439'
        self.xpath = '//a[@title="可在BT客户端使用，当天有效。"]/@href'

        self.resolution_map = {
            '720P': '3',
            '1080P': '1',
            '2160P': '5',
            '4K': '5',
        }

        self.video_codec_map = {
            'H.264': '1',
            'H.265': '10',
        }

        self.team_map = {
            'GodDramas': '29',
        }

        self.medium_map = {
            'WEB-DL': '8'
        }

        self.audiocodec_map = {
            'AAC': '6',
        }

        self.region_map = {
            'china': '2'
        }

    def build_description(self, publish):
        links = [publish.screenshot1_link, publish.screenshot2_link, publish.screenshot3_link,
                     publish.screenshot4_link, publish.screenshot5_link]
        return f"""{self.reference}
[img]{publish.cover}[/img]
[img]{self.groupIcon}[/img]
{publish.publish_info}
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
            # media_info信息
            'technical_info': publish.mediaInfo,
            # 类型 短剧
            'type': self.type,
            # 媒介 web_dl
            'medium_sel[5]':self.medium_map.get(publish.film_source,'8'),
            # 视频编码 h.264
            'codec_sel[5]': self.video_codec_map.get(publish.video_codec, '1'),
            # 音频编码 aac
            'audiocodec_sel[5]': self.audiocodec_map.get(publish.audio_codec, '6'),
            # 分辨率
            'standard_sel[5]': self.resolution_map.get(publish.resolution, '1'),
            # 地区 中国
            'processing_sel[5]': self.region_map.get('china', '2'),
            # 制作组
            'team_sel[5]': self.team_map.get(publish.team, '29'),
            # 标签
            'tags[5][]': [1,3, 5, 6, 28],
            # 匿名发布
            'uplver': 'yes',
        }

