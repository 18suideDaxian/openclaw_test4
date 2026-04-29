"""
现成词向量模型使用演示
由于下载大模型需要时间，这里演示如何使用和获取
"""

print("=" * 70)
print("现成词向量模型使用指南")
print("=" * 70)

print("\n1. 最方便的在线使用方式")
print("""
如果你只是想快速体验，可以使用在线服务：

1. **Gensim Data API**（推荐）
   ```python
   import gensim.downloader as api
   
   # 下载并加载预训练模型（自动下载）
   model = api.load('glove-wiki-gigaword-300')  # 400K词，300维
   model = api.load('word2vec-google-news-300') # 300万词，300维
   model = api.load('fasttext-wiki-news-subwords-300') # 支持子词
   
   # 直接使用
   vector = model['computer']
   similar = model.most_similar('computer', topn=10)
   ```
   
2. **HuggingFace Transformers**
   ```python
   from transformers import AutoTokenizer, AutoModel
   import torch
   
   # 加载BERT等模型
   tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
   model = AutoModel.from_pretrained('bert-base-uncased')
   
   # 获取上下文相关词向量
   inputs = tokenizer("Hello world", return_tensors="pt")
   outputs = model(**inputs)
   word_vectors = outputs.last_hidden_state
   ```
""")

print("\n2. 本地安装和使用")
print("""
步骤1：安装必要库
```bash
pip install gensim numpy
```

步骤2：下载预训练模型（选一个）
```bash
# Word2Vec（Google News，1.5GB）
wget -c "https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"
gunzip GoogleNews-vectors-negative300.bin.gz

# GloVe（维基百科，822MB）
wget https://nlp.stanford.edu/data/glove.6B.zip
unzip glove.6B.zip  # 得到 glove.6B.50d.txt 等文件

# FastText（多语言，6.7GB）
wget https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.zh.300.bin.gz
gunzip cc.zh.300.bin.gz
```

步骤3：Python代码使用
```python
from gensim.models import KeyedVectors

# 加载 Word2Vec
model = KeyedVectors.load_word2vec_format(
    'GoogleNews-vectors-negative300.bin', 
    binary=True
)

# 加载 GloVe（需要转换格式）
from gensim.scripts.glove2word2vec import glove2word2vec
glove2word2vec('glove.6B.300d.txt', 'glove.6B.300d.word2vec.txt')
model = KeyedVectors.load_word2vec_format('glove.6B.300d.word2vec.txt')

# 加载 FastText
from gensim.models import FastText
model = FastText.load_fasttext_format('cc.zh.300.bin')
```
""")

print("\n3. 实际使用示例代码")
print("让我们写一个完整的示例：")

