"""
词向量快速开始模板
复制这段代码就能立即使用！
"""

def quick_start_english():
    """英文词向量快速开始"""
    try:
        import gensim.downloader as api
        
        print("正在下载模型（第一次运行需要下载，约70MB）...")
        model = api.load('glove-wiki-gigaword-50')
        
        print("\n✅ 模型加载成功！")
        print(f"词表大小: {len(model.key_to_index):,} 词")
        print(f"向量维度: {model.vector_size} 维")
        
        # 演示功能
        print("\n🎯 功能演示：")
        
        # 1. 获取词向量
        word = "computer"
        vector = model[word]
        print(f"1. 获取'{word}'的向量（前5维）:")
        print(f"   {vector[:5]}...")
        
        # 2. 找相似词
        print(f"\n2. 与'{word}'最相似的词:")
        similar = model.most_similar(word, topn=5)
        for w, score in similar:
            print(f"   {w}: {score:.3f}")
        
        # 3. 计算相似度
        print(f"\n3. 相似度计算:")
        pairs = [("computer", "laptop"), ("man", "woman"), ("king", "queen")]
        for w1, w2 in pairs:
            sim = model.similarity(w1, w2)
            print(f"   {w1} vs {w2}: {sim:.3f}")
        
        # 4. 词向量类比
        print(f"\n4. 词向量类比:")
        analogy = model.most_similar(positive=['woman', 'king'], negative=['man'], topn=3)
        print(f"   女人 + 国王 - 男人 ≈ ?")
        for w, score in analogy:
            print(f"   可能: {w} (相似度: {score:.3f})")
            
        return model
        
    except ImportError:
        print("请先安装: pip install gensim")
        return None
    except Exception as e:
        print(f"错误: {e}")
        print("可能是网络问题，请重试或使用离线模型")
        return None

def quick_start_chinese():
    """中文词向量快速开始（需要先下载模型）"""
    print("\n📚 中文词向量使用指南：")
    print("""
由于中文模型较大（6.7GB），需要先下载：
    
方法1：使用小型中文模型（推荐初学者）
  下载地址：https://github.com/Embedding/Chinese-Word-Vectors
  选择小的模型文件，如 sgns.weibo.bigram-char (300MB)
  
方法2：使用 HuggingFace 的BERT中文
  ```python
  from transformers import AutoTokenizer, AutoModel
  tokenizer = AutoTokenizer.from_pretrained('bert-base-chinese')
  model = AutoModel.from_pretrained('bert-base-chinese')
  ```
  
方法3：在线API（无需下载）
  - 百度AI开放平台
  - 腾讯云NLP
  - 阿里云NLP
    """)
    return None

def advanced_usage():
    """高级用法示例"""
    print("\n🚀 高级用法：")
    print("""
1. 文档向量（将文档表示为向量）
   ```python
   def document_vector(doc_words, model):
       # 平均所有词的向量
       vectors = [model[word] for word in doc_words if word in model]
       return np.mean(vectors, axis=0) if vectors else None
   ```

2. 语义搜索
   ```python
   def semantic_search(query, documents, model):
       query_vec = document_vector(query.split(), model)
       results = []
       for doc in documents:
           doc_vec = document_vector(doc.split(), model)
           if doc_vec is not None:
               similarity = cosine_similarity([query_vec], [doc_vec])[0][0]
               results.append((doc, similarity))
       return sorted(results, key=lambda x: x[1], reverse=True)
   ```

3. 文本分类特征
   ```python
   # 用词向量作为特征训练分类器
   from sklearn.svm import SVC
   
   # 将每个文本转换为向量
   X_train = [document_vector(text.split(), model) for text in train_texts]
   y_train = train_labels
   
   clf = SVC()
   clf.fit(X_train, y_train)
   ```
    """)

if __name__ == "__main__":
    print("=" * 60)
    print("词向量快速开始")
    print("=" * 60)
    
    print("\n请选择：")
    print("1. 英文词向量（立即体验，自动下载）")
    print("2. 中文词向量（需要先下载模型）")
    print("3. 查看高级用法")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        model = quick_start_english()
        if model:
            print("\n🎉 恭喜！你现在可以：")
            print("  model['word'] - 获取词向量")
            print("  model.most_similar('word') - 找相似词")
            print("  model.similarity('w1', 'w2') - 计算相似度")
            
            # 交互式查询
            while True:
                query = input("\n输入一个英文单词查询 (或输入 'quit' 退出): ").strip()
                if query.lower() == 'quit':
                    break
                if query in model:
                    similar = model.most_similar(query, topn=5)
                    print(f"与 '{query}' 相似的词:")
                    for w, score in similar:
                        print(f"  {w}: {score:.3f}")
                else:
                    print(f"'{query}' 不在词表中")
                    
    elif choice == "2":
        quick_start_chinese()
        
    elif choice == "3":
        advanced_usage()
        
    else:
        print("无效选择")
    
    print("\n" + "=" * 60)
    print("更多资源：")
    print("=" * 60)
    print("""
📚 学习资源：
  - Gensim官方文档：https://radimrehurek.com/gensim/
  - HuggingFace教程：https://huggingface.co/learn/nlp-course/
  - 斯坦福CS224N：http://web.stanford.edu/class/cs224n/

🔧 工具推荐：
  - Google Colab：免费GPU，预装环境
  - Jupyter Notebook：本地实验
  - VS Code + Python扩展：开发环境

📦 预训练模型仓库：
  - HuggingFace Model Hub：https://huggingface.co/models
  - Gensim Data：https://github.com/RaRe-Technologies/gensim-data
  - 中文词向量：https://github.com/Embedding/Chinese-Word-Vectors
    """)