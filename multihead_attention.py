import numpy as np

print("=" * 70)
print("多头注意力（Multi-Head Attention）完全指南")
print("=" * 70)

print("\n1. 从单头注意力到多头注意力")
print("""
单头注意力（Single-Head）：
  只有一个"视角"看输入
  可能错过重要信息

多头注意力（Multi-Head）：
  多个"视角"同时看输入
  每个头关注不同方面
  最后综合所有视角
""")

print("\n2. 多头注意力的核心思想")
print("""
关键：将模型维度分成多个"头"

假设：
  d_model = 512（模型总维度）
  num_heads = 8（头数）
  
那么：
  每个头的维度 = d_model / num_heads = 512 / 8 = 64
  
每个头独立计算注意力，关注输入的不同方面。
""")

print("\n3. 多头注意力的计算步骤")
print("""
步骤1：线性变换 + 分头
  输入 x → 线性变换 → 分成 h 个头
  
步骤2：每个头独立计算注意力
  头1：计算注意力1
  头2：计算注意力2
  ...
  头h：计算注意力h
  
步骤3：合并多头
  将所有头的输出拼接
  线性变换得到最终输出
""")

print("\n4. 数学公式详解")
print("""
设：
  h = 头数
  d_model = 模型维度
  d_k = d_model / h（每个头的维度）

多头注意力公式：
  MultiHead(Q, K, V) = Concat(head₁, ..., headₕ)Wᴼ
  
其中每个头：
  headᵢ = Attention(QWᵢᵠ, KWᵢᴷ, VWᵢⱽ)
  
Attention公式：
  Attention(Q, K, V) = softmax(QKᵀ/√d_k)V
""")

print("\n5. 代码实现演示")
print("让我们实现一个简化的多头注意力：")

class MultiHeadAttentionSimple:
    """简化的多头注意力实现"""
    
    def __init__(self, d_model=512, num_heads=8):
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # 检查维度是否能整除
        assert d_model % num_heads == 0, "d_model必须能被num_heads整除"
        
        # 初始化权重（简化，实际中可学习）
        np.random.seed(42)
        self.W_q = np.random.randn(d_model, d_model) * 0.01
        self.W_k = np.random.randn(d_model, d_model) * 0.01
        self.W_v = np.random.randn(d_model, d_model) * 0.01
        self.W_o = np.random.randn(d_model, d_model) * 0.01
        
    def split_heads(self, x, batch_size):
        """将输入分成多个头"""
        # x形状: [batch_size, seq_len, d_model]
        # 分成: [batch_size, seq_len, num_heads, d_k]
        x = x.reshape(batch_size, -1, self.num_heads, self.d_k)
        # 转置: [batch_size, num_heads, seq_len, d_k]
        return x.transpose(0, 2, 1, 3)
    
    def merge_heads(self, x, batch_size):
        """合并多个头"""
        # x形状: [batch_size, num_heads, seq_len, d_k]
        # 转置: [batch_size, seq_len, num_heads, d_k]
        x = x.transpose(0, 2, 1, 3)
        # 合并: [batch_size, seq_len, d_model]
        return x.reshape(batch_size, -1, self.d_model)
    
    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        """缩放点积注意力"""
        # 计算注意力分数
        scores = np.matmul(Q, K.transpose(0, 1, 3, 2)) / np.sqrt(self.d_k)
        
        # 应用掩码（如果有）
        if mask is not None:
            scores = scores + mask * -1e9
        
        # Softmax得到注意力权重
        attention_weights = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attention_weights = attention_weights / np.sum(attention_weights, axis=-1, keepdims=True)
        
        # 加权求和
        output = np.matmul(attention_weights, V)
        
        return output, attention_weights
    
    def forward(self, Q, K, V, mask=None):
        """前向传播"""
        batch_size = Q.shape[0]
        
        print(f"\n输入形状:")
        print(f"  Q: {Q.shape}")
        print(f"  K: {K.shape}")
        print(f"  V: {V.shape}")
        
        # 1. 线性变换
        Q = np.dot(Q, self.W_q)
        K = np.dot(K, self.W_k)
        V = np.dot(V, self.W_v)
        
        print(f"\n线性变换后:")
        print(f"  Q: {Q.shape}")
        print(f"  K: {K.shape}")
        print(f"  V: {V.shape}")
        
        # 2. 分头
        Q = self.split_heads(Q, batch_size)
        K = self.split_heads(K, batch_size)
        V = self.split_heads(V, batch_size)
        
        print(f"\n分头后（每个头独立）:")
        print(f"  Q: {Q.shape}  # [batch, heads, seq_len, d_k]")
        print(f"  K: {K.shape}")
        print(f"  V: {V.shape}")
        print(f"  每个头维度 d_k = {self.d_k}")
        
        # 3. 每个头计算注意力
        attention_output, attention_weights = self.scaled_dot_product_attention(Q, K, V, mask)
        
        print(f"\n注意力计算后:")
        print(f"  每个头输出形状: {attention_output.shape}")
        print(f"  注意力权重形状: {attention_weights.shape}")
        
        # 4. 合并多头
        concatenated = self.merge_heads(attention_output, batch_size)
        
        print(f"\n合并多头后:")
        print(f"  合并形状: {concatenated.shape}")
        
        # 5. 输出线性变换
        output = np.dot(concatenated, self.W_o)
        
        print(f"\n最终输出:")
        print(f"  输出形状: {output.shape}")
        
        return output, attention_weights

