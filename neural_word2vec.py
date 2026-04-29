import numpy as np

print("=" * 70)
print("神经网络如何将词转换为词向量 - 逐步详解")
print("=" * 70)

print("\n1. 准备工作：构建词表")
print("""
假设我们有3个词的微型语料：
["猫", "狗", "鱼", "猫", "狗", "吃", "鱼"]

构建词表（按频率排序）：
  猫: 0, 狗: 1, 鱼: 2, 吃: 3
词表大小 V = 4
""")

V = 4  # 词表大小
d = 3  # 词向量维度（简化，实际300维）

print(f"\n词表大小 V = {V}")
print(f"词向量维度 d = {d}")

print("\n2. 第一步：词 → One-Hot 向量")
print("""
One-Hot 编码：
  "猫" = [1, 0, 0, 0]
  "狗" = [0, 1, 0, 0]
  "鱼" = [0, 0, 1, 0]
  "吃" = [0, 0, 0, 1]
  
每个词是 V 维的稀疏向量，只有1个位置是1
""")

# 创建 One-Hot 编码
one_hot = {
    "猫": np.array([1, 0, 0, 0]),
    "狗": np.array([0, 1, 0, 0]),
    "鱼": np.array([0, 0, 1, 0]),
    "吃": np.array([0, 0, 0, 1])
}

print("\n3. 第二步：初始化词向量矩阵 W")
print(f"""
创建词向量矩阵 W（形状：V×d = {V}×{d}）
每一行对应一个词的向量
初始化为随机小值
""")

np.random.seed(42)
W = np.random.randn(V, d) * 0.1  # 词向量矩阵

print(f"词向量矩阵 W 形状: {W.shape}")
print(f"W = \n{W}")
print(f"\n每一行是一个词的初始向量：")
for i, word in enumerate(["猫", "狗", "鱼", "吃"]):
    print(f"  {word}: {W[i]}")

print("\n4. 第三步：前向传播 - 获取词向量")
print("""
前向传播公式：
  词向量 = Wᵀ · One-Hot(词)
  
实际上更简单：
  因为 One-Hot 只有1个位置是1
  所以词向量 = W[词的索引]
  
就是直接取 W 矩阵的对应行！
""")

def get_word_vector(word, W):
    """获取词向量（前向传播）"""
    idx = list(one_hot.keys()).index(word)
    return W[idx]  # 直接取对应行

print("\n示例：获取'猫'的词向量")
cat_vec = get_word_vector("猫", W)
print(f"  '猫'的词向量: {cat_vec}")

print("\n5. 第四步：训练数据准备")
print("""
从文本生成训练对（Skip-Gram，窗口大小=1）：

句子："猫 吃 鱼"
中心词="吃"，上下文=["猫", "鱼"]

训练对：
  (中心词="吃", 正样本="猫")
  (中心词="吃", 正样本="鱼")
  
负样本：随机选择其他词（如"狗"）
""")

print("\n6. 第五步：神经网络完整前向传播")
print("""
输入：中心词 w（如"吃"）
步骤：
  1. One-Hot(w) → [0,0,0,1]
  2. 词向量 h = W[w的索引] → [w₁, w₂, w₃]
  3. 输出层：h · Cᵀ （C是上下文向量矩阵）
  4. Softmax：得到每个词作为上下文的概率
""")

# 初始化上下文矩阵 C（形状：V×d）
C = np.random.randn(V, d) * 0.1

def forward_pass(center_word, context_word, W, C):
    """完整前向传播"""
    # 1. 获取中心词向量
    center_idx = list(one_hot.keys()).index(center_word)
    h = W[center_idx]  # 中心词向量
    
    # 2. 计算输出分数
    scores = np.dot(C, h)  # C·h，得到每个词的分数
    
    # 3. Softmax 得到概率
    exp_scores = np.exp(scores - np.max(scores))
    probs = exp_scores / np.sum(exp_scores)
    
    # 4. 目标词的概率
    target_idx = list(one_hot.keys()).index(context_word)
    target_prob = probs[target_idx]
    
    return h, scores, probs, target_prob

