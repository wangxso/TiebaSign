# -*- coding:utf-8 -*-
import os
import requests
import hashlib
import time
import copy
import logging
import random
import argparse
import yaml
import json
# debug level
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# product level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename="logfile.log", filemode="a+")

logger = logging.getLogger(__name__)

# API_URL
LIKIE_URL = "http://c.tieba.baidu.com/c/f/forum/like"
TBS_URL = "http://tieba.baidu.com/dc/common/tbs"
SIGN_URL = "http://c.tieba.baidu.com/c/c/forum/sign"
HEADERS = {
    'Host': 'tieba.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
}
SIGN_DATA = {
    '_client_type': '2',
    '_client_version': '9.7.8.0',
    '_phone_imei': '000000000000000',
    'model': 'MI+5',
    "net_type": "1",
}

# VARIABLE NAME
COOKIE = "Cookie"
BDUSS_S = "BDUSS"
EQUAL = r'='
EMPTY_STR = r''
TBS = 'tbs'
PAGE_NO = 'page_no'
ONE = '1'
TIMESTAMP = "timestamp"
DATA = 'data'
FID = 'fid'
SIGN_KEY = 'tiebaclient!!!'
UTF8 = "utf-8"
SIGN = "sign"
KW = "kw"
s = requests.Session()

def get_tbs(bduss):
    logger.info("开始获取tbs")
    headers = copy.copy(HEADERS)
    headers.update({COOKIE: EMPTY_STR.join([BDUSS_S, EQUAL, bduss])})
    print(headers)
    # headers.update({COOKIE: cookie})
    try:
        tbs = s.get(url=TBS_URL, headers=headers, timeout=5).json()[TBS]
    except Exception as e:
        logger.error("获取tbs出错" + e)
        logger.info("开始重新获取tbs")
        tbs = s.get(url=TBS_URL, headers=headers, timeout=5).json()[TBS]
    logger.info("获取tbs完成")
    return tbs


def get_favorite(bduss):
    logger.info("开始获取关注的贴吧")
    # 客户端关注的贴吧
    returnData = {}
    i = 1
    data = {
        'BDUSS': bduss,
        '_client_type': '2',
        '_client_id': 'wappc_1534235498291_488',
        '_client_version': '9.7.8.0',
        '_phone_imei': '000000000000000',
        'from': '1008621y',
        'page_no': '1',
        'page_size': '200',
        'model': 'MI+5',
        'net_type': '1',
        'timestamp': str(int(time.time())),
        'vcode_tag': '11',
    }
    data = encodeData(data)
    try:
        res = s.post(url=LIKIE_URL, data=data, timeout=5).json()
    except Exception as e:
        logger.error("获取关注的贴吧出错" + e)
        send_message("获取关注的贴吧出错" + e)
        return []
    returnData = res
    if 'forum_list' not in returnData:
        returnData['forum_list'] = []
    if res['forum_list'] == []:
        return {'gconforum': [], 'non-gconforum': []}
    if 'non-gconforum' not in returnData['forum_list']:
        returnData['forum_list']['non-gconforum'] = []
    if 'gconforum' not in returnData['forum_list']:
        returnData['forum_list']['gconforum'] = []
    while 'has_more' in res and res['has_more'] == '1':
        i = i + 1
        data = {
            'BDUSS': bduss,
            '_client_type': '2',
            '_client_id': 'wappc_1534235498291_488',
            '_client_version': '9.7.8.0',
            '_phone_imei': '000000000000000',
            'from': '1008621y',
            'page_no': str(i),
            'page_size': '200',
            'model': 'MI+5',
            'net_type': '1',
            'timestamp': str(int(time.time())),
            'vcode_tag': '11',
        }
        data = encodeData(data)
        try:
            res = s.post(url=LIKIE_URL, data=data, timeout=5).json()
        except Exception as e:
            logger.error("获取关注的贴吧出错" + e)
            continue
        if 'forum_list' not in res:
            continue
        if 'non-gconforum' in res['forum_list']:
            returnData['forum_list']['non-gconforum'].append(res['forum_list']['non-gconforum'])
        if 'gconforum' in res['forum_list']:
            returnData['forum_list']['gconforum'].append(res['forum_list']['gconforum'])

    t = []
    for i in returnData['forum_list']['non-gconforum']:
        if isinstance(i, list):
            for j in i:
                if isinstance(j, list):
                    for k in j:
                        t.append(k)
                else:
                    t.append(j)
        else:
            t.append(i)
    for i in returnData['forum_list']['gconforum']:
        if isinstance(i, list):
            for j in i:
                if isinstance(j, list):
                    for k in j:
                        t.append(k)
                else:
                    t.append(j)
        else:
            t.append(i)
    logger.info("共获取到【"+str(len(t))+"】个关注的贴吧")
    return t


