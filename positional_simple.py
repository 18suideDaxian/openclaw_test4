import numpy as np

print("=" * 70)
print("位置嵌入（Positional Embedding）核心原理")
print("=" * 70)

print("\n1. 问题：Transformer没有顺序概念")
print("""
注意力机制是排列不变的（permutation invariant）：

输入：["我", "爱", "AI"]
注意力看到：{我, 爱, AI}（集合，无顺序）

结果：
  "我爱AI" 和 "AI爱我" 对模型来说是一样的！
  但实际上语义完全不同。
""")

print("\n2. 解决方案：添加位置信息")
print("""
给每个位置一个唯一标识：
  位置0 → 向量P₀
  位置1 → 向量P₁  
  位置2 → 向量P₂
  ...

最终输入 = 词向量 + 位置向量
""")

print("\n3. Transformer原创：正弦余弦位置编码")
print("""
公式（非常巧妙！）：
  PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
  PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

例子：d_model=4（简化）
  位置0: [sin(0), cos(0), sin(0/100), cos(0/100)] = [0, 1, 0, 1]
  位置1: [sin(1), cos(1), sin(1/100), cos(1/100)] ≈ [0.84, 0.54, 0.01, 1.00]
  位置2: [sin(2), cos(2), sin(2/100), cos(2/100)] ≈ [0.91, -0.42, 0.02, 1.00]
""")

def sinusoidal_pe(pos, d_model=4):
    """计算一个位置的正弦余弦编码"""
    pe = np.zeros(d_model)
    for i in range(0, d_model, 2):
        pe[i] = np.sin(pos / (10000 ** (i / d_model)))
        if i + 1 < d_model:
            pe[i + 1] = np.cos(pos / (10000 ** (i / d_model)))
    return pe

print("\n4. 实际计算示例")
print("d_model=6，计算前4个位置：")

d_model = 6
for pos in range(4):
    pe = sinusoidal_pe(pos, d_model)
    print(f"  位置{pos}: {pe}")

print("\n5. 为什么用sin/cos？三个神奇性质")
print("""
性质1：唯一性
  每个位置编码都不同，不会重复

性质2：有界性  
  值在[-1, 1]之间，与词向量尺度匹配

性质3：相对位置可计算（最神奇！）
  存在线性变换 M，使得：
    PE(pos + k) = M · PE(pos)
  
  这意味着模型可以学会"位置关系"
  例如：位置1 + 位置2 ≈ 位置3
""")

print("\n6. 位置编码 + 词编码 = 完整输入")
print("""
例子：句子"我爱AI"

词嵌入：
  "我" → [0.1, -0.2, 0.3, 0.4]
  "爱" → [0.4, 0.1, -0.1, 0.2]  
  "AI" → [-0.1, 0.3, 0.2, 0.1]

位置编码：
  位置0 → [0.0, 1.0, 0.0, 1.0]
  位置1 → [0.8, 0.5, 0.0, 1.0]
  位置2 → [0.9, -0.4, 0.0, 1.0]

最终输入（相加）：
  "我"在位置0 → [0.1, 0.8, 0.3, 1.4]
  "爱"在位置1 → [1.2, 0.6, -0.1, 1.2]
  "AI"在位置2 → [0.8, -0.1, 0.2, 1.1]
""")

print("\n7. 其他位置编码方法")
print("""
1. 可学习位置嵌入（BERT/GPT使用）
   - 像词嵌入一样随机初始化，通过训练学习
   - 简单，但需要训练数据

2. 相对位置编码（T5使用）
   - 不编码绝对位置，编码相对距离
   - 例如："我"和"爱"距离1，"我"和"AI"距离2

3. 旋转位置编码（RoPE，LLaMA使用）
   - 通过旋转矩阵编码位置
   - 更好的长文本处理能力

4. ALiBi（Attention with Linear Biases）
   - 在注意力分数上加一个与距离成比例的偏置
   - 距离越远，关注度越低
""")

