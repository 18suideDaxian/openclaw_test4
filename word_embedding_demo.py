import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SimpleWordEmbedding:
    """简化的词向量模型"""
    
    def __init__(self, vocab_size=100, embedding_dim=10):
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        
        # 随机初始化词向量（实际中通过学习得到）
        np.random.seed(42)
        self.embeddings = np.random.randn(vocab_size, embedding_dim) * 0.1
        
        # 创建一些有意义的词
        self.word_to_idx = {
            "猫": 0, "狗": 1, "鱼": 2, "老虎": 3, "狮子": 4,
            "苹果": 5, "香蕉": 6, "橙子": 7, "水果": 8,
            "汽车": 9, "飞机": 10, "火车": 11, "交通工具": 12,
            "国王": 13, "女王": 14, "男人": 15, "女人": 16,
            "中国": 17, "北京": 18, "日本": 19, "东京": 20
        }
        
        # 手动设置一些语义关系（模拟学习结果）
        self._set_semantic_relations()
    
    def _set_semantic_relations(self):
        """设置语义关系（模拟训练后的结果）"""
        # 动物类：猫、狗、鱼、老虎、狮子
        animal_center = np.array([0.8, 0.2, -0.1, 0.5, 0.3, 0.1, -0.2, 0.4, 0.6, -0.3])
        self.embeddings[0] = animal_center + np.random.randn(10) * 0.1  # 猫
        self.embeddings[1] = animal_center + np.random.randn(10) * 0.1  # 狗
        self.embeddings[2] = animal_center + np.array([-0.5, 0.7, 0.3, -0.2, 0.1, 0.4, 0.2, -0.3, 0.5, 0.1])  # 鱼
        self.embeddings[3] = animal_center + np.array([0.9, 0.1, 0.4, 0.6, 0.2, 0.3, 0.1, 0.5, 0.4, 0.2])  # 老虎
        self.embeddings[4] = animal_center + np.array([0.8, 0.3, 0.5, 0.7, 0.1, 0.4, 0.2, 0.6, 0.3, 0.3])  # 狮子
        
        # 水果类：苹果、香蕉、橙子
        fruit_center = np.array([-0.2, 0.9, 0.3, -0.1, 0.7, 0.4, 0.2, 0.1, -0.3, 0.5])
        self.embeddings[5] = fruit_center + np.random.randn(10) * 0.1  # 苹果
        self.embeddings[6] = fruit_center + np.random.randn(10) * 0.1  # 香蕉
        self.embeddings[7] = fruit_center + np.random.randn(10) * 0.1  # 橙子
        self.embeddings[8] = fruit_center  # 水果（类别）
        
        # 交通工具类
        vehicle_center = np.array([0.1, -0.3, 0.8, 0.4, -0.2, 0.6, 0.3, 0.2, 0.7, 0.1])
        self.embeddings[9] = vehicle_center + np.random.randn(10) * 0.1  # 汽车
        self.embeddings[10] = vehicle_center + np.array([0.3, -0.1, 0.9, 0.5, 0.1, 0.7, 0.4, 0.3, 0.8, 0.2])  # 飞机
        self.embeddings[11] = vehicle_center + np.array([0.2, -0.2, 0.7, 0.3, -0.1, 0.5, 0.2, 0.1, 0.6, 0.1])  # 火车
        self.embeddings[12] = vehicle_center  # 交通工具（类别）
        
        # 类比关系：国王 - 男人 + 女人 ≈ 女王
        self.embeddings[13] = np.array([0.5, 0.3, 0.2, 0.7, 0.1, 0.4, 0.6, 0.2, 0.3, 0.5])  # 国王
        self.embeddings[15] = np.array([0.3, 0.2, 0.1, 0.5, 0.1, 0.3, 0.4, 0.1, 0.2, 0.3])  # 男人
        self.embeddings[16] = np.array([0.4, 0.3, 0.2, 0.6, 0.2, 0.4, 0.5, 0.2, 0.3, 0.4])  # 女人
        self.embeddings[14] = self.embeddings[13] - self.embeddings[15] + self.embeddings[16]  # 女王
        
        # 国家城市关系：中国 - 北京 + 东京 ≈ 日本
        self.embeddings[17] = np.array([0.6, 0.4, 0.3, 0.8, 0.2, 0.5, 0.7, 0.3, 0.4, 0.6])  # 中国
        self.embeddings[18] = np.array([0.5, 0.3, 0.2, 0.7, 0.1, 0.4, 0.6, 0.2, 0.3, 0.5])  # 北京
        self.embeddings[20] = np.array([0.4, 0.5, 0.3, 0.6, 0.3, 0.5, 0.5, 0.4, 0.5, 0.4])  # 东京
        self.embeddings[19] = self.embeddings[17] - self.embeddings[18] + self.embeddings[20]  # 日本
    
    def get_vector(self, word):
        """获取词向量"""
        if word in self.word_to_idx:
            idx = self.word_to_idx[word]
            return self.embeddings[idx]
        else:
            return None
    
    def similarity(self, word1, word2):
        """计算余弦相似度"""
        vec1 = self.get_vector(word1)
        vec2 = self.get_vector(word2)
        if vec1 is not None and vec2 is not None:
            return cosine_similarity([vec1], [vec2])[0][0]
        return None
    
    def analogy(self, a, b, c):
        """词向量类比：a - b + c"""
        vec_a = self.get_vector(a)
        vec_b = self.get_vector(b)
        vec_c = self.get_vector(c)
        
        if vec_a is not None and vec_b is not None and vec_c is not None:
            result_vec = vec_a - vec_b + vec_c
            
            # 找到最相似的词
            similarities = []
            for word, idx in self.word_to_idx.items():
                if word not in [a, b, c]:
                    sim = cosine_similarity([result_vec], [self.embeddings[idx]])[0][0]
                    similarities.append((word, sim))
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            return result_vec, similarities[:3]
        return None, []
    
    def visualize_relationships(self):
        """可视化词向量关系"""
        print("=" * 60)
        print("词向量关系演示")
        print("=" * 60)
        
        # 1. 展示词向量
        print("\n1. 词向量示例（前5维）:")
        for word in ["猫", "狗", "鱼", "苹果", "汽车"]:
            vec = self.get_vector(word)
            print(f"   {word}: {vec[:5]}...")
        
        # 2. 语义相似度
        print("\n2. 语义相似度:")
        pairs = [("猫", "狗"), ("猫", "鱼"), ("苹果", "香蕉"), ("汽车", "飞机"), ("猫", "汽车")]
        for w1, w2 in pairs:
            sim = self.similarity(w1, w2)
            print(f"   {w1} vs {w2}: {sim:.3f}")
        
        # 3. 类比关系
        print("\n3. 词向量类比:")
        
        # 国王 - 男人 + 女人 ≈ 女王
        result_vec, top_matches = self.analogy("国王", "男人", "女人")
        print(f"   国王 - 男人 + 女人 ≈ ?")
        print(f"   最相似词: {top_matches[0][0]} (相似度: {top_matches[0][1]:.3f})")
        
        # 中国 - 北京 + 东京 ≈ 日本
        result_vec, top_matches = self.analogy("中国", "北京", "东京")
        print(f"\n   中国 - 北京 + 东京 ≈ ?")
        print(f"   最相似词: {top_matches[0][0]} (相似度: {top_matches[0][1]:.3f})")
        
        # 4. 聚类效果
        print("\n4. 语义聚类（通过向量距离）:")
        print("   动物类: 猫、狗、鱼、老虎、狮子")
        print("   水果类: 苹果、香蕉、橙子")
        print("   交通工具: 汽车、飞机、火车")
        
        # 计算类内平均相似度
        animal_words = ["猫", "狗", "鱼", "老虎", "狮子"]
        fruit_words = ["苹果", "香蕉", "橙子"]
        vehicle_words = ["汽车", "飞机", "火车"]
        
        def avg_similarity(words):
            total = 0
            count = 0
            for i in range(len(words)):
                for j in range(i+1, len(words)):
                    sim = self.similarity(words[i], words[j])
                    total += sim
                    count += 1
            return total / count if count > 0 else 0
        
        print(f"\n   类内平均相似度:")
        print(f"     动物类: {avg_similarity(animal_words):.3f}")
        print(f"     水果类: {avg_similarity(fruit_words):.3f}")
        print(f"     交通工具类: {avg_similarity(vehicle_words):.3f}")
        
        # 5. 词向量的维度含义（简化解释）
        print("\n5. 词向量维度的可能含义:")
        print("   虽然我们不知道每个维度的具体含义，但模型学会了:")
        print("   - 某些维度可能表示'动物性'")
        print("   - 某些维度可能表示'可食用性'")
        print("   - 某些维度可能表示'移动速度'")
        print("   - 这些特征是自动学习得到的，不是人工定义的")

# 运行演示
if __name__ == "__main__":
    model = SimpleWordEmbedding()
    model.visualize_relationships()
    
    print("\n" + "=" * 60)
    print("词向量的哲学思考")
    print("=" * 60)
    print("""
为什么离散的单词可以变成连续的向量？
    
1. 语言是连续的
   - 虽然单词是离散的符号，但语义是连续的
   - "猫"和"狗"之间有相似性，也有差异性
   - 向量空间可以表达这种连续关系

2. 分布式表示假设
   - "一个词的含义由其上下文决定"
   - 出现在相似上下文中的词，应该有相似的向量
   - 通过大量文本数据，模型学习到这种规律

3. 向量运算反映语义运算
   - 向量加减 ≈ 语义概念加减
   - 这类似于：图片向量可以表达"戴眼镜的人 = 人 + 眼镜"
   - 词向量空间形成了一个"语义代数系统"

4. 从符号到向量的好处
   - 可以计算相似度（猫 vs 狗 = 0.85）
   - 可以进行数学运算（国王 - 男人 + 女人 = 女王）
   - 可以降维可视化
   - 可以作为神经网络的输入
    """)