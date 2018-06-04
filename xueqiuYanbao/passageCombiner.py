import json
from bs4 import BeautifulSoup
import os


companies=['SH600000', 'SH600016', 'SH600019', 'SH600028', 'SH600029', 'SH600030', 'SH600036', 'SH600048', 'SH600050', 'SH600104', 'SH600111', 'SH600309', 'SH600340', 'SH600518', 'SH600519', 'SH600547', 'SH600606', 'SH600837', 'SH600887', 'SH600958', 'SH600999', 'SH601006', 'SH601088', 'SH601166', 'SH601169', 'SH601186', 'SH601211', 'SH601288', 'SH601318', 'SH601328', 'SH601336', 'SH601390', 'SH601398', 'SH601601', 'SH601628', 'SH601668', 'SH601669', 'SH601688', 'SH601766', 'SH601800', 'SH601818', 'SH601857', 'SH601985', 'SH601988', 'SH601989', 'SH603993']
#companies=['SH600000']
all_files=os.listdir('./shangzheng50')
for company in companies:
    outputs=[] # list of json(dictionary)
    #print(company)
    #print(len([name for name in os.listdir(company)]))
    #path, dirs, files = os.walk(company).__next__()
    files=[filename for filename in all_files if company in filename]
    file_count = len(files)
    print(f'{file_count} pages for {company}')
    for i in range(file_count):
        with open(f'shangzheng50/{company}_page{i+1}.json','r') as f:
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
    with open(f'shangzheng50_combined/yanbao_{company}.json','w') as f:
        json.dump(outputs,f,ensure_ascii=False)
        f.flush()
        f.close()

