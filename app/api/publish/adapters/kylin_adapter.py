from .base import SiteAdapter

class KylinAdapter(SiteAdapter):
    def __init__(self, config,proxies):
        super().__init__(config,proxies=proxies)
        self.url = 'https://www.hdkyl.in'

        self.headers.update({
        'Host': 'www.hdkyl.in',
        'Referer': 'https://www.hdkyl.in/index.php',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
        self.type = '427'
        self.xpath = '//a[@title="可在BT客户端使用，当天有效。"]/@href'
        self.year_map = {
            '2022': '2',
            '2023': '1',
            '2024': '10'
        }

        self.resolution_map = {
            '480P': '8',
            '720P': '3',
            '1080P': '1',
            '2160P': '6',
            '4K': '6',
        }

        self.video_codec_map = {
            'H264': '1',
            'H265': '6',
        }

        self.team_map = {
            'GodDramas': '9',
        }

        self.medium_map = {
            'WEB-DL': '31'
        }

        self.audiocodec_map = {
            'AAC': '6',
        }

        self.region_map = {
            'china':'15'
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
        main_title = (main_title.replace('AVC', 'H264')
                      .replace('H 264', 'H264')
                      .replace('HEVC', 'H265')
                      .replace('H 265', 'H265')
                      )
        return main_title


    def build_upload_data(self, publish):
        return {
            'name': self.format_main_title(publish.main_title, publish.mediaInfo),
            'small_descr': publish.sub_title,
            'technical_info': publish.mediaInfo,
            # 类型 短剧
            'type': self.type,
            # 年代
            'processing_sel[4]': self.year_map.get(publish.year, '0'),
            # 媒介 web_dl
            'medium_sel[4]': self.medium_map.get(publish.film_source, '31'),
            # 视频编码 h.264
            'codec_sel[4]': self.video_codec_map.get(publish.video_codec, '1'),
            # 音频编码 aac
            'audiocodec_sel[4]': self.audiocodec_map.get(publish.audio_codec, '6'),
            # 分辨率
            'standard_sel[4]': self.resolution_map.get(publish.resolution, '1'),
            # 地区 中国
            'source_sel[4]': self.region_map.get('china', '15'),
            # 制作组
            'team_sel[4]': self.team_map.get(publish.team, '9'),
            # 标签
            'tags[4][]': [1, 5, 6, 15, 17],
            # 匿名发布
            'uplver': 'yes',
        }

