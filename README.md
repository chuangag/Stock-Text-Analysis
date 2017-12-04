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
