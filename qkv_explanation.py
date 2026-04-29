import numpy as np

print("=" * 70)
print("Q、K、V 完全解析：注意力机制的核心")
print("=" * 70)

print("\n1. 注意力机制的直观理解")
print("""
注意力就像"信息检索系统"：

你有：一堆文档（输入序列）
你想：找到与查询最相关的文档

Q：你的查询（你想找什么）
K：文档的关键词（每个文档的特征）
V：文档的内容（实际返回的信息）
""")

print("\n2. Q、K、V 的具体含义")
print("""
在Transformer中，对于输入序列的每个词：

Q（Query，查询向量）：
  - 代表：这个词"想要关注什么"
  - 作用：主动查询其他词的信息
  - 比喻：举起手提问的学生

K（Key，键向量）：
  - 代表：这个词"能被关注什么"  
  - 作用：被其他词查询时的匹配依据
  - 比喻：学生胸前的名牌

V（Value，值向量）：
  - 代表：这个词"实际提供什么信息"
  - 作用：当被关注时，实际传递的信息
  - 比喻：学生脑子里真正的知识
""")

print("\n3. 注意力计算过程")
print("""
注意力公式：
  Attention(Q, K, V) = softmax(Q·Kᵀ/√d_k) · V

步骤分解：
  1. Q·Kᵀ：计算查询与键的相似度
      - 每个Q与所有K计算点积
      - 得到注意力分数矩阵
  
  2. softmax(分数/√d_k)：归一化为概率分布
      - 除以√d_k稳定梯度
      - softmax得到注意力权重（和为1）
  
  3. 权重·V：加权求和得到输出
      - 用注意力权重对V加权
      - 得到每个查询的最终表示
""")

print("\n4. 实际例子演示")
print("让我们用具体例子理解：")

def simple_attention_example():
    """简单的注意力示例"""
    print("\n句子：'猫 追 老鼠'")
    print("我们想计算'追'的注意力输出")
    
    # 模拟词向量（简化）
    words = ["猫", "追", "老鼠"]
    
    # 假设的词向量（3维）
    embeddings = {
        "猫": np.array([0.8, 0.2, 0.1]),    # 动物特征强
        "追": np.array([0.1, 0.9, 0.3]),    # 动作特征强  
        "老鼠": np.array([0.7, 0.3, 0.2])   # 动物特征强
    }
    
    print(f"\n词向量：")
    for word, vec in embeddings.items():
        print(f"  '{word}': {vec}")
    
    # 注意力计算：关注"追"
    print(f"\n计算'追'的注意力（自注意力）：")
    
    # Q = "追"的查询向量（想知道：谁在追？追什么？）
    Q = embeddings["追"].reshape(1, -1)  # 形状: [1, 3]
    
    # K = 所有词的键向量（能被查询的特征）
    K = np.array([embeddings["猫"], embeddings["追"], embeddings["老鼠"]])  # [3, 3]
    
    # V = 所有词的值向量（实际包含的信息）
    V = K.copy()  # 自注意力中，V通常与K相同
    
    print(f"\nQ（'追'的查询）: {Q[0]}")
    print(f"K（所有词的键）:")
    for i, word in enumerate(words):
        print(f"  '{word}': {K[i]}")
    
    # 计算注意力分数
    scores = np.dot(Q, K.T)  # Q·Kᵀ
    print(f"\n1. 计算注意力分数 Q·Kᵀ:")
    print(f"  分数: {scores[0]}")
    
    # 缩放
    d_k = Q.shape[1]
    scaled_scores = scores / np.sqrt(d_k)
    print(f"\n2. 缩放分数 /√d_k (d_k={d_k}):")
    print(f"  缩放后: {scaled_scores[0]}")
    
    # Softmax得到注意力权重
    attention_weights = np.exp(scaled_scores - np.max(scaled_scores))
    attention_weights = attention_weights / np.sum(attention_weights)
    print(f"\n3. Softmax得到注意力权重:")
    print(f"  权重: {attention_weights[0]}")
    print(f"  权重和: {np.sum(attention_weights[0]):.6f} (应为1)")
    
    # 加权求和
    output = np.dot(attention_weights, V)
    print(f"\n4. 加权求和 权重·V:")
    print(f"  最终输出: {output[0]}")
    
    print(f"\n💡 分析：")
    print(f"  '追'最关注'猫'（权重最高）")
    print(f"  因为'猫追'是合理的动作关系")
    print(f"  输出向量融合了'猫'和'老鼠'的特征")
    
    return Q, K, V, attention_weights, output

