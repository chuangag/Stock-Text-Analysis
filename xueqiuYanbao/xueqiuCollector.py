import requests
import json
import time
import random

#urls=[]
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36',\
'Accept-Encoding':'gzip, deflate, br',\
'Cookie':'device_id=c0100ecdc4b255de547f0cae395f9fd3; s=fz11xetdga; aliyungf_tc=AQAAAHHs71AeIQwA6k3xe7cLNo6gfeLd; xq_a_token=93ef7d84fd99d7b5f81ea4e1442c7252dff29d20; xq_a_token.sig=2_cWCFNwc-q7CurYUzOoewHw_DM; xq_r_token=18ddc4996d6018b400ebaaaa74f144296c288826; xq_r_token.sig=7749cnGDm8cToOaVZtCC3FKmJys; u=931515142418137; __utma=1.723619502.1514297425.1514297425.1515142419.2; __utmc=1; __utmz=1.1515142419.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); Hm_lvt_1db88642e346389874251b5a1eded6e3=1514297438,1515142419,1515142424,1515144553; __utmb=1.7.10.1515142419; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1515145322',\
'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,ja;q=0.6',\
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}

datas=[]
for i in range(10):
    t=random.randint(3,6)
    payloads={'symbol_id':"SH600031",'count':10,'source':"研报",'page':(i+1)}
    res=requests.get("https://xueqiu.com/statuses/stock_timeline.json",headers=headers,params=payloads)
    print(res)
    data=json.loads(res.content)
    if i==0:
        print(data)
    datas.append(data)
    with open(('sanyizhonggong/page%d.json'%(i+1)),'w') as f:
        json.dump(data,f)
    print('catch%d'%(i+1))
    time.sleep(t)