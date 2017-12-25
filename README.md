# Stock-Text-Analysis
## jiebacut.py

**输入**
- `xq_yanbao.json`：原始数据集
- `stop_words.txt`：停用词词典

**输出**
- `split_True.json`：分词结果（默认使用停用词）
- `frequency.txt`：高频词表

## tfidf.py

**输入**
- `split_True.json`：分好词的数据集
- `frequency.txt`：高频词表

**输出**
- `tfidf.txt`：300维向量数组
- `words.txt`：向量的维度对应的词


## 2fc_keras.py
- 2層神經網路

**輸入**
- 單篇研報對應的300維tfidf數組

**輸出**
- 根據指定的SAR累加範圍與閾值生成的5類：大跌／小跌／持平／小漲／大漲

## ioutils.py
- `get_training_data_json(filename)`: helper function for getting training data, return x_train, y_train
- `shuffle_data(x_train,y_train)`: helper function for shuffleing training data

## data_dump_preprocess.py
Preprocess, pairup and dump data into json files

