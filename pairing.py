import json
import csv
import numpy as np

with open('xq_yanbao.json','r') as f:
    datas=json.load(f)
dates=[]
for i in range(len(datas)):
    date=datas[i]['time']
    if date[:4]!='2015' and date[:4]!='2016':
        date='2017-'+date
        date=date[:-6]
        dates.append(date)

with open('tfidf.txt','r') as f:
    vectors=f.readlines()
assert(len(vectors)==len(dates))

dates_asr=[]
asrs=[]
with open('stockperform.csv') as f:
    f_csv = csv.DictReader(f)
    for row in f_csv:
        dates_asr.append(row['date'][:10])
        asrs.append(row['ASR'])

"""
input: str date, dict date_asrs, int window_size
ouput: float asr_sum_over_window
"""
def get_correspond_label(date,dates_asr,asrs,window_size=90,asr_threshold=[-0.3,-0.1,0.1,0.3]):
    # take the nearest trade date if not exist
    if date not in dates_asr:
        y,m,d=int(date[:4]),int(date[-5:-3]),int(date[-2:])
        while str(y)+'-'+str(m)+'-'+str(d) not in dates_asr:
            if d<31:
                d+=1
            elif m<=12:
                m+=1
                d=1
            else:
                y+=1
                m=1
                d=1
        idx=dates_asr.index(str(y)+'-'+str(m)+'-'+str(d))
            
    else:
        idx=dates_asr.index(date)
    asr_sum=0.0
    for i in range(window_size):
        # prevent out of range
        if idx+i >=len(dates_asr):
            break
        asr_sum+=float(asrs[idx+i])
    label=len(asr_threshold)
    for idx,th in enumerate(asr_threshold):
        if asr_sum<th:
            label=idx
            break
    return label

with open('datas.json','w') as f:
    datas=[]
    for idx in range(len(dates)):
        datas.append((vectors[idx][1:-2],get_correspond_label(dates[idx],dates_asr,asrs)))
    count=[0,0,0,0,0]
    for data in datas:
        count[data[1]]+=1
    print(count)
    #json.dump(datas,f)