def encodeData(data):
    s = EMPTY_STR
    keys = data.keys()
    for i in sorted(keys):
        s += i + EQUAL + str(data[i])
    sign = hashlib.md5((s + SIGN_KEY).encode(UTF8)).hexdigest().upper()
    data.update({SIGN: str(sign)})
    return data


def client_sign(bduss, tbs, fid, kw, idx, count):
    flag = True
    error_msgs = []
    # 客户端签到
    logger.info("【" + kw +"】吧，开始签到("+str(idx+1)+"/"+str(count)+")")
    headers = copy.copy(HEADERS)
    headers.update({COOKIE: EMPTY_STR.join([BDUSS_S, EQUAL, bduss])})
    # headers.update({COOKIE: cookie})
    data = copy.copy(SIGN_DATA)
    data.update({BDUSS: bduss, FID: fid, KW: kw, TBS: tbs, TIMESTAMP: str(int(time.time()))})
    # print(data)
    data = encodeData(data)
    res = s.post(url=SIGN_URL, data=data, timeout=5, headers=headers).json()
    # print(res)
    if res['error_code'] == '0':
        logger.info("签到成功，你是第"+res['user_info']['user_sign_rank']+"个签到的")
    if res['error_code'] != '0':
        logger.error(res['error_msg'])
<<<<<<< HEAD
        if res['error_msg'] not in error_msgs:
            error_msgs.append(res['error_msg'])
        flag = False
    return flag
=======
        send_message(res['error_msg'])
        return False
    return True
>>>>>>> d28a06224026ee403ba979110921acedf73c1d14


def main():
    # b = os.environ['BDUSS'].split('#')
    b = []
    b.append(BDUSS)
    for n, i in enumerate(b):
        if(len(i) <= 0):
            logger.info("未检测到BDUSS")
            continue
        logger.info("第" + str(n+1) + "个用户开始签到" )
        tbs = get_tbs(i)
        favorites = get_favorite(i)
        count = len(favorites)
        for idx,j in enumerate(favorites):
            time.sleep(random.randint(1,5))
            try:
<<<<<<< HEAD
                res = client_sign(i, tbs, j["id"], j["name"],idx,count)    
=======
                res = client_sign(i, tbs, j["id"], j["name"],idx,count)
                if not res:
                    break
>>>>>>> d28a06224026ee403ba979110921acedf73c1d14
            except TypeError:
                logger.error("第"+ str(n+1) + "个用户的BDUSS不正确")
                send_message("第"+ str(n+1) + "个用户的BDUSS不正确")
                break
        logger.info("第" + str(n+1) + "个用户签到完成")
        send_message("第" + str(n+1) + "个用户签到完成, 共完成签到" + str(count) + "个贴吧. ")
    logger.info("所有用户签到完成")

def init():
    global BDUSS
    global WEBHOOK_URL
    r = open("./config.yaml", "r")
    config = yaml.load(r, Loader=yaml.SafeLoader)
    if 'BDUSS' not in config:
        logger.error("配置文件中缺少BDUSS")
        return False
    if 'feishu' not in config:
        logger.info("配置文件缺少飞书通知配置")
    else:
        WEBHOOK_URL = config['feishu']['webhook']
    BDUSS = config['BDUSS']
    logger.info("BDUSS: " + BDUSS)
    logger.info("WEBGOOK: " + WEBHOOK_URL)
    r.close()
    return True

def send_message(msg):
    payload = json.dumps({
    "msg_type": "text",
    "content": {
        "text": msg
        }
    })
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", WEBHOOK_URL, headers=headers, data=payload)
    logger.info(response.text)

if __name__ == '__main__':
    if init():
        main()
    else:
        logger.error("程序运行出错, 请参考日志")
        
    
        