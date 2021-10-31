import time
import datetime
import json
import requests
import traceback
from urllib.parse import urlencode
import random


def bbs(s):
    # 优化日志， 打印10%
    i = random.randint(1, 100)
    if i > 90:
        print('[{}] {}'.format(datetime.datetime.now().strftime('%H:%M:%S'), s), file=f,flush=True)

def bbs2(s):
    print('[{}] {}'.format(datetime.datetime.now().strftime('%H:%M:%S'), s), file=f,flush=True)


def push(title, desc):
    try:

        url = 'https://sctapi.ftqq.com/{}.send?{}&{}&channel=8'.format(key, urlencode({'title': title}),
                                                                       urlencode({
                                                                           'desp': desc}))
        requests.post(url)
    except Exception as e:
        traceback.format_exc()


f = open('/root/iPhone-Pickup-Monitor/log.txt', 'w+')

# input('欢迎使用iPhone取货预约助手，请合理使用工具\n正在检查环境：\n即将播放预约提示音，按任意键开始...')
print('欢迎使用iPhone取货预约助手，请合理使用工具\n正在检查环境：\n即将播放预约提示音，按任意键开始...', file=f,flush=True)
# sound_alarm = './alarm.mp3'
# playsound(sound_alarm)

print('配置特定型号', file=f,flush=True)
# Config State
# 服务器位置
type_phone = json.load(open('/root/iPhone-Pickup-Monitor/category.json', encoding='utf-8'))
# type_phone = json.load(open('category.json', encoding='utf-8'))
url_param = ['state', 'city', 'district']
config_param = []
dic_param = {}
lst_choice_param = []
# print('--------------------------------')
# for index, item in enumerate(type_phone):
#     print('[{}] {}'.format(index, item))
# input_type = int(input('选择型号：'))
input_type = 2
choice_type = list(type_phone)[input_type]

# print('--------------------------------')
# for index, (key, value) in enumerate(type_phone[choice_type].items()):
#     print('[{}] {}'.format(index, value))
# input_size = int(input('选择尺寸/颜色：'))
input_size = 7
code_iphone = list(type_phone[choice_type])[input_size]
select_size = type_phone[choice_type][code_iphone]
# input('您的选择：{} {}，按任意键继续...'.format(choice_type, select_size))
print('您的选择：{} {}，按任意键继续...'.format(choice_type, select_size), file=f,flush=True)

print('选择计划预约的地址', file=f,flush=True)
headers = {
    'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    'Referer': 'https://www.apple.com.cn/shop/buy-iphone/iphone-13-pro/{}'.format(code_iphone),
    'DNT': '1',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
}
stepMap = {0: 5, 1: 0, 2: 4}
for step, param in enumerate(url_param):
    # print('请稍后...{}/{}'.format(step+1, len(url_param)))
    url = "https://www.apple.com.cn/shop/address-lookup?{}".format('&'.join(lst_choice_param))
    response = requests.request("GET", url, headers=headers, data={})
    response_json = json.loads(response.text)
    result_body = response_json['body']
    result_param = result_body[param]
    if type(result_param) is dict:
        result_data = result_param['data']
        # print('--------------------------------')
        # for index, item in enumerate(result_data):
        #     print('[{}] {}'.format(index, item['value']))
        # input_index = int(input('请选择序号：'))
        input_index = stepMap[step]
        choice_result = result_data[input_index]['value']
        dic_param[param] = choice_result
        lst_choice_param.append('{}={}'.format(param, dic_param[param]))
    else:
        lst_choice_param.append('{}={}'.format(param, result_param))

print('正在加载网络资源...', file=f,flush=True)
url = "https://www.apple.com.cn/shop/address-lookup?{}".format('&'.join(lst_choice_param))
response = requests.request("GET", url, headers=headers, data={})
response_json = json.loads(response.text)
provinceCityDistrict = response_json['body']['provinceCityDistrict']
# input('您的选择：{}，按任意键继续...'.format(provinceCityDistrict))
print('您的选择：{}，按任意键继续...'.format(provinceCityDistrict), file=f,flush=True)
# fixme 使用自己的key 谢谢
key = 'SCT89259TnFfyHpdFeaamFehINJJDzDaQ'
# Loop for checking iPhone status
pre_is_valiable = False
print('开始预约', file=f,flush=True)

while True:
    try:
        url = "https://www.apple.com.cn/shop/fulfillment-messages?pl=true&parts.0={}&location={}".format(code_iphone,
                                                                                                         provinceCityDistrict)
        try:
            response = requests.request("GET", url, headers=headers, data={})
        except Exception as e:
            print('发送库存请求失败',file=f)
        res_text = response.text
        res_json = json.loads(res_text)
        stores = res_json['body']['content']['pickupMessage']['stores']
        is_available = False
        storeName = ''
        for item in stores:
            storeName = item['storeName']
            if ('泰禾广场' == storeName):
                pickupSearchQuote = item['partsAvailability'][code_iphone]['pickupSearchQuote']
                bbs('{} - {}'.format(storeName, pickupSearchQuote))
                if pickupSearchQuote == '今天可取货':
                    is_available = True

        # 本次可以， 上次不可以，发送 可预约 推送
        if is_available & (not pre_is_valiable):
            # Display while iPhone is available
            # print('以下直营店预约可用：\n{}\nhttps://www.apple.com.cn/shop/buy-iphone'.format(','.join(lst_available)))
            push('iphone 预约', '{} 可以预约 {} {}'.format(
                storeName, choice_type,
                select_size))
            bbs2('iphone 预约', '{} 可以预约 {} {}'.format(
                storeName, choice_type,
                select_size))

            pre_is_valiable = True
        # 本次不可， 上次可， 发布售罄推送
        if (not is_available) & pre_is_valiable:
            push('iphone 售罄', '{} 售罄 {} {}'.format(
                storeName, choice_type,
                select_size))

        if not is_available:
            pre_is_valiable = False

    except Exception as err:
        bbs(err)
    #  本次可， 一分钟1次， 本次不可，1秒一次
    if (is_available):
        time.sleep(60)
    else:
        time.sleep(1)
