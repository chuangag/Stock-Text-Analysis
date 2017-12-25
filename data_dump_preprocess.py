import json
import csv
import numpy as np
import matplotlib.pyplot as plt

def pre_process_asr(yanbao='rawdata/xq_yanbao.json',tfidf='rawdata/tfidf.txt',stock_stats='rawdata/stockperform.csv'):
    with open(yanbao,'r') as f:
        datas=json.load(f)
    dates=[]
    for i in range(len(datas)):
        date=datas[i]['time']
        if date[:4]!='2015' and date[:4]!='2016':
            date='2017-'+date
            date=date[:-6]
            dates.append(date)

    with open(tfidf,'r') as f:
        vectors=f.readlines()
    assert(len(vectors)==len(dates))

    dates_asr=[]
    asrs=[]
    with open(stock_stats) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            dates_asr.append(row['date'][:10])
            asrs.append(row['ASR'])
    return dates,vectors,dates_asr,asrs

def get_correspond_label(date,dates_asr,asrs,window_size=30,asr_threshold=[-0.2,-0.05,0.05,0.2]):
    """
    input: str date, dict date_asrs, int window_size
    ouput: float asr_sum_over_window
    """
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
    return label,asr_sum

def dump_data(filename,dates,vectors,dates_asr,asrs,interval=30):
    with open(filename,'w') as f:
        datas=[]
        asrs_over_interval=[]
        for idx in range(len(dates)):
            label,asr_sum=get_correspond_label(dates[idx],dates_asr,asrs,window_size=interval)
            datas.append((vectors[idx][1:-2],label))
            asrs_over_interval.append(asr_sum)
        count=[0,0,0,0,0]
        for data in datas:
            count[data[1]]+=1
        print(count)
        json.dump(datas,f)
    return asrs_over_interval

dates,vectors,dates_asr,asrs=pre_process_asr()
intervals=[15,30,45,60,90]
for interval in intervals:
    filename='datasets/datas_'+str(interval)+'d.json'
    asrs_plt=dump_data(filename,dates,vectors,dates_asr,asrs,interval=interval)
    plt.hist(asrs_plt)
    plt.xlabel('asr sum over '+str(interval)+' days')
    plt.ylabel('number of data')
    plt.title('Total number of data:'+str(len(asrs_plt)))
    plt.axis([-0.5, 0.5,0,30])
    plt.savefig('figs/Distribution_over_'+str(interval)+'days')
    plt.close()
    
    
