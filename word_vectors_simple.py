import numpy as np

def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

print("=" * 60)
print("词向量（Word Embedding）原理详解")
print("=" * 60)

print("\n1. 为什么需要词向量？")
print("""
传统方法的问题：
- One-Hot编码：[1,0,0,0,...], [0,1,0,0,...]
  - 维度太高（词表多大，向量就多长）
  - 所有词距离相等，无法表达语义关系
  - 无法进行数学运算

词向量的优势：
- 低维稠密向量：[0.2, -0.1, 0.8, ..., 0.3]
  - 维度固定（如300维）
  - 语义相似的词向量也相似
  - 可以进行数学运算
""")

print("\n2. 核心思想：分布式假设")
print("""
"一个词的含义由其上下文决定"

例子：
句子1：我养了一只可爱的[猫]
句子2：我养了一只可爱的[狗]
句子3：我买了一条新鲜的[鱼]

分析：
- "猫"和"狗"出现在相似的上下文中 → 向量应该相似
- "鱼"出现在不同的上下文中 → 向量应该不同
- 通过大量文本，模型学习到这种规律
""")

print("\n3. 词向量学习过程（Word2Vec为例）")
print("""
训练数据：大量文本
目标：让相似上下文的词有相似向量

方法1：CBOW（连续词袋）
输入：["我", "养", "了", "一只", "可爱的"]（上下文）
输出：预测中心词 ["猫"]

方法2：Skip-Gram
输入：中心词 ["猫"]
输出：预测上下文词 ["我", "养", "了", "一只", "可爱的"]

训练后得到：
- 每个词对应一个固定向量
- 向量空间中的距离反映语义距离
""")

print("\n4. 词向量的神奇特性")
print("""
特性1：语义相似性
  similarity("猫", "狗") ≈ 0.85  # 很相似
  similarity("猫", "鱼") ≈ 0.45  # 有点相似  
  similarity("猫", "电脑") ≈ 0.12 # 不相似

特性2：类比关系
  国王 - 男人 + 女人 ≈ 女王
  中国 - 北京 + 东京 ≈ 日本
  快速 - 慢 + 好 ≈ 优秀

特性3：向量运算反映语义运算
  vec("巴黎") - vec("法国") + vec("德国") ≈ vec("柏林")
""")

print("\n5. 实际向量示例")
print("让我们创建一些模拟的词向量：")

# 创建模拟词向量
np.random.seed(42)

# 定义一些词
words = ["猫", "狗", "老虎", "苹果", "香蕉", "汽车", "飞机"]

# 创建有语义关系的向量
# 动物类向量（相似）
cat_vec = np.array([0.8, 0.2, -0.1, 0.5, 0.3])
dog_vec = np.array([0.7, 0.3, -0.2, 0.6, 0.2])  # 与猫相似
tiger_vec = np.array([0.9, 0.1, 0.1, 0.7, 0.4])  # 与猫相似

# 水果类向量（相似）
apple_vec = np.array([-0.2, 0.9, 0.3, -0.1, 0.7])
banana_vec = np.array([-0.3, 0.8, 0.4, -0.2, 0.6])  # 与苹果相似

# 交通工具类向量
car_vec = np.array([0.1, -0.3, 0.8, 0.4, -0.2])
plane_vec = np.array([0.2, -0.2, 0.9, 0.5, -0.1])  # 与汽车相似

# 计算相似度
print("\n词向量相似度计算：")
print(f"猫 vs 狗: {cosine_similarity(cat_vec, dog_vec):.3f}")
print(f"猫 vs 老虎: {cosine_similarity(cat_vec, tiger_vec):.3f}")
print(f"苹果 vs 香蕉: {cosine_similarity(apple_vec, banana_vec):.3f}")
print(f"汽车 vs 飞机: {cosine_similarity(car_vec, plane_vec):.3f}")
print(f"猫 vs 苹果: {cosine_similarity(cat_vec, apple_vec):.3f}")
print(f"猫 vs 汽车: {cosine_similarity(cat_vec, car_vec):.3f}")

print("\n6. 类比关系演示")
print("让我们模拟：国王 - 男人 + 女人 ≈ 女王")

# 创建类比向量
king_vec = np.array([0.5, 0.3, 0.2, 0.7, 0.1])
man_vec = np.array([0.3, 0.2, 0.1, 0.5, 0.1])
woman_vec = np.array([0.4, 0.3, 0.2, 0.6, 0.2])

# 计算：国王 - 男人 + 女人
queen_calc = king_vec - man_vec + woman_vec

# 假设的女王向量（实际应该接近计算结果）
queen_real = np.array([0.6, 0.4, 0.3, 0.8, 0.2])

print(f"\n计算过程：")
print(f"  国王向量: {king_vec}")
print(f"  男人向量: {man_vec}")
print(f"  女人向量: {woman_vec}")
print(f"  计算结果: {queen_calc}")
print(f"  实际女王向量: {queen_real}")
print(f"  相似度: {cosine_similarity(queen_calc, queen_real):.3f}")

print("\n7. 词向量在Transformer中的应用")
print("""
在Transformer中：
1. 输入层：单词 → 词向量
   "我" → [0.1, -0.2, 0.3, ...]
   "爱" → [0.4, 0.1, -0.1, ...]
   "你" → [-0.1, 0.3, 0.2, ...]

2. 加上位置编码
   词向量 + 位置向量

3. 送入Transformer层处理
   通过注意力机制，结合上下文信息

4. 输出：更新后的向量表示
   包含了上下文信息的词向量
""")

print("\n8. 从符号到向量的哲学意义")
print("""
这是AI理解语言的关键突破：

1. 符号接地问题（Symbol Grounding）
   - 传统AI：符号是空洞的，没有意义
   - 词向量：符号通过向量连接到现实世界的统计规律

2. 连续表示的优势
   - 可以计算相似度、距离、方向
   - 可以进行梯度下降优化
   - 适合神经网络处理

3. 分布式语义
   - 一个概念分散在多个维度中
   - 每个维度可能对应某种抽象特征
   - 这些特征是自动学习得到的

4. 多语言通用性
   - 不同语言的相似概念有相似向量
   - 便于机器翻译、跨语言理解
""")

print("\n" + "=" * 60)
print("总结：词向量是AI理解语言的基础")
print("=" * 60)
print("""
1. 将离散符号转换为连续向量
2. 向量空间中的距离反映语义距离  
3. 通过大量文本数据自动学习得到
4. 支持数学运算和相似度计算
5. 是Transformer等现代NLP模型的基础

词向量让计算机从"认识字"进步到"理解意思"。
""")