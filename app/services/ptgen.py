import re

import requests

import logging

def fetch_ptgen_data(api_url, resource_url) -> (bool,dict):
    douban_info = {}
    retry_count = 0
    while retry_count < 3:
        try:
            # 设置一个合理的超时时间，例如10秒
            response = requests.get(f"{api_url}?url={resource_url}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 封面: data['poster']
                douban_info['poster'] = data.get('poster','')
                # format信息
                douban_info['format'] = format_conversion(data.get('format', ''))
                # 简介: data['introduction']
                douban_info['introduction'] = data.get('introduction','')
                # 中文名: data['chinese_title']
                douban_info['cnName'] = data.get('chinese_title','')
                # 年份: data['year']
                douban_info['year'] = data.get('year','')
                # 地区: data['中国大陆']
                douban_info['region'] = data.get('region',[])
                # 语言: data['language']
                douban_info['language'] = data.get('language',[])
                # 类型: data['genre']
                douban_info['category'] = data.get('genre',{})
                return  True,douban_info
        except Exception as e:
            retry_count += 1
            if retry_count < 3:
                logging.info(f'进行第{retry_count}次重试，错误原因:{e}')
            else:
                logging.error(f'重试次数已用完')
                return False,None


def format_conversion(text) -> str:
    if text != '':
        # 正则去除
        pattern = r'\[img\].*?\[/img\]'
        cleaned_format = re.sub(pattern, '', text).strip("\n")
        return cleaned_format
    return text

