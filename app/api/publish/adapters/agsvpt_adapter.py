from .base import SiteAdapter


class AgsvptAdapter(SiteAdapter):
    def __init__(self, config,proxies):
        super().__init__(config,proxies=proxies)
        self.xpath = '//a[@title="可在BT客户端使用，当天有效。"]/@href'
        self.type = '419'
        self.headers.update({
            'Host': 'new.agsvpt.com',
            'Referer': f'{self.config.url}/index.php',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
        self.resolution_map = {
            '480P': '4',
            '720P': '3',
            '1080P': '1',
            '2160P': '5',
            '4K': '5',
        }
        self.video_codec_map = {
            'AVC': '1',
            'HEVC': '6',
        }

        self.team_map = {
            'GodDramas': '23',
        }

        self.medium_map = {
            'WEB-DL':'10'
        }

        self.audiocodec_map = {
            'AAC': '6',
        }

    def build_description(self, publish):
        links = [publish.screenshot1_link, publish.screenshot2_link, publish.screenshot3_link,
                     publish.screenshot4_link, publish.screenshot5_link]
        return f"""{self.reference}
[img]{publish.cover}[/img]
[img]{self.groupIcon}[/img]
{publish.publish_info}
[img]{self.screenshotIcon}[/img]
{''.join(f"[img]{link}[/img]\n" for link in links if link)}
[img]{publish.video_screenshot_link}[/img]"""

    def format_main_title(self, title: str, media_info: str) -> str:
        main_title = title.replace('.', ' ')
        main_title = (main_title
                      .replace('H264', 'AVC')
                      .replace('H265', 'HEVC')
                      .replace('H 264', 'AVC')
                      .replace('H 265', 'HEVC')
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
            'medium_sel[4]': self.medium_map.get(publish.film_source, '10'),
            # 编码 h.264,avc h.265,hevc
            'codec_sel[4]': self.video_codec_map.get(publish.video_codec, '1'),
            # 音频编码 aac
            'audiocodec_sel[4]': self.audiocodec_map.get(publish.audio_codec, '6'),
            # 分辨率
            'standard_sel[4]': self.resolution_map.get(publish.resolution, '0'),
            # 制作组
            'team_sel[4]': self.team_map.get(publish.team, '1'),
            # 标签 紧转 国语 中字 完结 驻站 冰种
            'tags[4][]': [1,5, 6, 19, 44, 34],
            # 匿名发布
            'uplver': 'yes',
        }