Q, K, V, weights, output = simple_attention_example()

print("\n5. Q、K、V 的线性变换")
print("""
在实际Transformer中，Q、K、V不是直接使用词向量，
而是经过线性变换：

  Q = X·W_q  # 查询变换
  K = X·W_k  # 键变换  
  V = X·W_v  # 值变换

其中：
  X: 输入词向量
  W_q, W_k, W_v: 可学习的权重矩阵

为什么需要变换？
  1. 增加模型容量
  2. 让Q、K、V学习不同的表示
  3. 提高注意力机制的灵活性
""")

print("\n6. 不同类型的注意力")
print("""
1. 自注意力（Self-Attention）
   Q、K、V都来自同一个输入序列
   用于理解序列内部关系
   
   例子：理解句子内部语法关系
     "猫追老鼠"中，"追"需要关注"猫"和"老鼠"

2. 交叉注意力（Cross-Attention）
   Q来自一个序列，K、V来自另一个序列
   用于序列间信息传递
   
   例子：机器翻译
     解码器（目标语言）查询编码器（源语言）
     Q: 英文词"cat"的查询
     K,V: 中文词"猫"的键和值

3. 编码器-解码器注意力
   解码器的Q关注编码器的K、V
   用于生成时参考源信息
""")

print("\n7. Q、K、V 的维度关系")
print("""
设：
  batch_size = B（批量大小）
  seq_len = N（序列长度）
  d_model = D（模型维度）
  num_heads = H（头数）
  d_k = D/H（每个头维度）

那么：
  Q形状: [B, N, D] → 线性变换 → [B, N, D] → 分头 → [B, H, N, d_k]
  K形状: [B, N, D] → 线性变换 → [B, N, D] → 分头 → [B, H, N, d_k]
  V形状: [B, N, D] → 线性变换 → [B, N, D] → 分头 → [B, H, N, d_k]

注意力计算：
  Q·Kᵀ: [B, H, N, d_k] × [B, H, d_k, N] → [B, H, N, N]
  权重·V: [B, H, N, N] × [B, H, N, d_k] → [B, H, N, d_k]
""")

print("\n8. Q、K、V 的物理意义")
print("""
Q（查询）的物理意义：
  - 代表"主动关注"的能力
  - 决定关注哪些其他位置
  - 编码了"我想知道什么"

K（键）的物理意义：
  - 代表"被关注"的特征
  - 决定如何被其他位置关注
  - 编码了"我能提供什么线索"

V（值）的物理意义：
  - 代表"实际传递"的信息
  - 当被关注时，实际传递的内容
  - 编码了"我真正包含的信息"

关键：Q和K决定"关注谁"，V决定"关注后得到什么"
""")

print("\n9. 实际应用中的Q、K、V")
print("""
例子1：机器翻译
  输入："The cat sat on the mat"
  
  Q（解码器查询）：当前生成的词想知道什么？
    生成"猫"时，Q想知道：主语是什么？动词是什么？
  
  K（编码器键）：源语言词的特征
    "The": 限定词特征
    "cat": 动物名词特征
    "sat": 过去时动词特征
    
  V（编码器值）：源语言词的实际信息
    当关注"cat"时，得到"猫"的语义信息

例子2：文本分类
  输入："这部电影非常精彩，演员表演出色"
  
  Q（每个词的查询）：这个词对分类的贡献？
    "精彩"的Q：寻找情感相关的词
    
  K（每个词的键）：能被用于分类的特征
    "电影"的K：类型特征
    "精彩"的K：情感特征
    
  V（每个词的值）：实际的情感强度信息
""")

