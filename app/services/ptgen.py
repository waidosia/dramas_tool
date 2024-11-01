import re

import requests

import logging


genre_type = {
    "剧情" : "1",
    "爱情":"2" ,
    "穿越":"3" ,
    "重生":"4" ,
    "逆袭":"5",
    "都市":"6" ,
    "喜剧":"7" ,
    "科幻":"8" ,
}




def fetch_ptgen_data(api_url, resource_url) -> dict:
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
                douban_info['chinese_title'] = data.get('chinese_title','')
                # 年份: data['year']
                douban_info['year'] = data.get('year','')
                # 地区: data['中国大陆']
                douban_info['region'] = data.get('region',[])
                # 语言: data['language']
                douban_info['language'] = data.get('language',[])
                # 类型: data['genre']
                douban_info['genre'] = genre_conversion(data.get('genre',{}))
                return {'code': 200, 'data': douban_info}
        except Exception as e:
            retry_count += 1
            if retry_count < 3:
                logging.info(f'进行第{retry_count}次重试，错误原因:{e}')
            else:
                logging.error(f'重试次数已用完')
                return {'code':500,'data':None}


def format_conversion(text) -> str:
    if text != '':
        # 正则去除
        pattern = r'\[img\].*?\[/img\]'
        cleaned_format = re.sub(pattern, '', text).strip("\n")
        return cleaned_format
    return text


def genre_conversion(genre) -> []:
    new_genre = []
    for element in genre:
        if element in genre_type:
            new_genre.append(genre_type[element])
        else:
            continue
    return new_genre
