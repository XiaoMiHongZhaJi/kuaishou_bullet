import requests
import json
import time

# 陈工
liveUrl = "https://live.kuaishou.com/u/3x2gpmyhvtdh9s6"
# KPL王者荣耀职业联赛
liveUrl = "https://live.kuaishou.com/u/KPL704668133"

# 刷新间隔
TIME = 3000


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
            print(e)
            return []

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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(liveUrl, headers=headers)
    response_text = response.text
    start_index = response_text.find('"liveStream":{"id":"')
    end_index = response_text.find('"', start_index + 20)

    while start_index == -1 or end_index == -1:
        print('获取不到 liveStreamId，可能是暂未开播，1分钟后再试...')
        time.sleep(60)
        response = requests.get(liveUrl, headers=headers)
        response_text = response.text
        start_index = response_text.find('"liveStream":{"id":"')
        end_index = response_text.find('"', start_index + 20)

    liveStreamId = response_text[start_index + 20:end_index]
    print('获取到 liveStreamId：' + liveStreamId + '，开始抓取弹幕')

    liveStream = KuaiLiveBarrage(liveStreamId)

    while True:
        barrages = liveStream.get()
        # print(barrages)
        for barrage in barrages:
            # print(barrage)
            userId = barrage.get('userId')
            userName = barrage.get('userName')
            userImg = barrage.get('userImg')
            content = barrage.get('content')
            type = barrage.get('type')
            timestamp = barrage.get('timestamp') / 1000
            time_text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            print(time_text + ' ' + userName + '：' + content)
        time.sleep(TIME / 1000)