print("\n10. Q、K、V 的可视化理解")
print("""
想象一个社交网络：

Q：你主动关注谁？
  - 你想了解编程，所以关注程序员
  - 你想了解设计，所以关注设计师

K：你容易被谁关注？
  - 如果你是专家，别人会关注你获取知识
  - 如果你是名人，别人会关注你获取动态

V：当别人关注你时，看到什么？
  - 你的专业知识（技术博客）
  - 你的生活动态（社交分享）

注意力机制：根据兴趣(Q)找到相关人(K)，获取他们的信息(V)
""")

print("\n11. 多头注意力中的Q、K、V")
print("""
在多头注意力中，每个头有自己的Q、K、V：

头1（语法头）：
  Q：语法相关的查询（主谓关系？动宾关系？）
  K：语法特征（名词？动词？形容词？）
  V：语法信息（词性、句法角色）

头2（语义头）：
  Q：语义相关的查询（同义词？反义词？）
  K：语义特征（词义、概念）
  V：语义信息（词义表示）

头3（指代头）：
  Q：指代相关的查询（指代谁？被谁指代？）
  K：指代特征（代词、名词）
  V：指代信息（指代关系）

每个头从不同角度理解输入，最后合并。
""")

print("\n12. 为什么Q、K、V要分开？")
print("""
为什么不直接用同一个向量？

1. 功能分离原则
   - 查询功能：主动寻找信息
   - 匹配功能：被寻找时的特征
   - 内容功能：实际包含的信息
   
   分开让网络学习更专门化的表示

2. 增加模型容量
   三个独立的变换矩阵增加参数
   提高模型表达能力

3. 灵活性
   可以设计不同的注意力变体
   如：K和V可以不同（非对称注意力）

实验证明：分开的Q、K、V比共享的效果好很多。
""")

print("\n13. Q、K、V 的训练过程")
print("""
Q、K、V的权重矩阵通过训练学习：

初始化：随机小值
训练：通过反向传播调整

学习目标：
  W_q：学习如何生成有效的查询
  W_k：学习如何生成可匹配的键
  W_v：学习如何生成有价值的信息

最终：Q、K、V学会协作，实现有效的信息检索。
""")

print("\n14. 常见误解澄清")
print("""
误解1：Q、K、V是三个不同的输入
  正确：它们都来自同一个输入，但经过不同变换

误解2：Q是问题，K是答案
  正确：Q和K都是特征表示，用于计算相似度

误解3：V必须和K相同
  正确：在自注意力中通常相同，但可以不同

误解4：Q、K、V的顺序固定
  正确：在交叉注意力中，Q和K、V可以来自不同序列
""")

print("\n15. 代码实现示例")
print("""
PyTorch中的Q、K、V计算：

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Q、K、V的线性变换层
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # 1. 线性变换得到Q、K、V
        Q = self.W_q(query)  # [B, N, D]
        K = self.W_k(key)    # [B, N, D]
        V = self.W_v(value)  # [B, N, D]
        
        # 2. 分头
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # 3. 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        # ... 后续计算
```
""")

print("\n" + "=" * 70)
print("总结：Q、K、V的核心理解")
print("=" * 70)
print("""
三个关键词记住：

1. **Q（Query）**：我要什么？
   - 主动查询者
   - 决定关注方向
   - 编码查询意图

2. **K（Key）**：我有什么特征？
   - 被查询的对象
   - 匹配查询的依据
   - 编码可被关注的特征

3. **V（Value）**：我实际给什么？
   - 信息提供者
   - 实际传递的内容
   - 编码真实信息

注意力机制的工作流程：
  1. 用Q寻找相关的K（计算相似度）
  2. 根据相似度决定关注程度（softmax）
  3. 用关注程度加权求和V得到输出

类比总结：
  Q：你的搜索关键词
  K：网页的元标签（关键词）
  V：网页的实际内容
  
  搜索引擎：用Q匹配K，返回相关的V
  注意力：用Q匹配K，加权组合V
""")

print("\n🎯 一句话记住：")
print("Q决定'找谁'，K决定'被谁找到'，V决定'找到后得到什么'。")