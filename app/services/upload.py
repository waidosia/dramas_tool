import json
import logging
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from requests import RequestException
from PIL import Image
import uuid

global token

proxies = {}


# 二次封装，把upload_screenshot函数封装成一个公共函数，在函数里调用不同的上传图床API
def upload_screenshot(imageHost,content,proxyUrl):
    global proxies

    if imageHost.is_proxy is True and proxyUrl != '':
        logging.info(f'使用代理:{proxyUrl}')
        proxies = {
            'http': proxyUrl,
            'https': proxyUrl
        }

    if imageHost.name == 'Pter':
        return pter_upload(imageHost,content)
    elif imageHost.name == '兰空图床':
        return lsky_pro_upload(imageHost,content)
    elif imageHost.name == 'pixhost':
        return pixhost_upload(imageHost,content)
    else:
        # 暂不支持
        logging.error("未知图床")
        return {'code':'404','url':''}


# 兰空图床
def lsky_pro_upload(imageHost,content):
    global proxies
    file_obj = BytesIO(content)
    file_obj.name = send_file_name()+'.'+get_pic_type(content)

    headers = {'Accept': 'application/json'}
    files = {'file': file_obj}
    if imageHost.key_or_cookie != '':
        headers['Authorization'] = imageHost.key_or_cookie

    res = None
    retry_count = 0
    while retry_count < 3:
        try:
            # 发送POST请求
            res = requests.post("{}/api/v1/upload".format(imageHost.url),files=files,data={},headers=headers,proxies=proxies)
            logging.info("已成功发送上传图床的请求")
            break
        except RequestException as e:
            logging.error("请求过程中出现错误:" + str(e))
            retry_count += 1
            if retry_count < 3:
                logging.info("进行第" + str(retry_count) + "次重试")
            else:
                logging.error("重试次数已用完")
                return {'code':500,'url': ''}
    try:
        api_response = json.loads(res.text)
        if api_response['status']:
            return {'code':200,'url':api_response['data']['links']['url']}
        else:
            return {'code': 400, 'url': ''}
    except json.JSONDecodeError:
        logging.error("响应不是有效的JSON格式")
        return {'code':500,"url": ''}




# 猫站
def pter_upload(imageHost,content):
    global token
    global proxies
    token = ''
    auth_token = get_token(imageHost.url, imageHost.key_or_cookie)
    if auth_token == '':
        logging.error('未找到auth_token')
        return {"code":400,"url": ''}

    logging.info("开始上传图床")

    files = {'source': content}

    headers = {'cookie': imageHost.key_or_cookie}
    data = {'type': 'file', 'action': 'upload', 'nsfw': 0, 'auth_token': auth_token}
    req = None
    retry_count = 0
    while retry_count < 3:
        try:
            req = requests.post(f'{imageHost.url}/json', data=data, files=files, headers=headers, proxies=proxies)
            logging.info(req.text)
            break
        except Exception as r:
            retry_count += 1
            if retry_count < 3:
                logging.info(f'进行第{retry_count}次重试，错误原因是：{r}', )
            else:
                logging.error(f'重试次数已用完')
                return {"code":500,"url": ''}

    try:
        res = req.json()
        if not req.ok or 'error' in res or 'status_code' in res and res.get('status_code') != 200:
            logging.error("请求过程中出现错误:" + res.text)
            return {"code":400,"url": ''}
        if 'image' not in res or 'url' not in res['image']:
            logging.error(f"图片直链获取失败")
            return {"code": 400, "url": ''}
        return  {"code": 200, "url": res['image']['url']}

    except json.decoder.JSONDecodeError:
        logging.error("处理返回的JSON过程中出现错误")
        return {"code":500,"url": ''}



# pixhost 图床
def pixhost_upload(imageHost,content):
    global proxies
    logging.info('接受到上传pixhost图床请求')
    files = {'img': (send_file_name(), content, get_pic_type(content))}
    data = {'content_type': 0, 'max_th_size': 420}
    headers = {'Accept': 'application/json'}
    res = None
    retry_count = 0
    while retry_count < 3:
        try:
            # 发送POST请求
            logging.info("开始发送上传图床的请求")
            res = requests.post(imageHost.url, headers=headers, data=data, files=files,proxies=proxies)
            break
        except RequestException as e:
            logging.error("请求过程中出现错误:" + str(e))
            retry_count += 1
            if retry_count < 3:
                logging.info("进行第" + str(retry_count) + "次重试")
            else:
                logging.error("重试次数已用完")
                return {'code': 500, 'url': ''}

    try:
        data = json.loads(res.text)
        # 提取所需的URL
        image_url = data["th_url"].replace("//t", "//img").replace("/thumbs/", "/images/")
        return {"code":200,"url": image_url}
    except KeyError as e:
        logging.error("图床响应结果缺少所需的值：" + str(e))
        return {"code":400,"url": ''}
    except json.JSONDecodeError as e:
        logging.error("处理返回的JSON过程中出现错误：" + str(e))
        return {"code":500,"url": ''}


def get_token(url, cookie):
    global proxies
    global token
    if token:
        return token

    headers = {
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/99.0.4844.51 Safari/537.36'}
    response = None
    retry_count = 0
    while retry_count < 3:
        try:
            response = requests.get(url=url, headers=headers, proxies=proxies, timeout=10)
            break
        except Exception as r:
            logging.error(f'获取token失败，原因:{r}')
            retry_count += 1
            if retry_count < 3:
                logging.info(f'进行第{retry_count}次重试')
            else:
                logging.error(f'重试次数已用完')
                return ''

    content = response.text
    if "马上注册" in content:
        return ''

    soup = BeautifulSoup(content, 'lxml')
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if 'auth_token' in href:
            token = href.split("auth_token=")[-1]
            return token
    return ''


def get_pic_type(file_stream):
    try:
        img = Image.open(BytesIO(file_stream))
        return img.format if img.format else "jpeg"
    except IOError:
        return "unknown"

def send_file_name():
    return uuid.uuid4().hex