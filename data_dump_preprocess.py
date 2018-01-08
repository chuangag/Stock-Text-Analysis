import json
import csv
import numpy as np
import matplotlib.pyplot as plt

def pre_process_asr(yanbao='rawdata/xq_yanbao.json',tfidf='rawdata/tfidf.txt',stock_stats='rawdata/stockperform.csv'):
    with open(yanbao,'r') as f:
        datas=json.load(f)
    dates=[]
    for data in datas:
        date=data['time']
        #if date[:4]!='2015' and date[:4]!='2016':
        #    date='2017-'+date
        date=date[:-6]
        dates.append(date)

    with open(tfidf,'r') as f:
        vectors=f.readlines()
    print(len(vectors))
    print(len(dates))
    assert(len(vectors)==len(dates))

    dates_trade=[]
    asrs=[]
    profits=[]
    with open(stock_stats) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            dates_trade.append(row['\ufeffdate'][:10])
            asrs.append(row['ASR'])
            profits.append(row['profit'])
    return dates,vectors,dates_trade,asrs,profits

def get_correspond_label(date,dates_trade,asrs,profits,window_size=30,asr_threshold=[-0.2,-0.05,0.05,0.2],profit_threshold=[-0.2,-0.05,0.05,0.2]):
    """
    input: str date, dict date_asrs, int window_size
    ouput: float asr_sum_over_window
    """
    # take the nearest trade date if not exist
    if date not in dates_trade:
        y,m,d=int(date[:4]),int(date[-5:-3]),int(date[-2:])
        while format(y,'04')+'-'+format(m,'02')+'-'+format(d,'02') not in dates_trade:
            if d<31:
                d+=1
            elif m<12:
                m+=1
                d=1
            else:
                y+=1
                m=1
                d=1
            
            assert(y!=2018)
        idx=dates_trade.index(format(y,'04')+'-'+format(m,'02')+'-'+format(d,'02'))
            
    else:
        idx=dates_trade.index(date)
    asr_sum=0.0
    profit_sum=0.0
    for i in range(window_size):
        # prevent out of range
        if idx+i >=len(dates_trade):
            break
        asr_sum+=float(asrs[idx+i])
        profit_sum+=float(profits[idx+i])
    label_asr=len(asr_threshold)
    for idx,th in enumerate(asr_threshold):
        if asr_sum<th:
            label_asr=idx
            break
    label_profit=len(profit_threshold)
    for idx,th in enumerate(profit_threshold):
        if asr_sum<th:
            label_profit=idx
            break
    return label_asr,label_profit,asr_sum,profit_sum

def dump_data(filename,dates,vectors,dates_trade,asrs,profits,interval=30):
    with open(filename,'w') as f:
        datas=[]
        asrs_over_interval=[]
        profits_over_interval=[]
        for idx in range(len(dates)):
            label_asr,label_profit,asr_sum,profit_sum=get_correspond_label(dates[idx],dates_trade,asrs,profits,window_size=interval)
            datas.append((vectors[idx][1:-2],label_asr,label_profit))  # remove "[" and "]"
            asrs_over_interval.append(asr_sum)
            profits_over_interval.append(profit_sum)
        count_asr=[0,0,0,0,0]
        for data in datas:
            count_asr[data[1]]+=1 # count distibution of asr sum
        print('asr count: '+str(count_asr))
        count_profit=[0,0,0,0,0]
        for data in datas:
            count_profit[data[2]]+=1 # count distibution of profit sum
        print('profit count: '+str(count_profit))
        print(len(datas))
        json.dump(datas,f)
    return asrs_over_interval,profits_over_interval


companies=['kedaxunfei','fuxingyiyao','sanyizhonggong','yonghuichaoshi']

for company in companies:
    print(company)
    dates,vectors,dates_trade,asrs,profits=pre_process_asr(yanbao='rawdata/yanbao_'+company+'_1617.json',\
    tfidf='rawdata/tfidf_'+company+'.txt',stock_stats='rawdata/perform_'+company+'.csv')
    intervals=[30]
    for interval in intervals:
        filename='datasets/datas_'+company+'_'+str(interval)+'d.json'
        asrs_plt=dump_data(filename,dates,vectors,dates_trade,asrs,profits,interval=interval)
        """
        plt.hist(asrs_plt)
        plt.xlabel('asr sum over '+str(interval)+' days')
        plt.ylabel('number of data')
        plt.title('Total number of data:'+str(len(asrs_plt)))
        plt.axis([-0.5, 0.5,0,30])
        plt.savefig('figs/Distribution_over_'+str(interval)+'days')
        plt.close()
        """
    
    
