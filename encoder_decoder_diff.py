import numpy as np

print("=" * 70)
print("编码器 vs 解码器多头注意力区别详解")
print("=" * 70)

print("\n1. Transformer整体架构回顾")
print("""
Transformer = 编码器 + 解码器

编码器（Encoder）：
  输入：源序列（如英文句子）
  输出：上下文表示（理解后的表示）

解码器（Decoder）：
  输入：1. 目标序列（如中文句子，自回归生成）
        2. 编码器输出（参考信息）
  输出：下一个词的概率分布
""")

print("\n2. 编码器多头注意力（Encoder Multi-Head Attention）")
print("""
类型：自注意力（Self-Attention）
输入：Q、K、V都来自编码器输入
特点：双向，可以看到整个序列

计算过程：
  输入序列：["I", "love", "AI"]
  
  对于每个词：
    Q = 该词的查询（我想关注什么？）
    K = 所有词的键（你们有什么特征？）
    V = 所有词的值（你们实际包含什么？）
    
  注意力：每个词关注序列中的所有词
  
例子："love"的注意力：
  - 关注"I"（主语）
  - 关注"AI"（宾语）
  - 关注自己（自指）
  
结果：每个词获得包含上下文信息的表示
""")

print("\n3. 解码器多头注意力（Decoder Multi-Head Attention）")
print("""
解码器有两层注意力：

第一层：掩码自注意力（Masked Self-Attention）
  类型：自注意力 + 因果掩码
  输入：Q、K、V都来自解码器输入
  特点：单向，只能看到前面的词
  
第二层：交叉注意力（Cross-Attention）
  类型：编码器-解码器注意力
  输入：Q来自解码器，K、V来自编码器
  特点：参考编码器信息
""")

print("\n4. 掩码自注意力详解")
print("""
为什么需要掩码？
  解码器生成是自回归的：一个一个词生成
  生成第t个词时，不能看到第t+1个及以后的词（未来信息）
  
因果掩码（Causal Mask）：
  下三角矩阵，上三角为-inf
  
例子：生成序列 ["我", "爱", "AI"]
  
生成"爱"时：
  可以看到：["我"]（前面已生成的词）
  不能看到：["AI"]（未来要生成的词）
  
掩码实现：
  注意力分数矩阵：
    [我, 爱, AI] × [我, 爱, AI]ᵀ
    
  应用掩码后：
    [我] 可以关注 [我]
    [爱] 可以关注 [我, 爱]
    [AI] 可以关注 [我, 爱, AI]
    
  上三角（未来位置）被掩码为 -inf
""")

print("\n5. 交叉注意力详解")
print("""
为什么需要交叉注意力？
  解码器生成目标词时，需要参考源序列信息
  
输入：
  Q：来自解码器（当前生成词的查询）
  K、V：来自编码器（源序列的键和值）
  
计算过程：
  解码器词"猫"的Q vs 编码器所有词的K
  找到最相关的源语言词
  用注意力权重加权编码器的V
  
例子：英译中
  源序列：["The", "cat", "sat", "on", "the", "mat"]
  目标序列：["猫", "坐在", "垫子", "上"]
  
生成"猫"时：
  Q："猫"的查询（想知道英文对应什么？）
  K：["The", "cat", "sat", "on", "the", "mat"]的键
  V：这些词的英文语义信息
  
注意力："猫"的Q与"cat"的K最相似
结果："猫"获得"cat"的语义信息
""")

print("\n6. 代码实现对比")
print("让我们实现两种注意力：")

def encoder_self_attention():
    """编码器自注意力示例"""
    print("\n=== 编码器自注意力 ===")
    
    # 模拟输入序列：["I", "love", "AI"]
    seq_len = 3
    d_model = 4
    
    np.random.seed(42)
    # 输入词向量（已包含位置编码）
    X = np.random.randn(seq_len, d_model)
    
    print(f"输入序列: ['I', 'love', 'AI']")
    print(f"输入形状: {X.shape}")
    print(f"\n输入向量:")
    for i, word in enumerate(["I", "love", "AI"]):
        print(f"  '{word}': {X[i]}")
    
    # 模拟Q、K、V（实际中通过线性变换得到）
    # 为简化，假设X就是Q、K、V
    Q = X
    K = X
    V = X
    
    # 计算注意力分数
    scores = np.dot(Q, K.T) / np.sqrt(d_model)
    
    print(f"\n注意力分数矩阵（无掩码）:")
    print(scores)
    print("\n每个词可以看到所有词（双向）")
    
    # Softmax得到注意力权重
    attention_weights = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    attention_weights = attention_weights / np.sum(attention_weights, axis=-1, keepdims=True)
    
    print(f"\n注意力权重:")
    for i, word in enumerate(["I", "love", "AI"]):
        print(f"  '{word}'关注: I={attention_weights[i,0]:.3f}, love={attention_weights[i,1]:.3f}, AI={attention_weights[i,2]:.3f}")
    
    # 加权求和
    output = np.dot(attention_weights, V)
    
    print(f"\n输出（每个词获得上下文信息）:")
    for i, word in enumerate(["I", "love", "AI"]):
        print(f"  '{word}'输出: {output[i]}")
    
    return X, attention_weights