print("\n6. 运行示例")
print("让我们创建一个多头注意力实例：")

# 创建多头注意力
d_model = 12  # 简化，方便理解
num_heads = 3
mha = MultiHeadAttentionSimple(d_model=d_model, num_heads=num_heads)

print(f"\n多头注意力配置:")
print(f"  模型维度 d_model = {d_model}")
print(f"  头数 num_heads = {num_heads}")
print(f"  每个头维度 d_k = {d_model // num_heads}")

# 创建模拟输入
batch_size = 2
seq_len = 4

np.random.seed(42)
Q = np.random.randn(batch_size, seq_len, d_model)
K = np.random.randn(batch_size, seq_len, d_model)
V = np.random.randn(batch_size, seq_len, d_model)

print(f"\n模拟输入:")
print(f"  批量大小: {batch_size}")
print(f"  序列长度: {seq_len}")
print(f"  输入示例（第一个batch的第一个词）:")
print(f"    Q[0,0]: {Q[0,0, :3]}...")
print(f"    K[0,0]: {K[0,0, :3]}...")
print(f"    V[0,0]: {V[0,0, :3]}...")

# 运行多头注意力
output, attention_weights = mha.forward(Q, K, V)

print("\n7. 多头注意力的可视化理解")
print("""
输入句子："猫 在 垫子 上"

假设有3个头：

头1（语法头）：
  关注："猫" → "在"（动词）
        "在" → "垫子"（宾语）
        "垫子" → "上"（介词）

头2（语义头）：
  关注："猫" → "动物"
        "垫子" → "家具"
        "在...上" → "位置关系"

头3（指代头）：
  关注：整个句子的连贯性
        没有指代歧义

每个头生成不同的注意力模式，最后合并。
""")

print("\n8. 为什么需要多头？")
print("""
单头注意力的问题：

1. 信息瓶颈
   一个头要关注所有方面，可能力不从心

2. 局部最优
   可能只关注最明显的模式，忽略细微模式

3. 表示能力有限
   单个注意力矩阵的表示能力有限

多头注意力的优势：

1. 并行处理
   多个头同时计算，效率高

2. 专业化
   每个头可以专门关注特定方面

3. 鲁棒性
   即使某个头出错，其他头可以弥补

4. 表示丰富
   综合多个视角，表示更丰富
""")

print("\n9. 多头注意力的实际例子")
print("""
例子：翻译 "The cat sat on the mat"

头1（语法头）：
  "The" → "cat"（限定词-名词）
  "cat" → "sat"（主语-动词）
  "sat" → "on"（动词-介词）
  "on" → "the mat"（介词-宾语）

头2（语义头）：
  "cat" → "animal"
  "mat" → "furniture"
  "sat on" → "position"

头3（指代头）：
  "the" → 指代特定的猫和垫子
  确保一致性

头4（位置头）：
  关注词序信息
  确保翻译保持正确顺序

所有头的输出合并，得到综合理解。
""")

