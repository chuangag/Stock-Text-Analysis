import requests
import json
import time
import random

#urls=[]
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36',\
'Accept-Encoding':'gzip, deflate, br',\
'Cookie':'s=fn18y9gvn8; xq_a_token=0d524219cf0dd2d0a4d48f15e36f37ef9ebcbee1; xq_r_token=7095ce0c820e0a53c304a6ead234a6c6eca38488; __utmc=1; __utmt=1; u=131526238902151; device_id=afd74aaf4eaf297de3aed00eb12d7ec0; __utma=1.1210525900.1526238901.1526238901.1526239034.2; __utmz=1.1526239034.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); Hm_lvt_1db88642e346389874251b5a1eded6e3=1526238903,1526239034; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1526239236; __utmb=1.9.9.1526239236918',\
'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,ja;q=0.6',\
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}

"""
# get ids of stocks from log
stockids=[]
log=open('../shangzheng50log/log.txt','r')
lines=log.readlines()
for line in lines:
    words=line.strip().split()
    if words[0]=='bad':
        continue
    stockids.append(words[0].replace('#',''))
log.close()
print(stockids)
exit()
"""
stockids=['SH601601', 'SH601628', 'SH601668', 'SH601669', 'SH601688', 'SH601766', 'SH601800', 'SH601818', 'SH601857', 'SH601985', 'SH601988', 'SH601989', 'SH603993']
for stockid in stockids:
    datas=[]
    for i in range(100):
        t=random.randint(2,4)
        payloads={'symbol_id':stockid,'count':10,'source':"研报",'page':(i+1)}
        res=requests.get("https://xueqiu.com/statuses/stock_timeline.json",headers=headers,params=payloads)
        print(res)
        #print(res.content)
        data=json.loads(res.content)
        if len(data['list'])==0:
            break
        if i==0:
            print(data)
        datas.append(data)
        with open(f'shangzheng50/{stockid}_page{i+1}.json','w') as f:
            json.dump(data,f, ensure_ascii=False)
        print(f'catched:{stockid}_page{i+1}')
        time.sleep(t)