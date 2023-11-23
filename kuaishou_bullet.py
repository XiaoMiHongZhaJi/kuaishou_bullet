import sys

import requests
import json
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# 创建一个输出到控制台的handler
console_handler = logging.StreamHandler(sys.stdout)
# 创建一个格式化器
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
# 将格式化器添加到handler
console_handler.setFormatter(formatter)
# 将handler添加到logger
logger.addHandler(console_handler)

## 此处是直播地址，每个主播固定
# 陈工
liveUrl = "https://live.kuaishou.com/u/3x2gpmyhvtdh9s6"
# KPL王者荣耀职业联赛
# liveUrl = "https://live.kuaishou.com/u/KPL704668133"
# 小米轰炸姬
# liveUrl = "https://live.kuaishou.com/u/3xcm2jt6vgeyx7c"


## 此处是直播流id，每次开播都不一样，会根据直播地址自动获取
## 但是！！如果自动获取次数过多或过于频繁，可能会导致IP被封禁，这种情况需要手动填入直播流id
##（获取方式在程序中会有提示。一旦手动填入直播流id，将不再通过直播地址自动获取）
liveStreamId = ''

# 弹幕刷新间隔，单位：秒
bulletRefresh = 3


def get_bullet():
    global liveStreamId
    if liveStreamId is None or liveStreamId == '':

        logger.info('通过直播地址：' + liveUrl + ' 尝试自动获取直播流id...')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
        }
        response = requests.get(liveUrl, headers=headers)
        response_text = response.text

        if response_text.find('请求过快，请稍后重试') > -1:
            logger.warning('页面提示请求过快，可能已经被封IP了...')
            logger.warning('请手动打开直播页面，按以下步骤获取直播流id：')
            logger.warning('1，聊天区域点击右键 -> 查看页面源代码（或者 ctrl + U 快捷键）')
            logger.warning('2，ctrl + F 查找 -> 输入 liveStream -> 找到 "liveStream":{"id":"xxxx"...')
            logger.warning('3，将 "id":"xxxx" 中的 xxxx 复制到程序第 31 行 liveStreamId = \'\' 的分号之间')
            logger.warning('4，重新运行程序')
            return 1

        start_index = response_text.find('"liveStream":{"id":"')
        end_index = response_text.find('"', start_index + 20)

        if start_index == -1 or end_index == -1:
            logger.info('获取不到直播流id，可能是暂未开播，程序退出...')
            return 0

        liveStreamId = response_text[start_index + 20:end_index]
        logger.info('获取到直播流id：' + liveStreamId + '，开始抓取弹幕...')
    else:
        logger.info('手动指定直播流id：' + liveStreamId + '，开始抓取弹幕...')

    liveStream = KuaiLiveBarrage(liveStreamId)
    while True:
        barrages = liveStream.get()
        # logger.info(barrages)
        if barrages is None:
            logger.warning('直播流id：' + liveStreamId + ' 获取弹幕出错，可能是直播已结束。程序退出...')
            return 0

        for barrage in barrages:
            # logger.info(barrage)
            userId = barrage.get('userId')
            userName = barrage.get('userName')
            userImg = barrage.get('userImg')
            content = barrage.get('content')
            type = barrage.get('type')
            timestamp = barrage.get('timestamp') / 1000
            time_text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            logger.info(time_text + ' ' + userName + '：' + content)
        time.sleep(bulletRefresh)


class KuaiLiveBarrage:
    def __init__(self, liveStreamId) -> None:
        self.liveStreamId = liveStreamId
        self.session = requests.Session()

    def get(self) -> list:
        data = self.session.get(
            f'https://livev.m.chenzhongtech.com/wap/live/feed?liveStreamId={self.liveStreamId}').text
        try:
            data = json.loads(json.loads(data))
        except Exception as e:
            logger.error(e)
            return None

        liveStreamFeeds = data['liveStreamFeeds']
        barrages = []
        if liveStreamFeeds:
            for liveStreamFeed in liveStreamFeeds:
                barrage = {
                    'userId': liveStreamFeed['author']['userId'],
                    'userName': liveStreamFeed['author']['userName'],
                    'userImg': liveStreamFeed['author']['headurl'],
                    'content': liveStreamFeed['content'],
                    'timestamp': liveStreamFeed['time'],
                    'type': liveStreamFeed['type']
                }
                barrages.append(barrage)
        return barrages


if __name__ == '__main__':
    get_bullet()