# 模拟一个简单的词向量查询系统
class MockWordVectors:
    """模拟预训练词向量（避免实际下载）"""
    
    def __init__(self):
        # 模拟一些词向量
        self.vectors = {
            'computer': [0.1, 0.2, 0.3, 0.4, 0.5],
            'laptop': [0.12, 0.18, 0.28, 0.42, 0.48],
            'phone': [0.15, 0.25, 0.2, 0.3, 0.4],
            'book': [-0.1, -0.2, 0.1, 0.2, 0.3],
            'read': [-0.05, -0.15, 0.15, 0.25, 0.35],
            'king': [0.5, 0.3, 0.2, 0.7, 0.1],
            'queen': [0.6, 0.4, 0.3, 0.8, 0.2],
            'man': [0.3, 0.2, 0.1, 0.5, 0.1],
            'woman': [0.4, 0.3, 0.2, 0.6, 0.2],
            'paris': [0.7, 0.5, 0.4, 0.9, 0.3],
            'france': [0.65, 0.45, 0.35, 0.85, 0.25],
            'berlin': [0.68, 0.48, 0.38, 0.88, 0.28],
            'germany': [0.63, 0.43, 0.33, 0.83, 0.23],
        }
    
    def __getitem__(self, word):
        return self.vectors.get(word, None)
    
    def similarity(self, word1, word2):
        """计算余弦相似度"""
        import numpy as np
        v1 = self[word1]
        v2 = self[word2]
        if v1 is None or v2 is None:
            return None
        v1, v2 = np.array(v1), np.array(v2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    
    def most_similar(self, word, topn=5):
        """找最相似的词"""
        import numpy as np
        target = self[word]
        if target is None:
            return []
        
        target = np.array(target)
        similarities = []
        
        for w, v in self.vectors.items():
            if w == word:
                continue
            v = np.array(v)
            sim = np.dot(target, v) / (np.linalg.norm(target) * np.linalg.norm(v))
            similarities.append((w, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:topn]
    
    def analogy(self, a, b, c, topn=3):
        """词向量类比：a - b + c"""
        import numpy as np
        va, vb, vc = self[a], self[b], self[c]
        if None in (va, vb, vc):
            return []
        
        va, vb, vc = np.array(va), np.array(vb), np.array(vc)
        result = va - vb + vc
        
        # 找最相似的词
        similarities = []
        for w, v in self.vectors.items():
            if w in (a, b, c):
                continue
            v = np.array(v)
            sim = np.dot(result, v) / (np.linalg.norm(result) * np.linalg.norm(v))
            similarities.append((w, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:topn]

# 演示
print("\n模拟词向量系统演示：")
model = MockWordVectors()

print("\n1. 获取词向量：")
words = ['computer', 'king', 'paris']
for word in words:
    vec = model[word]
    print(f"  '{word}' 的向量（前3维）: {vec[:3]}...")

print("\n2. 计算相似度：")
pairs = [('computer', 'laptop'), ('computer', 'book'), ('king', 'queen')]
for w1, w2 in pairs:
    sim = model.similarity(w1, w2)
    print(f"  '{w1}' vs '{w2}': {sim:.3f}")

print("\n3. 找相似词：")
test_words = ['computer', 'king']
for word in test_words:
    similar = model.most_similar(word, topn=3)
    print(f"  与'{word}'最相似的词:")
    for w, sim in similar:
        print(f"    {w}: {sim:.3f}")

print("\n4. 词向量类比：")
analogies = [
    ('king', 'man', 'woman'),  # 国王 - 男人 + 女人 ≈ ?
    ('paris', 'france', 'germany')  # 巴黎 - 法国 + 德国 ≈ ?
]

for a, b, c in analogies:
    results = model.analogy(a, b, c, topn=2)
    print(f"\n  {a} - {b} + {c} ≈ ?")
    for w, sim in results:
        print(f"    可能: {w} (相似度: {sim:.3f})")

print("\n5. 实际项目中的使用场景：")
print("""
场景1：文本分类
  ```python
  # 将文档中所有词的向量平均，得到文档向量
  doc_vector = average([model[word] for word in doc_words])
  # 用文档向量训练分类器
  ```

场景2：语义搜索
  ```python
  # 查询向量 = 平均(查询词的向量)
  query_vec = average([model[q] for q in query_words])
  # 计算与所有文档的相似度，排序返回
  ```

场景3：推荐系统
  ```python
  # 用户向量 = 平均(用户历史点击词的向量)
  user_vec = average([model[word] for word in user_history])
  # 推荐与用户向量最相似的内容
  ```

场景4：词义消歧
  ```python
  # 多义词"苹果"在不同上下文中的含义
  context1 = ["吃", "水果", "甜"]  # 水果含义
  context2 = ["手机", "公司", "乔布斯"]  # 公司含义
  # 计算"苹果"向量与两个上下文的相似度
  ```
""")

print("\n6. 不同模型的对比")
print("""
| 模型 | 训练数据 | 词表大小 | 维度 | 特点 | 适用场景 |
|------|----------|----------|------|------|----------|
| **Word2Vec** | Google News | 300万 | 300 | 经典，速度快 | 英文通用任务 |
| **GloVe** | 维基百科+网页 | 220万 | 300 | 全局统计，稳定 | 学术研究，需要稳定性 |
| **FastText** | Common Crawl | 200万 | 300 | 支持子词，OOV友好 | 多语言，有未登录词 |
| **BERT** | 图书+维基百科 | 3万 | 768 | 上下文相关，动态 | 需要深层理解的任务 |
| **中文词向量** | 中文维基+新闻 | 800万 | 200-300 | 中文优化 | 中文NLP任务 |
""")

print("\n7. 快速开始建议")
print("""
如果你是初学者，建议：

1. **从 Gensim Data API 开始**
   ```python
   import gensim.downloader as api
   model = api.load('glove-wiki-gigaword-50')  # 小模型，快速下载
   print(model.most_similar('computer'))
   ```

2. **中文用户用 FastText**
   ```python
   # 下载中文 FastText 模型
   # 支持简体繁体，有子词信息
   ```

3. **生产环境用 BERT**
   ```python
   from transformers import AutoTokenizer, AutoModel
   # 获取上下文相关词向量，效果最好
   ```

4. **资源有限用 GloVe**
   ```python
   # 模型文件较小，效果稳定
   # glove.6B.50d.txt 只有 69MB
   ```
""")

print("\n8. 注意事项")
print("""
1. **内存需求**：大模型需要几GB内存
2. **磁盘空间**：模型文件从几十MB到几GB
3. **加载时间**：第一次加载可能需要几十秒
4. **语言匹配**：确保模型语言与你的数据匹配
5. **领域适配**：通用模型在专业领域可能效果差
6. **更新问题**：预训练模型不会自动更新知识
""")

print("\n" + "=" * 70)
print("总结：如何获取和使用现成词向量")
print("=" * 70)
print("""
三步搞定：

1. **选择模型**（根据需求）：
   - 英文通用：Word2Vec/GloVe
   - 中文：腾讯词向量/FastText中文
   - 多语言/未登录词：FastText
   - 最新最好：BERT/GPT

2. **下载加载**：
   ```python
   # 最简单的方式
   import gensim.downloader as api
   model = api.load('模型名称')
   ```

3. **直接使用**：
   ```python
   vector = model['单词']  # 获取向量
   similar = model.most_similar('单词')  # 找相似词
   analogy = 模型不支持直接类比，但可以计算
   ```

现在就去试试吧！这是 NLP 中最成熟、最易用的技术之一。
""")