print("\n示例：中心词='吃'，上下文='猫'")
h, scores, probs, target_prob = forward_pass("吃", "猫", W, C)
print(f"  中心词向量 h: {h}")
print(f"  所有词分数: {scores}")
print(f"  所有词概率: {probs}")
print(f"  '猫'的概率: {target_prob:.4f}")

print("\n7. 第六步：损失函数计算")
print("""
使用负对数似然损失：
  Loss = -log(P(上下文词|中心词))
  
对于负采样：
  Loss = -log(σ(h·c⁺)) - Σ log(σ(-h·c⁻))
  其中：σ是sigmoid函数
        h是中心词向量
        c⁺是正样本上下文向量
        c⁻是负样本上下文向量
""")

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def calculate_loss(h, context_vec, negative_vecs):
    """计算负采样损失"""
    # 正样本损失
    pos_score = np.dot(h, context_vec)
    pos_loss = -np.log(sigmoid(pos_score))
    
    # 负样本损失
    neg_loss = 0
    for neg_vec in negative_vecs:
        neg_score = np.dot(h, neg_vec)
        neg_loss += -np.log(sigmoid(-neg_score))
    
    return pos_loss + neg_loss

print("\n8. 第七步：反向传播 - 更新词向量")
print("""
关键：通过梯度下降更新 W 和 C

梯度公式（简化）：
  ∂Loss/∂h = (σ(h·c) - 标签) · c
  
更新规则：
  h_new = h_old - η · ∂Loss/∂h
  
其中 η 是学习率
""")

def update_vectors(center_word, context_word, negative_words, W, C, learning_rate=0.01):
    """更新词向量（简化版反向传播）"""
    center_idx = list(one_hot.keys()).index(center_word)
    context_idx = list(one_hot.keys()).index(context_word)
    
    h = W[center_idx]  # 中心词向量
    c_pos = C[context_idx]  # 正样本上下文向量
    
    # 计算梯度
    pos_score = np.dot(h, c_pos)
    pos_grad = (sigmoid(pos_score) - 1) * c_pos
    
    # 负样本梯度
    neg_grad = np.zeros_like(h)
    for neg_word in negative_words:
        neg_idx = list(one_hot.keys()).index(neg_word)
        c_neg = C[neg_idx]
        neg_score = np.dot(h, c_neg)
        neg_grad += sigmoid(neg_score) * c_neg
    
    # 总梯度
    total_grad = pos_grad + neg_grad
    
    # 更新中心词向量
    W[center_idx] -= learning_rate * total_grad
    
    # 更新上下文向量（简化，实际更复杂）
    C[context_idx] -= learning_rate * (sigmoid(pos_score) - 1) * h
    for neg_word in negative_words:
        neg_idx = list(one_hot.keys()).index(neg_word)
        neg_score = np.dot(h, C[neg_idx])
        C[neg_idx] -= learning_rate * sigmoid(neg_score) * h
    
    return W, C

print("\n9. 第八步：训练过程可视化")
print("""
迭代训练：

初始化：W = 随机小值
        所有词向量随机分布

第1轮训练：
  输入：("吃", "猫"), 负样本=["狗"]
  更新：让"吃"的向量更接近"猫"，远离"狗"

第2轮训练：
  输入：("吃", "鱼"), 负样本=["猫"]
  更新：让"吃"的向量更接近"鱼"，远离"猫"

经过大量训练后：
  - 经常一起出现的词，向量相似
  - 不常一起出现的词，向量不相似
  - W 矩阵的每一行就是学习到的词向量！
""")

print("\n10. 数学原理深度解析")
print("""
为什么这样能学到语义？

目标函数：最大化 log P(上下文|中心词)
        = 最大化 Σ log σ(h·c⁺) + Σ log σ(-h·c⁻)

这等价于：
  让中心词向量与正样本上下文向量点积大
  让中心词向量与负样本上下文向量点积小

经过训练：
  如果"猫"和"狗"经常出现在相似上下文
  那么它们的向量 h_cat 和 h_dog 会：
    - 与相似的上下文向量点积都大
    - 逐渐变得相似
    
最终：语义相似的词 → 向量相似
""")

