import numpy as np
import matplotlib.pyplot as plt

print("=" * 70)
print("位置嵌入（Positional Embedding）详解")
print("=" * 70)

print("\n1. 为什么需要位置嵌入？")
print("""
Transformer的问题：注意力机制是排列不变的（permutation invariant）

例子：
句子1："猫 追 老鼠" → 注意力看到 {猫, 追, 老鼠}
句子2："老鼠 追 猫" → 注意力看到 {老鼠, 追, 猫}

没有位置信息时，这两个句子对模型来说是一样的！
但实际上语义完全不同。

解决方案：给每个位置添加唯一标识
""")

print("\n2. 正弦余弦位置编码（Transformer原创）")
print("""
公式：
  PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
  PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
  
其中：
  pos: 位置（0, 1, 2, ...）
  i: 维度索引（0, 1, 2, ..., d_model/2-1）
  d_model: 模型维度（如512）
""")

def sinusoidal_positional_encoding(seq_len, d_model):
    """生成正弦余弦位置编码"""
    pe = np.zeros((seq_len, d_model))
    
    for pos in range(seq_len):
        for i in range(0, d_model, 2):
            pe[pos, i] = np.sin(pos / (10000 ** (i / d_model)))
            if i + 1 < d_model:
                pe[pos, i + 1] = np.cos(pos / (10000 ** ((i) / d_model)))
    
    return pe

# 生成示例
seq_len = 10
d_model = 16
pe = sinusoidal_positional_encoding(seq_len, d_model)

print(f"\n位置编码矩阵形状：{pe.shape}（{seq_len}个位置 × {d_model}维）")
print(f"\n前3个位置的前6维：")
for pos in range(3):
    print(f"  位置{pos}: {pe[pos, :6]}...")

print("\n3. 正弦余弦编码的数学性质")
print("""
神奇性质1：相对位置可计算
  对于固定偏移 k，存在线性变换 M_k 使得：
    PE(pos + k) = M_k · PE(pos)
  
  这意味着模型可以学会"位置1 + 位置2 = 位置3"的关系

神奇性质2：唯一性
  每个位置有唯一编码，不会重复

神奇性质3：有界性
  值在[-1, 1]之间，与词向量尺度匹配
""")

print("\n4. 可视化位置编码")
print("让我们看看位置编码的样子：")

# 生成更大的位置编码用于可视化
seq_len_viz = 50
d_model_viz = 64
pe_viz = sinusoidal_positional_encoding(seq_len_viz, d_model_viz)

print(f"\n生成 {seq_len_viz}×{d_model_viz} 的位置编码矩阵")
print("前几个位置的编码模式：")

# 打印前几个位置的前几个维度
print("\n位置0-4，维度0-7：")
for pos in range(5):
    row = " ".join([f"{pe_viz[pos, i]:6.3f}" for i in range(8)])
    print(f"  位置{pos}: {row}...")

print("\n5. 位置编码与词嵌入的结合")
print("""
在Transformer中：
  最终输入 = 词嵌入 + 位置编码
  
代码示例：
  ```python
  # 词嵌入
  word_embeddings = embedding_layer(input_ids)  # [batch, seq_len, d_model]
  
  # 位置编码（预计算或实时计算）
  position_embeddings = positional_encoding(seq_len, d_model)
  
  # 结合
  input_embeddings = word_embeddings + position_embeddings
  ```
  
为什么用加法而不是拼接？
  1. 节省参数：d_model 不变
  2. 信息融合：词信息和位置信息在同一个向量空间
  3. 实践证明有效
""")

print("\n6. 相对位置 vs 绝对位置")
print("""
正弦余弦编码的巧妙之处：

绝对位置信息：
  每个位置有唯一编码，模型知道"这是第几个词"

相对位置信息：
  通过三角函数公式，模型能计算位置之间的距离
  例如：PE(pos+k) 可以从 PE(pos) 推导出来
  
这使得模型既能知道绝对位置，也能理解相对位置关系
""")

print("\n7. 位置编码的变体")
print("""
1. 可学习位置嵌入（BERT/GPT使用）
   ```python
   # 像词嵌入一样学习
   self.position_embeddings = nn.Embedding(max_len, d_model)
   ```

2. 相对位置编码（Transformer-XL, T5）
   - 不编码绝对位置，编码相对距离
   - 适合长文本，有更好的泛化能力

3. 旋转位置编码（RoPE，LLaMA使用）
   - 通过旋转矩阵编码位置
   - 更好的长序列外推能力

4. ALiBi（Attention with Linear Biases）
   - 在注意力分数上加一个与距离成比例的偏置
   - 简单有效，适合超长序列
""")

print("\n8. 不同模型的位置编码选择")
print("""
| 模型 | 位置编码类型 | 特点 |
|------|-------------|------|
| **原始Transformer** | 正弦余弦 | 理论优美，相对位置可计算 |
| **BERT** | 可学习嵌入 | 简单，从数据学习 |
| **GPT系列** | 可学习嵌入 | 自回归，需要绝对位置 |
| **Transformer-XL** | 相对位置 | 支持超长文本，片段递归 |
| **T5** | 相对位置 | 编码器-解码器，相对位置更好 |
| **LLaMA** | 旋转位置(RoPE) | 更好的外推能力 |
| **ChatGLM** | 旋转位置 | 中文优化 |
| **Longformer** | 多种结合 | 处理长文档 |
""")