def decoder_masked_attention():
    """解码器掩码自注意力示例"""
    print("\n=== 解码器掩码自注意力 ===")
    
    # 模拟目标序列：["我", "爱", "AI"]（自回归生成）
    seq_len = 3
    d_model = 4
    
    np.random.seed(42)
    # 解码器输入（已生成的部分）
    X_decoder = np.random.randn(seq_len, d_model)
    
    print(f"目标序列: ['我', '爱', 'AI']（自回归生成）")
    print(f"解码器输入形状: {X_decoder.shape}")
    
    # 模拟Q、K、V
    Q = X_decoder
    K = X_decoder
    V = X_decoder
    
    # 计算注意力分数
    scores = np.dot(Q, K.T) / np.sqrt(d_model)
    
    print(f"\n原始注意力分数:")
    print(scores)
    
    # 创建因果掩码（下三角为0，上三角为-inf）
    mask = np.triu(np.ones((seq_len, seq_len)), k=1)  # 上三角为1
    mask = mask * -1e9  # 上三角为-inf
    
    print(f"\n因果掩码矩阵:")
    print(mask)
    print("0表示可以关注，-inf表示不能关注")
    
    # 应用掩码
    masked_scores = scores + mask
    
    print(f"\n掩码后分数:")
    print(masked_scores)
    
    # Softmax（-inf经过softmax变成0）
    attention_weights = np.exp(masked_scores - np.max(masked_scores, axis=-1, keepdims=True))
    attention_weights = attention_weights / np.sum(attention_weights, axis=-1, keepdims=True)
    
    print(f"\n掩码注意力权重:")
    print("'我'（位置0）: 只能关注自己")
    print("'爱'（位置1）: 可以关注'我'和自己")
    print("'AI'（位置2）: 可以关注'我'、'爱'和自己")
    print(f"\n具体权重:")
    for i, word in enumerate(["我", "爱", "AI"]):
        row = [f"{w:.3f}" for w in attention_weights[i]]
        print(f"  '{word}'关注: {row}")
    
    return attention_weights

def cross_attention_example():
    """交叉注意力示例"""
    print("\n=== 解码器交叉注意力 ===")
    
    # 源序列（编码器输出）：["The", "cat", "sat"]
    encoder_seq_len = 3
    # 目标序列（解码器输入）：["猫", "坐在"]
    decoder_seq_len = 2
    d_model = 4
    
    np.random.seed(42)
    # 编码器输出（源序列表示）
    encoder_output = np.random.randn(encoder_seq_len, d_model)
    # 解码器当前状态（目标序列表示）
    decoder_state = np.random.randn(decoder_seq_len, d_model)
    
    print(f"源序列（编码器）: ['The', 'cat', 'sat']")
    print(f"目标序列（解码器）: ['猫', '坐在']")
    print(f"编码器输出形状: {encoder_output.shape}")
    print(f"解码器状态形状: {decoder_state.shape}")
    
    # 交叉注意力：Q来自解码器，K、V来自编码器
    Q = decoder_state  # 解码器的查询
    K = encoder_output  # 编码器的键
    V = encoder_output  # 编码器的值
    
    # 计算注意力分数
    scores = np.dot(Q, K.T) / np.sqrt(d_model)
    
    print(f"\n交叉注意力分数（解码器Q vs 编码器K）:")
    print("行：解码器词，列：编码器词")
    print(scores)
    
    # Softmax
    attention_weights = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    attention_weights = attention_weights / np.sum(attention_weights, axis=-1, keepdims=True)
    
    print(f"\n交叉注意力权重:")
    print("'猫'（解码器）最关注'cat'（编码器）")
    print("'坐在'（解码器）最关注'sat'（编码器）")
    print(f"\n具体权重:")
    for i, word in enumerate(["猫", "坐在"]):
        row = [f"{w:.3f}" for w in attention_weights[i]]
        print(f"  '{word}'关注编码器: The={row[0]}, cat={row[1]}, sat={row[2]}")
    
    # 加权求和
    output = np.dot(attention_weights, V)
    
    print(f"\n交叉注意力输出:")
    print("解码器词获得了编码器信息")
    for i, word in enumerate(["猫", "坐在"]):
        print(f"  '{word}'输出: {output[i]}")
    
    return attention_weights

print("\n7. 运行示例")
encoder_X, encoder_weights = encoder_self_attention()
decoder_weights = decoder_masked_attention()
cross_weights = cross_attention_example()