print("\n10. 多头注意力的参数分析")
print("""
关键参数选择：

1. 头数选择
   - 太少：表示能力不足
   - 太多：计算开销大，可能过拟合
   - 经验：d_model=512时，h=8效果最好

2. 头维度
   d_k = d_model / h
   - 太小：每个头表示能力有限
   - 太大：计算复杂度高

3. 常见配置：
   | 模型 | d_model | num_heads | d_k |
   |------|---------|-----------|-----|
   | 原始Transformer | 512 | 8 | 64 |
   | BERT-base | 768 | 12 | 64 |
   | BERT-large | 1024 | 16 | 64 |
   | GPT-3 | 12288 | 96 | 128 |
""")

print("\n11. 多头注意力的计算复杂度")
print("""
计算复杂度分析：

单头注意力：
  时间复杂度: O(n²·d)  # n=序列长度，d=维度
  空间复杂度: O(n² + n·d)

多头注意力：
  时间复杂度: O(n²·d)  # 与单头相同（并行计算）
  空间复杂度: O(h·n² + n·d)  # 多了h倍注意力矩阵

虽然空间复杂度增加，但：
  1. 并行计算，时间不增加
  2. 表示能力大幅提升
  3. 实际效果证明值得
""")

print("\n12. 多头注意力的变体")
print("""
1. 跨注意力（Cross-Attention）
   - 编码器-解码器注意力
   - Q来自解码器，K,V来自编码器

2. 稀疏注意力（Sparse Attention）
   - 只计算部分位置的注意力
   - 降低计算复杂度

3. 局部注意力（Local Attention）
   - 只关注局部窗口
   - 适合长序列

4. 线性注意力（Linear Attention）
   - 将softmax线性化
   - 降低计算复杂度
""")

print("\n13. 多头注意力在Transformer中的位置")
print("""
Transformer编码器层：

输入 → 层归一化 → 多头自注意力 → 残差连接 → 
层归一化 → 前馈网络 → 残差连接 → 输出

关键：多头注意力是Transformer的核心组件
没有它，Transformer就退化成普通前馈网络
""")

print("\n14. 实验证据")
print("""
在原始Transformer论文中：

英德翻译任务对比：
  - 单头注意力：BLEU 25.8
  - 4头注意力：BLEU 27.3
  - 8头注意力：BLEU 28.4（最佳）
  - 16头注意力：BLEU 28.1（略有下降）

结论：多头确实比单头好，但头数不是越多越好
""")

print("\n15. 多头注意力的局限性")
print("""
1. 计算复杂度高
   O(n²)复杂度，处理长序列困难

2. 内存消耗大
   需要存储h个n×n的注意力矩阵

3. 可解释性差
   每个头具体关注什么，难以解释

4. 超参数敏感
   头数需要仔细调优
""")

print("\n16. 现代改进")
print("""
针对局限性的改进：

1. 高效注意力
   - Reformer：局部敏感哈希
   - Linformer：低秩近似
   - Performer：随机特征映射

2. 稀疏注意力
   - Longformer：滑动窗口+全局注意力
   - BigBird：随机+局部+全局

3. 多头压缩
   - 共享部分参数
   - 动态头数
""")

print("\n" + "=" * 70)
print("总结：多头注意力的核心价值")
print("=" * 70)
print("""
多头注意力的三大价值：

1. **表示多样性**
   - 多个头关注不同方面
   - 综合得到更丰富的表示
   - 类似"委员会决策"，比单个人更准确

2. **并行效率**
   - 多个头可以并行计算
   - 充分利用GPU并行能力
   - 计算时间不增加

3. **模型容量**
   - 增加模型表达能力
   - 不显著增加参数（主要是线性变换）
   - 性价比高的容量增加方式

关键理解：
  多头注意力不是简单的"重复计算"
  而是"多视角协同理解"
  
就像团队合作：
  不是每个人做同样的事
  而是每个人负责不同方面
  最后综合得到全面理解
""")

print("\n🎯 记住多头注意力的核心：")
print("1. 分头：d_model → h × d_k")
print("2. 并行：每个头独立计算注意力")
print("3. 合并：拼接所有头，线性变换")
print("4. 价值：多视角理解，表示更丰富")