print("\n9. 位置编码的实际效果")
print("""
没有位置编码：
  "我爱自然语言处理" = "处理自然语言爱我"
  ❌ 顺序混乱，语义错误

有位置编码：
  "我爱自然语言处理" ≠ "处理自然语言爱我"
  ✅ 保持正确顺序，语义正确

实验证明：
  - 去掉位置编码，翻译质量下降30%
  - 位置编码错误，模型完全无法工作
  - 好的位置编码能处理更长的序列
""")

print("\n10. 代码实现对比")
print("让我们实现两种位置编码：")

def learnable_positional_embedding(seq_len, d_model):
    """可学习位置嵌入（简化版）"""
    # 实际中会使用 nn.Embedding
    return np.random.randn(seq_len, d_model) * 0.02  # 模拟学习后的嵌入

def relative_position_bias(seq_len, d_model):
    """相对位置偏置（简化版）"""
    # 创建一个与距离相关的偏置矩阵
    bias = np.zeros((seq_len, seq_len))
    for i in range(seq_len):
        for j in range(seq_len):
            distance = abs(i - j)
            bias[i, j] = -distance * 0.1  # 距离越远，偏置越小（更不关注）
    return bias

# 比较
print(f"\n序列长度={seq_len}, 维度={d_model}")
print("\n正弦余弦编码（前3位置）：")
for pos in range(3):
    print(f"  位置{pos}: {pe[pos, :4]}...")

print("\n可学习编码（前3位置，模拟）：")
learnable_pe = learnable_positional_embedding(seq_len, d_model)
for pos in range(3):
    print(f"  位置{pos}: {learnable_pe[pos, :4]}...")

print("\n相对位置偏置矩阵（3×3）：")
rel_bias = relative_position_bias(3, d_model)
for i in range(3):
    print(f"  行{i}: {rel_bias[i, :3]}")

print("\n11. 位置编码的哲学思考")
print("""
位置编码解决了AI理解语言的一个根本问题：

语言的两个维度：
  1. 词汇维度：用什么词（词嵌入）
  2. 顺序维度：词的顺序（位置编码）

就像音乐：
  音符（词汇） + 节奏/顺序（位置） = 旋律（语义）

位置编码让Transformer从"词袋"变成"序列"
从"静态照片"变成"动态视频"
""")

print("\n12. 现代大模型的位置编码趋势")
print("""
趋势1：从绝对到相对
  早期：绝对位置（BERT, GPT-2）
  现在：相对位置（T5, Transformer-XL）
  未来：更灵活的相对位置

趋势2：从固定到可扩展
  问题：训练时512长度，推理时2048怎么办？
  解决方案：RoPE, ALiBi 支持长度外推

趋势3：多维度位置
  不只是线性位置，还有：
  - 二维位置（图像、表格）
  - 层次位置（树结构、代码）
  - 时间位置（视频、音频）
""")

print("\n" + "=" * 70)
print("总结：位置嵌入的核心思想")
print("=" * 70)
print("""
一句话总结：
  位置嵌入给没有顺序概念的注意力机制添加了"顺序感"

三个关键点：

1. 必要性
   - 注意力机制是排列不变的
   - 语言严重依赖顺序
   - 必须添加位置信息

2. 方法
   - 正弦余弦编码：理论优美，相对位置可计算
   - 可学习嵌入：简单实用，从数据学习
   - 相对位置编码：更灵活，适合长文本

3. 作用
   - 区分 "我爱AI" 和 "AI爱我"
   - 让模型理解语法结构
   - 支持长序列处理

位置嵌入 + 词嵌入 = 完整的输入表示
这是Transformer理解语言的基础！
""")

# 可视化（如果需要可以取消注释）
"""
try:
    import matplotlib.pyplot as plt
    
    # 可视化位置编码的热图
    plt.figure(figsize=(12, 8))
    
    # 正弦余弦编码
    plt.subplot(2, 2, 1)
    plt.imshow(pe_viz.T, aspect='auto', cmap='RdBu')
    plt.colorbar()
    plt.title('Sinusoidal Positional Encoding')
    plt.xlabel('Position')
    plt.ylabel('Dimension')
    
    # 不同位置的编码曲线
    plt.subplot(2, 2, 2)
    for pos in [0, 10, 20, 30, 40]:
        plt.plot(pe_viz[pos, :32], label=f'Pos {pos}')
    plt.title('Encoding Values at Different Positions')
    plt.xlabel('Dimension')
    plt.ylabel('Value')
    plt.legend()
    
    # 相对位置关系
    plt.subplot(2, 2, 3)
    # 计算位置0与其他位置的相似度
    similarities = []
    for pos in range(seq_len_viz):
        sim = np.dot(pe_viz[0], pe_viz[pos]) / (
            np.linalg.norm(pe_viz[0]) * np.linalg.norm(pe_viz[pos])
        )
        similarities.append(sim)
    plt.plot(range(seq_len_viz), similarities)
    plt.title('Similarity to Position 0')
    plt.xlabel('Position')
    plt.ylabel('Cosine Similarity')
    
    plt.tight_layout()
    plt.savefig('positional_encoding.png', dpi=150, bbox_inches='tight')
    print("\n可视化已保存为 positional_encoding.png")
    
except ImportError:
    print("\n(需要matplotlib才能生成可视化图像)")
"""