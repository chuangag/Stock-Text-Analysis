import json
from bs4 import BeautifulSoup
import os

outputs=[] # list of json(dictionary)
companies=['yonghuichaoshi']
for company in companies:
    #print(company)
    #print(len([name for name in os.listdir(company)]))
    path, dirs, files = os.walk(company).__next__()
    file_count = len(files)
    print(company)
    print(file_count)
    if company=='fuxingyiyao':
        file_count=8
    for i in range(file_count):
        with open(company+'/page%d.json'%(i+1),'r') as f:
            data=json.load(f)
        #print(data)
        count=data['count']
        reports=data['list']
        for report in reports:
            output={}
            output['target']=report['target']
            output['title']=report['title']
            output['text'] = BeautifulSoup(report['text']).text
            output['source']=report['source']
            output['time']=report['timeBefore']
            outputs.append(output)
    print(len(outputs))
    with open('yanbao_'+company+'.json','w') as f:
        json.dump(outputs,f,ensure_ascii=False)
        f.flush()
        f.close()

