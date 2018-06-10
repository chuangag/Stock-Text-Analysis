import json
import csv
import io
import jieba
import re
import time
import datetime
from datetime import timedelta
from collections import Counter
import numpy as np
from sklearn import preprocessing

### ---Global Variables--- ###
cat_threshold=[-0.075,-0.025,0.025,0.075]
num_class=len(cat_threshold)+1
class_labels=list(range(num_class))
class_count=Counter()
companies=['SH600000', 'SH600016', 'SH600019', 'SH600028', 'SH600029', 'SH600030', 'SH600036', 'SH600048', 'SH600050', 'SH600104', 'SH600111', 'SH600309', 'SH600340', 'SH600518', 'SH600519', 'SH600547', 'SH600606', 'SH600837', 'SH600887', 'SH600958', 'SH600999', 'SH601006', 'SH601088', 'SH601166', 'SH601169', 'SH601186', 'SH601211', 'SH601288','SH601318', 'SH601328', 'SH601336', 'SH601390', 'SH601398', 'SH601601', 'SH601628', 'SH601668', 'SH601669', 'SH601688', 'SH601766', 'SH601800', 'SH601818', 'SH601857', 'SH601985', 'SH601988', 'SH601989', 'SH603993']


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class DatasetGenerator:
    """
    Generate a data set from the processed raw data, result in a list of data tuples(list of numbers actually) and save to file.
    The last element of each tuple will be the target class for that datum.
    Result in two files: dataset_X_cont, dataset_X_1hot and dataset_Y where X_cont is the data tuples with 
    continuous features, X_1hot is data tuples with one-hot features and Y is ther corresponding labels
    """
    def __init__(self,processed_data_folder,output_folder,stockid_list):
        self.stockid_list=stockid_list
        self.processed_data_folder=processed_data_folder
        self.output_folder=output_folder
        self.rawdatas=[]
        for stockid in stockid_list:
            with open(self.processed_data_folder+stockid+'.json','r') as f:
                datas=json.load(f)
                self.rawdatas.extend(datas)
        self.rawdatas_cont=[]
        self.normalized_array=[]
        self.rawdatas_disc=[]
        self.Ys=[]
    
    def selectNumericFeatures(self):
        numeric_features=set()
        discrete_features=set()
        assert(len(self.rawdatas)>0)
        for key,value in list(self.rawdatas[0].items()):
            if is_int(str(value)):
                discrete_features.add(key)
            elif is_number(str(value)):
                numeric_features.add(key)
        badkeys=['predict_target_value','predict_target_class','isGood']
        for key in badkeys:
            discrete_features.discard(key)
            numeric_features.discard(key)

        # TO CHANGE IN FUTURE
        discrete_features.discard('volume')
        numeric_features.add('volume')

        print('Numeric features:',numeric_features)
        print('Discrete features:',discrete_features)
        print('total:',len(numeric_features)+len(discrete_features),'features')
        self.rawdatas_cont=[{k:data[k] for k in numeric_features} for data in self.rawdatas]
        self.rawdatas_disc=[{k:data[k] for k in discrete_features} for data in self.rawdatas]
        self.Ys=[{'predict_target_class':data['predict_target_class']} for data in self.rawdatas]
    
    def normalization(self):
        rawdatas_nokey=[]
        for data in self.rawdatas_cont:
            rawdatas_nokey.append([value for key,value in list(data.items())])
        x=np.array(rawdatas_nokey)
        self.normalized_array = preprocessing.scale(x)

    def writeXcontCSV(self):
        with open(self.output_folder+'X_cont.csv', 'w') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(list(self.rawdatas_cont[0].keys()))
            csvwriter.writerows(self.normalized_array)

    def writeX1hotCSV(self):
        assert(len(self.rawdatas_disc)>0)
        keys = self.rawdatas_disc[0].keys()
        with open(self.output_folder+'X_disc.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.rawdatas_disc)   

    def writeY(self):
        assert(len(self.Ys)>0)
        keys = self.Ys[0].keys()
        with open(self.output_folder+'Y.csv', 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.Ys)    

    def writeCSV(self):
        print(f'Total {len(self.rawdatas)} data tuples')
        self.writeX1hotCSV()
        self.writeXcontCSV()
        self.writeY()
        print('Generated')

    def run(self):
        self.selectNumericFeatures()
        self.normalization()
        self.writeCSV()
        
        

class AllDataProcessor:
    """
    A processor for all stocks in a foler.
    """
    def __init__(self,rawdata_folder,output_folder,stat_folder,stockid_list,stopwordsfile='stop_words.txt'):
        """
        rawdata_folder: folder of the raw data
        ouput_folder: folder to output the processed data
        stat_folder: folder of the statistics for the stocks
        stockid_list: a list of stock id to be processed
        """
        self.stockid_list=stockid_list
        self.rawdata_folder=rawdata_folder
        self.output_folder=output_folder
        self.stat_folder=stat_folder
        self.atitude_word_set=set()
        self.title_wordset=set()
        self.text_wordset=set()
        self.titles=list()
        self.texts=list()
    
    @property
    def num_titles(self):
        return len(self.titles)
    
    @property
    def num_texts(self):
        return len(self.texts)

    def GiniCoefficient(self,word,pr):
        """
        Gini coefficient
        """
        #class_list=class_count.most_common(num_class)
        #class_list.reverse() # increasing order of size
        #print(class_list)

        cnt=Counter()
        for c in class_labels:
            cnt[c]=self.wcp(word,c,pr)
        cnt_list=cnt.most_common(num_class)
        cnt_list.reverse()
        
        miu=np.mean([self.wcp(word,i,pr) for i in range(num_class)])
        G=np.sum([(2*(i+1)-num_class-1)*self.wcp(word,cnt_list[i][0],pr) for i in range(num_class)])/\
                (num_class*(num_class-1)*miu)
        return G

    def wcp(self,word,clas,pr):
        """
        WithinClassPopularity
        """
        wcp=pr[word][clas]/sum([item[1] for item in list(pr[word].items())])
        assert(wcp>=0)
        return wcp
    
    def LaplacianSmoothProb(self):
        """
        return a two-layer dictionary pr where pr[word][clas]=Pr(f|class_i)
        """
        title_pr=dict()
        title_N=dict()
        text_pr=dict()
        text_N=dict()

        # Calculate Pr for title
        for word in list(self.title_wordset):
            for clas in class_labels:
                if clas not in title_N:
                    title_N[clas]=dict()
                title_N[clas][word]=0
                for title in self.titles:
                    if word in title[0] and title[1]==clas:
                        title_N[clas][word]+=1

        title_sigma=dict()
        for clas in class_labels:
            title_sigma[clas]=0
            for count in list(title_N[clas].items()):
                title_sigma[clas]+=count[1]

        for word in list(self.title_wordset):
            title_pr[word]=dict()
            for clas in class_labels:
                title_pr[word][clas]=(1+title_N[clas][word])/(len(self.title_wordset)+title_sigma[clas])

        # Calculate Pr for text
        for word in list(self.text_wordset):
            for clas in class_labels:
                if clas not in text_N:
                    text_N[clas]=dict()
                text_N[clas][word]=0
                for text in self.texts:
                    if word in text[0] and text[1]==clas:
                        text_N[clas][word]+=1

        text_sigma=dict()
        for clas in class_labels:
            text_sigma[clas]=0
            for count in list(text_N[clas].items()):
                text_sigma[clas]+=count[1]

        for word in list(self.text_wordset):
            text_pr[word]=dict()
            for clas in class_labels:
                text_pr[word][clas]=(1+text_N[clas][word])/(len(self.text_wordset)+text_sigma[clas])
        
        return title_pr,text_pr

    def polishKeyWords(self,freq_threshold=0.025,feature_proportion=0.05):
        """
        - 對每個word進行出現頻率統計，若在少於5%的文章中出現則刪除
	    - 使用WCP(within class popularity)進行篩選
        """
        # part 1 polish
        print(f"Total {self.num_titles} titles, {self.num_texts} texts, feature selecting........")
        print(f"Initially {len(self.title_wordset)} keywords for title, {len(self.text_wordset)} keywords for text")
        
        title_cnt=Counter()
        for word in list(self.title_wordset):
            for title in self.titles:
                if word in title[0]:
                    title_cnt[word]+=1
        text_cnt=Counter()
        for word in list(self.text_wordset):
            for text in self.texts:
                if word in text[0]:
                    text_cnt[word]+=1
        title_wordlist=[word for word in list(self.title_wordset) if title_cnt[word]>self.num_titles*freq_threshold]
        text_wordlist=[word for word in list(self.text_wordset) if text_cnt[word]>self.num_texts*freq_threshold]
        self.title_wordset=set(title_wordlist)
        self.text_wordset=set(text_wordlist)
        print(f'Deleted word that freq < 5%: {len(self.title_wordset)} keywords for title, {len(self.text_wordset)} keywords for text left')
        
        # part 2 polish using WCP and Gini coefficient
        title_pr,text_pr=self.LaplacianSmoothProb()
        Gini_title=Counter()
        Gini_text=Counter()
        for word in list(self.title_wordset):
            Gini_title[word]=self.GiniCoefficient(word,title_pr)
        for word in list(self.text_wordset):
            Gini_text[word]=self.GiniCoefficient(word,text_pr)
        title_wordlist=[word for (word,gini) in Gini_title.most_common(int(len(self.title_wordset)*feature_proportion))]
        text_wordlist=[word for (word,gini) in Gini_text.most_common(int(len(self.text_wordset)*feature_proportion))]
        self.title_wordset=set(title_wordlist)
        self.text_wordset=set(text_wordlist)
        print(f'Selected {feature_proportion} of the words that  has highest gini coefficient : {len(self.title_wordset)} keywords for title, {len(self.text_wordset)} keywords for text left')
        print("Selected features:")
        print('title words:',self.title_wordset, 'total:', len(self.title_wordset),'features')
        print('text words:',self.text_wordset, 'total:', len(self.text_wordset),'features')

    def run(self):
        processors=dict()
        # step 1 pre-process
        for stockid in self.stockid_list:
            print(f'Running:{stockid}')
            processors[stockid]=RawDataProcessor(self.rawdata_folder,stockid)
            processors[stockid].selectYears()
            #processor.number2text()
            processors[stockid].jiebacut()
            processors[stockid].matchStatistics(self.stat_folder,stockid)
            self.atitude_word_set=self.atitude_word_set.union(processors[stockid].atitudeWordsinSameStock())
            stock_title_wordset,stock_text_wordset,titles,texts=processors[stockid].getAllWordsInStock()
            self.title_wordset=self.title_wordset.union(stock_title_wordset)
            self.text_wordset=self.text_wordset.union(stock_text_wordset)
            self.titles.extend(titles)
            self.texts.extend(texts)
        self.polishKeyWords()
        print(f'Class distribution: {class_count}')
        atitude_word_list=sorted(list(self.atitude_word_set))
        title_word_list=sorted(list(self.title_wordset))
        text_word_list=sorted(list(self.text_wordset))
        # step 2 pre-process
        for stockid in self.stockid_list:
            processors[stockid].addAtitudeFeatures(atitude_word_list)
            processors[stockid].addWordFeatures(title_word_list,text_word_list)
            processors[stockid].dumpJson(self.output_folder,stockid)

class RawDataProcessor:
    """
    A processor for a single stock.
    """
    def __init__(self,datafolder,stockid,stopwordsfile='stop_words.txt'):
        """
        yanbao: path of raw data, json file 
        """
        # datas is a list of dictionary, each contain key of "target", "title", "text", "source", "time"
        with open(datafolder+stockid+'.json','r') as f:
            self.datas=json.load(f)
            self.originDatas=list(self.datas)
        self.check_stop_words=False
        if stopwordsfile!="":
            self.check_stop_words=True
            self.stop_words=[]
            with io.open(stopwordsfile, 'r', encoding='utf-8') as file:
                for line in file:
                    self.stop_words.append(line[:-1])
        for data in self.datas:
            data['isGood']=True
    
    def dumpJson(self,save_folder,stockid):
        """
        :save_file: path for saving the processed data, json file
        """
        with open(save_folder+stockid+'.json','w') as f:
            json.dump(self.datas,f,ensure_ascii=False)

    def number2text(self):
        # jieba is bad at cutting text numbers so maybe not to use this function before jieba cut
        """
        transform numerics and some symbols in text of raw data into Chinese text
        for simplicity, only direct transform but no polishing like 120 will be transform to 一二零 instead of 一百二十
        """
        _symbol_mapping={"%": "百分点",".":"点"} # jieba has stopped %, and ., not sure the effect of not stopping them
        _number_mapping={"0":"零","1":"一","2":"二","3":"三","4":"四","5":"五","6":"六","7":"七","8":"八","9":"九"}
        for item in self.datas:
            #text=item["text"]
            for pair in _symbol_mapping.items():
                item["text"]=item["text"].replace(*pair)
            for pair in _number_mapping.items():
                item["text"]=item["text"].replace(*pair)
    
    def jiebacut(self):
        """
        use jieba word cutting on the texts
        """
        company_regex = re.compile(r'［(.*)：(.*)］(.*)')
        note_regex = re.compile(r'[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?：●【】“”！，。？、~@#￥%……&*（）]+')

        for sj in self.datas:
            # NOT to select paper in 2017
            #if len(sj['time']) >= 15:
                #continue
            m_title = company_regex.match(sj['title'])
            if m_title==None:
                sj['isGood']=False
                continue;
            sj['researcherCompany'] = m_title.group(1)
            sj['atitude'] = m_title.group(2)
            sj['title_wordlist'] = list(jieba.cut(re.sub(note_regex, '', m_title.group(3))))
            sj['text_wordlist'] = list(jieba.cut(re.sub(note_regex, '', sj['text'])))
            if self.check_stop_words:
                for word in sj['title_wordlist']:
                    if word in self.stop_words:
                        sj['title_wordlist'].remove(word)
                for word in sj['text_wordlist']:
                    if word in self.stop_words:
                        sj['text_wordlist'].remove(word)
            
        self.removeBadDatas()
        
    def selectYears(self,years=['2016','2017']):
        """
        Only choose the report that is published in certain years(matching with the statistics)
        """
        self.datas=[item for item in self.datas if item["time"][:4] in years]
        for data in self.datas:
            data['isGood']=True
        #print(len(self.originDatas),len(self.datas))
    
    def removeBadDatas(self):
        """
        Remove bad datas
        """
        origin=len(self.datas)
        self.datas=[item for item in self.datas if item["isGood"]==True]
        new=len(self.datas)
        #print(f'removed {origin-new} datas')
 
    def matchStatistics(self,stat_folder,stockid,category_threshold=cat_threshold):
        """
        THIS FUNCTION IS PRETTY HARDCODED, MODIFICATION IS NEEDED IF THE FORMAT IS CHANGED
        match the statistic to each research paper, the matched statistic refers to section 3.2 of 
        重庆大学硕士论文：基于文本情感分析的股价预测研究与实现
        """
        # loading stat files
        stats=list()
        #dates=list()
        stats_dict=dict()
        with open(stat_folder+stockid[:2]+'#'+stockid[2:]+'.txt','r') as f:
            stats=f.readlines()
        for stat in stats:
            #stat_dict=dict()
            #stat_dict['date']=stat[:10].replace('/','-')
            #dates.append(stat[:10].replace('/','-')) # the date
            #stat_dict['content']=eval(stat[11:-1].replace('\'','\"'))
            stats_dict[stat[:10].replace('/','-')]=eval(stat[11:-1].replace('\'','\"'))

        # matching stat features to data tuples
        for data in self.datas:
            date=data['time'][:10]
            if date not in stats_dict:
                dateobj=datetime.date(int(date[:4]),int(date[5:7]),int(date[8:10]))
                delta=timedelta(days=-1)
                dateobj+=delta
                # find the most recent past date with stats
                while dateobj.isoformat() not in stats_dict:
                    dateobj+=delta
                date=dateobj.isoformat()
            data['change']=stats_dict[date]['chg']
            data['volume']=stats_dict[date]['volume']
            data['vol_change']=stats_dict[date]['vol_chg']
            data['profitRate']=stats_dict[date]['rate']
            data['RSI']=stats_dict[date]['RSI']
            data['avgPrice']=stats_dict[date]['price']['avg']
            data['K']=stats_dict[date]['KDJ']['K']
            data['D']=stats_dict[date]['KDJ']['D']
            data['J']=stats_dict[date]['KDJ']['J']
                
        # matching predict target to data tuples
        for data in self.datas:
            k_days=timedelta(days=10) # k=10, predict the price change of 10 days after
            curdate=data['time'][:10]
            date_predict=datetime.date(int(curdate[:4]),int(curdate[5:7]),int(curdate[8:10]))+k_days
            if date_predict.isoformat() not in stats_dict:
                delta=timedelta(days=1)
                date_predict+=delta
                
                # find the most recent future date with stats, terminate if cannot find match stats and mark the data by data['isGood']=False
                future_count=0
                while date_predict.isoformat() not in stats_dict:
                    future_count+=1
                    if future_count>=20:
                        data['isGood']=False
                        break;
                    date_predict+=delta
            if data['isGood']==True:
                future_price=stats_dict[date_predict.isoformat()]['price']['avg']
                data['predict_target_value']=(future_price-data['avgPrice'])/data['avgPrice']
                # classify according to category threshold
                data['predict_target_class']=0
                for idx,threshold in enumerate(sorted(category_threshold)):
                    if data['predict_target_value']>=threshold:
                        data['predict_target_class']=idx+1
                class_count[data['predict_target_class']]+=1
        self.removeBadDatas()

    def atitudeWordsinSameStock(self):
        """
        Evaluate the atitude words appear throughout the articles of the same stock.
        Return a set of atitude words
        """
        wordset=set()
        for data in self.datas:
            if data["atitude"] not in wordset:
                wordset.add(data["atitude"])
    
        #for data in self.datas:
        #    for word in list(wordset):
        #        if data["atitude"]==word:
        #            data[word]=1
        #        else:
        #            data[word]=0
        return wordset 
    
    def addAtitudeFeatures(self,word_list):
        """
        add one-hot features to the data tuples according, each feature according to a word in the word_list
        """
        for data in self.datas:
            for word in word_list:
                if data["atitude"]==word:
                    data[word]=1
                else:
                    data[word]=0 

    def addWordFeatures(self,title_wordlist,text_wordlist):
        for data in self.datas:
            title_c=Counter(data["title_wordlist"])
            for word in title_wordlist:
                data[f"titile_{word}"]=title_c[word]
            text_c=Counter(data["text_wordlist"])
            for word in text_wordlist:
                data[f"text_{word}"]=text_c[word]

    def getAllWordsInStock(self):
        """
        get the word set of titles and texts within same stock. return two sets
        Also return all list of tuples, (title sets, target_class) and (passage sets,target_class)
        """
        title_wordset=set()
        text_wordset=set()
        titles=list()
        texts=list()
        for data in self.datas:
            titles.append((set(data["title_wordlist"]),data['predict_target_class']))
            texts.append((set(data["text_wordlist"]),data['predict_target_class']))
            for word in data["title_wordlist"]:
                if word not in title_wordset:
                    title_wordset.add(word)
            for word in data["text_wordlist"]:
                if word not in text_wordset:
                    text_wordset.add(word)
        return title_wordset,text_wordset,titles,texts

if __name__=="__main__":
    stock_list=companies
    """
    processor=AllDataProcessor('./xueqiuYanbao/shangzheng50_combined/yanbao_',\
                                './xueqiuYanbao/shangzheng50_processed/',\
                                './shangzheng50log/output/',\
                                stock_list)
    processor.run()
    """
    dataGen=DatasetGenerator('./xueqiuYanbao/shangzheng50_processed/',\
                                './dataset_shangzheng50/',\
                                stock_list)
    dataGen.run()


    