print("\n11. 词向量矩阵 W 的物理意义")
print(f"""
W 矩阵（{V}×{d}）：
  每一行：一个词的向量表示
  每一列：一个"语义特征维度"

训练后，W 的几何意义：
  - 行方向：不同词的向量
  - 列方向：不同语义特征
  
例如（假设3个维度）：
  维度1：动物性（猫、狗、鱼值高，吃值低）
  维度2：动作性（吃值高，猫狗鱼值低）
  维度3：水生性（鱼值高，猫狗值低）
  
这些特征不是人工定义的，是自动学习的！
""")

print("\n12. 完整训练示例（简化）")
print("让我们模拟几轮训练：")

# 重新初始化
np.random.seed(42)
W = np.random.randn(V, d) * 0.1
C = np.random.randn(V, d) * 0.1

print(f"\n初始词向量：")
for i, word in enumerate(["猫", "狗", "鱼", "吃"]):
    print(f"  {word}: {W[i]}")

# 模拟几轮训练
training_pairs = [
    ("吃", "猫", ["狗"]),  # 中心词="吃"，正样本="猫"，负样本=["狗"]
    ("吃", "鱼", ["猫"]),  # 中心词="吃"，正样本="鱼"，负样本=["猫"]
    ("猫", "吃", ["鱼"]),  # 中心词="猫"，正样本="吃"，负样本=["鱼"]
]

print(f"\n训练过程：")
for epoch, (center, context, negs) in enumerate(training_pairs, 1):
    print(f"\n第{epoch}轮：中心词='{center}'，上下文='{context}'，负样本={negs}")
    
    # 计算初始相似度
    center_vec = get_word_vector(center, W)
    context_vec = get_word_vector(context, W)
    sim_before = np.dot(center_vec, context_vec) / (
        np.linalg.norm(center_vec) * np.linalg.norm(context_vec)
    )
    
    # 更新
    W, C = update_vectors(center, context, negs, W, C, learning_rate=0.1)
    
    # 计算更新后相似度
    center_vec_new = get_word_vector(center, W)
    context_vec_new = get_word_vector(context, W)
    sim_after = np.dot(center_vec_new, context_vec_new) / (
        np.linalg.norm(center_vec_new) * np.linalg.norm(context_vec_new)
    )
    
    print(f"  更新前相似度: {sim_before:.3f}")
    print(f"  更新后相似度: {sim_after:.3f}")
    print(f"  变化: {sim_after - sim_before:+.3f}")

print(f"\n训练后词向量：")
for i, word in enumerate(["猫", "狗", "鱼", "吃"]):
    print(f"  {word}: {W[i]}")

print("\n13. 从神经网络权重到语义空间")
print("""
神奇之处：

训练前：W 是随机数，没有意义
训练后：W 编码了语义信息

为什么？
因为训练目标让 W 能够：
  1. 预测上下文词
  2. 区分正负样本
  
要完成这个任务，W 必须：
  - 让语义相似的词有相似向量
  - 让语义不同的词有不同向量
  
最终：W 的每一行成为一个词的"语义指纹"
""")

print("\n" + "=" * 70)
print("总结：神经网络如何学习词向量")
print("=" * 70)
print("""
四步转换：

1. 符号 → 索引
   "猫" → 0, "狗" → 1, ...

2. 索引 → One-Hot
   0 → [1,0,0,...], 1 → [0,1,0,...]

3. One-Hot → 矩阵查找 → 词向量
   [1,0,0,...] · W = W[0,:] = 猫的词向量

4. 训练更新 W
   通过预测上下文任务
   反向传播调整 W
   让 W 编码语义信息

关键洞见：
  - 词向量不是"计算"出来的，是"学习"出来的
  - W 矩阵是神经网络为了完成任务而学习的副产品
  - 语义信息被编码在权重矩阵的几何结构中
  
这就是神经网络将词转换为词向量的魔法！
""")