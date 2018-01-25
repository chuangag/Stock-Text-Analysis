import json
import io
years=['2016','2017']
companies=['kedaxunfei','fuxingyiyao','sanyizhonggong','yonghuichaoshi']

for company in companies:
    f = io.open('rawdata/yanbao_'+company+'.json', encoding='utf-8')
    content = json.load(f)
    content=[item for item in content if item['time'][:4] in years and item['time'][:7]!= '2017-12']
    print(len(content))
    with open('rawdata/yanbao_'+company+'_1617.json','w') as fo:
        json.dump(content,fo,ensure_ascii=False)
        fo.flush()
        fo.close()
    f.close()