print("\n8. 注意力模式可视化")
print("""
编码器自注意力模式（无掩码）：
  I   → [I, love, AI]
  love → [I, love, AI]
  AI  → [I, love, AI]
  每个词可以看到所有词

解码器掩码自注意力模式：
  我   → [我]
  爱   → [我, 爱]
  AI  → [我, 爱, AI]
  只能看到前面词

解码器交叉注意力模式：
  猫   → [The, cat, sat]（编码器所有词）
  坐在 → [The, cat, sat]（编码器所有词）
  参考源序列信息
""")

print("\n9. 训练与推理的区别")
print("""
训练时（Teacher Forcing）：
  解码器输入：完整目标序列（一次输入）
  掩码：仍然需要（防止看到未来信息）
  并行计算：可以并行计算所有位置
  
推理时（自回归生成）：
  解码器输入：已生成的部分序列
  掩码：自动满足（没有未来信息）
  串行生成：一个一个词生成
  
关键：训练时用掩码模拟推理时的因果约束。
""")

print("\n10. 不同任务中的应用")
print("""
任务1：机器翻译（编码器-解码器）
  编码器：理解源语言句子
  解码器：生成目标语言句子（参考编码器）

任务2：文本生成（仅解码器，如GPT）
  只有解码器（没有编码器）
  只有掩码自注意力
  自回归生成文本

任务3：文本理解（仅编码器，如BERT）
  只有编码器
  只有自注意力（无掩码）
  理解输入文本

任务4：序列到序列（T5）
  编码器：理解输入
  解码器：生成输出（参考编码器）
""")

print("\n11. 实际模型配置")
print("""
BERT（仅编码器）：
  层数：12-24层
  每层：自注意力 + 前馈网络
  注意力：双向，无掩码

GPT（仅解码器）：
  层数：12-96层
  每层：掩码自注意力 + 前馈网络
  注意力：单向，有因果掩码

T5（编码器-解码器）：
  编码器：12层，自注意力
  解码器：12层，掩码自注意力 + 交叉注意力
""")

print("\n12. 性能考虑")
print("""
计算复杂度：
  编码器自注意力：O(n²)（n=源序列长度）
  解码器掩码自注意力：O(m²)（m=目标序列长度）
  解码器交叉注意力：O(m×n)（解码器×编码器）

内存消耗：
  编码器：存储n×n注意力矩阵
  解码器：存储m×m和m×n两个注意力矩阵

优化技巧：
  KV缓存：解码器推理时缓存K、V，避免重复计算
  稀疏注意力：减少计算量
  线性注意力：降低复杂度
""")

print("\n13. 设计哲学")
print("""
编码器设计哲学：
  "全面理解" - 看到整个输入，建立完整表示
  像：读完一篇文章，全面理解内容

解码器设计哲学：
  "逐步生成" - 基于已有内容，参考源信息，生成下一个
  像：写作时，基于已写内容和参考资料，写下一句

掩码的必要性：
  防止信息泄漏（不能看到未来）
  确保自回归性质（一个一个生成）
  模拟人类生成过程（想到哪写到哪）
""")

print("\n14. 常见问题")
print("""
问题1：为什么解码器需要两层注意力？
  答：第一层理解目标序列内部关系，第二层参考源序列信息。

问题2：训练时解码器能看到完整目标序列，为什么还要掩码？
  答：掩码确保模型学会自回归生成，不会依赖未来信息。

问题3：编码器为什么不需要掩码？
  答：编码器任务是理解，需要看到整个序列建立完整表示。

问题4：交叉注意力中，为什么K和V都来自编码器？
  答：K用于匹配（哪些源词相关），V用于传递信息（相关源词的信息）。
""")

print("\n" + "=" * 70)
print("总结：编码器 vs 解码器多头注意力")
print("=" * 70)
print("""
三大核心区别：

1. **注意力类型不同**
   编码器：自注意力（看自己）
   解码器：掩码自注意力 + 交叉注意力（先看自己，再看编码器）

2. **信息访问权限不同**
   编码器：双向，可以看到整个序列
   解码器：单向，只能看到前面词（掩码）

3. **输入来源不同**
   编码器：Q、K、V都来自编码器输入
   解码器：
     - 掩码自注意力：Q、K、V来自解码器输入
     - 交叉注意力：Q来自解码器，K、V来自编码器

关键理解：
  编码器是"理解者" - 全面分析输入
  解码器是"生成者" - 基于理解和已有内容生成
  
就像：
  编码器：读者（读完并理解文章）
  解码器：作者（基于理解和已写内容，写下一句）
""")

print("\n🎯 记住：")
print("编码器：自注意力，双向，全面理解")
print("解码器：掩码自注意力（单向） + 交叉注意力（参考编码器）")