print("\n8. 位置编码的重要性验证")
print("""
实验：去掉位置编码会怎样？

任务：机器翻译
  有位置编码：BLEU得分 28.4
  无位置编码：BLEU得分 8.7（下降70%！）

结论：位置编码不是可选的，是必需的！
""")

print("\n9. 代码实现对比")
print("让我们实现两种位置编码：")

# 正弦余弦编码
def create_sinusoidal_pe(seq_len, d_model):
    pe = np.zeros((seq_len, d_model))
    for pos in range(seq_len):
        for i in range(0, d_model, 2):
            pe[pos, i] = np.sin(pos / (10000 ** (i / d_model)))
            if i + 1 < d_model:
                pe[pos, i + 1] = np.cos(pos / (10000 ** (i / d_model)))
    return pe

# 可学习编码（模拟）
def create_learnable_pe(seq_len, d_model):
    # 模拟训练后的可学习位置嵌入
    np.random.seed(42)
    return np.random.randn(seq_len, d_model) * 0.1

print("\n序列长度=5，维度=8")
seq_len, d_model = 5, 8

sin_pe = create_sinusoidal_pe(seq_len, d_model)
learn_pe = create_learnable_pe(seq_len, d_model)

print("\n正弦余弦编码（前2个位置）：")
for pos in range(2):
    print(f"  位置{pos}: {sin_pe[pos, :4]}...")

print("\n可学习编码（前2个位置，模拟）：")
for pos in range(2):
    print(f"  位置{pos}: {learn_pe[pos, :4]}...")

print("\n10. 位置编码的直观理解")
print("""
比喻1：音乐会座位
  词嵌入：你是谁（钢琴家、小提琴手）
  位置编码：你坐在第几排第几座
  合起来：钢琴家坐在第一排中央

比喻2：时间线
  词嵌入：发生了什么事件
  位置编码：事件发生的时间点
  合起来：9:00开会，10:00喝咖啡

比喻3：坐标系统
  词嵌入：物体的性质（红色、圆形）
  位置编码：物体的位置坐标(x,y,z)
  合起来：红色的圆在(1,2,3)位置
""")

print("\n11. 现代大模型的位置编码选择")
print("""
| 模型 | 位置编码 | 原因 |
|------|----------|------|
| BERT | 可学习 | 简单，双向注意力需要绝对位置 |
| GPT | 可学习 | 自回归生成需要知道当前位置 |
| T5 | 相对位置 | 编码器-解码器，相对位置更灵活 |
| LLaMA | 旋转位置(RoPE) | 更好的长度外推能力 |
| ChatGLM | 旋转位置 | 中文优化，长文本支持 |
| Longformer | 多种结合 | 专门处理长文档 |
""")

print("\n12. 位置编码的未来发展")
print("""
挑战：如何支持超长文本？
  - 训练时512长度，推理时要处理10万长度
  - 现有方法外推能力有限

解决方案方向：
  1. 相对位置编码的改进
  2. 层次位置编码（段落、句子、词）
  3. 压缩位置信息（类似视频关键帧）
  4. 动态位置编码（根据内容调整）
""")

print("\n" + "=" * 70)
print("核心总结")
print("=" * 70)
print("""
位置嵌入解决了Transformer的根本缺陷：

问题：注意力机制没有顺序概念
  输入 ["A", "B", "C"] = 输入 ["C", "B", "A"]

解决方案：添加位置信息
  位置0 + 词A ≠ 位置2 + 词A

两种主要方法：
  1. 正弦余弦编码（Transformer原创）
     - 数学优美，相对位置可计算
     - 不需要训练
  
  2. 可学习位置嵌入（BERT/GPT使用）
     - 简单直接，从数据学习
     - 需要训练数据

关键作用：
  - 区分 "我爱AI" 和 "AI爱我"
  - 让模型理解语法结构
  - 支持序列任务（翻译、生成、摘要）

没有位置嵌入，Transformer只是一个高级词袋模型。
有了位置嵌入，Transformer才能真正理解语言序列。
""")

print("\n🎯 一句话记住：")
print("词嵌入告诉模型'是什么'，位置嵌入告诉模型'在哪里'。")