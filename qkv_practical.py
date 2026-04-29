import numpy as np
import torch
import torch.nn as nn

print("=" * 70)
print("实际应用中 Q、K、V 的获取方法")
print("=" * 70)

print("\n1. 整体流程概览")
print("""
输入：词向量序列 [batch_size, seq_len, d_model]
    ↓
三个独立的线性变换层：
    ↓
Q = Linear_q(输入)  # 查询变换
K = Linear_k(输入)  # 键变换
V = Linear_v(输入)  # 值变换
    ↓
多头分拆
    ↓
注意力计算
""")

print("\n2. 实际代码实现（PyTorch）")
print("让我们看一个完整的实现：")

class PracticalMultiHeadAttention(nn.Module):
    """实际应用中的多头注意力实现"""
    
    def __init__(self, d_model=512, num_heads=8, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # 关键：三个独立的线性变换层
        self.W_q = nn.Linear(d_model, d_model)  # 查询变换
        self.W_k = nn.Linear(d_model, d_model)  # 键变换
        self.W_v = nn.Linear(d_model, d_model)  # 值变换
        self.W_o = nn.Linear(d_model, d_model)  # 输出变换
        
        self.dropout = nn.Dropout(dropout)
        
    def split_heads(self, x):
        """将输入分成多个头"""
        batch_size, seq_len, d_model = x.size()
        return x.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
    
    def merge_heads(self, x):
        """合并多个头"""
        batch_size, _, seq_len, d_k = x.size()
        return x.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
    
    def forward(self, query, key, value, mask=None):
        """前向传播"""
        batch_size = query.size(0)
        
        print(f"\n=== 前向传播开始 ===")
        print(f"输入形状: query={query.shape}, key={key.shape}, value={value.shape}")
        
        # 1. 线性变换得到 Q、K、V
        Q = self.W_q(query)  # [batch, seq_len, d_model]
        K = self.W_k(key)    # [batch, seq_len, d_model]
        V = self.W_v(value)  # [batch, seq_len, d_model]
        
        print(f"\n1. 线性变换后:")
        print(f"  Q形状: {Q.shape}")
        print(f"  K形状: {K.shape}")
        print(f"  V形状: {V.shape}")
        print(f"  注意：Q、K、V形状相同，但内容不同（不同权重矩阵变换）")
        
        # 2. 分头
        Q = self.split_heads(Q)  # [batch, heads, seq_len, d_k]
        K = self.split_heads(K)
        V = self.split_heads(V)
        
        print(f"\n2. 分头后（多头注意力）:")
        print(f"  Q形状: {Q.shape}")
        print(f"  K形状: {K.shape}")
        print(f"  V形状: {V.shape}")
        print(f"  每个头维度 d_k = {self.d_k}")
        
        # 3. 计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = torch.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        print(f"\n3. 注意力计算:")
        print(f"  注意力分数形状: {scores.shape}  # [batch, heads, seq_len, seq_len]")
        print(f"  注意力权重形状: {attention_weights.shape}")
        
        # 4. 应用注意力到V
        attention_output = torch.matmul(attention_weights, V)
        
        print(f"\n4. 应用注意力到V:")
        print(f"  注意力输出形状: {attention_output.shape}")
        
        # 5. 合并多头
        concatenated = self.merge_heads(attention_output)
        
        print(f"\n5. 合并多头:")
        print(f"  合并后形状: {concatenated.shape}")
        
        # 6. 输出线性变换
        output = self.W_o(concatenated)
        
        print(f"\n6. 最终输出:")
        print(f"  输出形状: {output.shape}")
        
        return output, attention_weights

print("\n3. 实际数据流演示")
print("让我们用具体数据演示：")

# 创建模拟数据
def create_mock_data():
    """创建模拟输入数据"""
    print("\n创建模拟输入数据：")
    
    # 假设：批量大小=2，序列长度=3，模型维度=12
    batch_size, seq_len, d_model = 2, 3, 12
    
    # 模拟词向量（已经经过词嵌入+位置编码）
    torch.manual_seed(42)
    input_embeddings = torch.randn(batch_size, seq_len, d_model)
    
    print(f"输入词向量形状: {input_embeddings.shape}")
    print(f"输入示例（第一个batch的第一个词）:")
    print(f"  {input_embeddings[0, 0, :6]}...")
    
    return input_embeddings

# 创建模型
def demonstrate_qkv_creation():
    """演示Q、K、V的创建过程"""
    print("\n=== 创建多头注意力模型 ===")
    
    d_model = 12
    num_heads = 3
    model = PracticalMultiHeadAttention(d_model=d_model, num_heads=num_heads)
    
    print(f"模型配置:")
    print(f"  d_model = {d_model}")
    print(f"  num_heads = {num_heads}")
    print(f"  d_k = {d_model // num_heads}")
    
    # 查看权重矩阵
    print(f"\n权重矩阵形状:")
    print(f"  W_q形状: {model.W_q.weight.shape}  # [{d_model}, {d_model}]")
    print(f"  W_k形状: {model.W_k.weight.shape}")
    print(f"  W_v形状: {model.W_v.weight.shape}")
    print(f"  W_o形状: {model.W_o.weight.shape}")
    
    # 创建输入数据
    input_embeddings = create_mock_data()
    
    # 自注意力：Q、K、V都来自同一个输入
    print(f"\n=== 自注意力模式 ===")
    print("Q、K、V都来自同一个输入序列")
    
    output, attention_weights = model(
        query=input_embeddings,
        key=input_embeddings,
        value=input_embeddings
    )
    
    return model, input_embeddings, output

model, inputs, output = demonstrate_qkv_creation()

print("\n4. 权重矩阵的初始化与学习")
print("""
Q、K、V的权重矩阵如何初始化？

标准初始化（Transformer论文）：
  W_q, W_k, W_v, W_o 使用 Xavier/Glorot 初始化
  
PyTorch中：
  nn.Linear默认使用Kaiming均匀初始化
  
训练过程：
  1. 前向传播：输入 → 线性变换 → Q、K、V
  2. 计算损失：比较输出与目标
  3. 反向传播：梯度通过注意力机制传回
  4. 更新权重：调整W_q、W_k、W_v
  
学习目标：
  W_q：学习生成有效的查询表示
  W_k：学习生成可匹配的键表示
  W_v：学习生成有价值的信息表示
""")

print("\n5. 不同场景下的Q、K、V来源")
print("""
场景1：编码器自注意力（如BERT）
  输入：同一个序列的词向量
  Q、K、V：都来自同一个输入
  代码：model(input, input, input)

场景2：解码器自注意力（如GPT）
  输入：目标序列的词向量（带因果掩码）
  Q、K、V：都来自目标序列
  代码：model(target, target, target, causal_mask)

场景3：编码器-解码器注意力（如翻译）
  Q：来自解码器（目标语言）
  K、V：来自编码器（源语言）
  代码：model(decoder_output, encoder_output, encoder_output)

场景4：跨模态注意力（如图文理解）
  Q：来自文本序列
  K、V：来自图像特征
  代码：model(text_embeddings, image_features, image_features)
""")

print("\n6. 实际项目中的代码示例")
print("""
在真实Transformer项目中：

```python
# BERT中的自注意力
class BertSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        
        # 三个线性变换
        self.query = nn.Linear(config.hidden_size, config.hidden_size)
        self.key = nn.Linear(config.hidden_size, config.hidden_size)
        self.value = nn.Linear(config.hidden_size, config.hidden_size)
        
    def forward(self, hidden_states, attention_mask=None):
        # 线性变换得到Q、K、V
        query_layer = self.query(hidden_states)
        key_layer = self.key(hidden_states)
        value_layer = self.value(hidden_states)
        
        # 后续计算...
```

在HuggingFace Transformers库中：
  这些线性变换层已经封装好，直接调用即可。
""")

print("\n7. Q、K、V的维度变化可视化")
print("""
以BERT-base为例：
  d_model = 768
  num_heads = 12
  d_k = 768 / 12 = 64

数据流：
  输入: [batch, seq_len, 768]
    ↓
  线性变换（三个独立）:
    Q: [batch, seq_len, 768] → W_q → [batch, seq_len, 768]
    K: [batch, seq_len, 768] → W_k → [batch, seq_len, 768]
    V: [batch, seq_len, 768] → W_v → [batch, seq_len, 768]
    ↓
  分头:
    Q: [batch, 12, seq_len, 64]
    K: [batch, 12, seq_len, 64]
    V: [batch, 12, seq_len, 64]
    ↓
  注意力计算...
""")

print("\n8. 训练过程中的Q、K、V变化")
print("""
训练初期：
  W_q、W_k、W_v是随机初始化的
  Q、K、V的变换没有明确意义
  注意力模式随机

训练中期：
  网络开始学习有效的注意力模式
  W_q学习生成有意义的查询
  W_k学习生成可匹配的键
  W_v学习生成有价值的信息

训练后期：
  Q、K、V的变换高度专业化
  每个头学习关注特定方面
  注意力模式变得清晰、有意义
""")

print("\n9. 实际调试技巧")
print("""
调试Q、K、V的方法：

1. 检查形状
   ```python
   print(f"Q shape: {Q.shape}")
   print(f"K shape: {K.shape}")
   print(f"V shape: {V.shape}")
   ```

2. 可视化注意力权重
   ```python
   import matplotlib.pyplot as plt
   plt.imshow(attention_weights[0, 0].detach().cpu().numpy())
   plt.show()
   ```

3. 检查梯度
   ```python
   print(f"W_q grad norm: {model.W_q.weight.grad.norm()}")
   print(f"W_k grad norm: {model.W_k.weight.grad.norm()}")
   print(f"W_v grad norm: {model.W_v.weight.grad.norm()}")
   ```

4. 对比不同头的注意力
   ```python
   # 查看不同头的注意力模式
   for head in range(num_heads):
       print(f"Head {head} attention pattern:")
       print(attention_weights[0, head])
   ```
""")

print("\n10. 性能优化技巧")
print("""
实际生产中的优化：

1. 融合线性变换
   ```python
   # 传统：三个独立的线性层
   # 优化：一个大的线性层，然后分割
   combined = nn.Linear(d_model, 3 * d_model)
   Q, K, V = torch.split(combined_output, d_model, dim=-1)
   ```

2. 缓存K、V（推理优化）
   ```python
   # GPT等自回归模型推理时
   # 可以缓存之前计算的K、V，避免重复计算
   if use_cache:
       key_states = torch.cat([past_key, key_states], dim=2)
       value_states = torch.cat([past_value, value_states], dim=2)
   ```

3. 量化与压缩
   ```python
   # 对W_q、W_k、W_v进行量化，减少内存
   quantized_W_q = quantize(model.W_q.weight)
   ```

4. 稀疏注意力
   ```python
   # 只计算部分位置的注意力，减少计算量
   sparse_scores = compute_sparse_attention(Q, K)
   ```
""")

print("\n11. 常见问题与解决方案")
print("""
问题1：Q、K、V的维度不匹配
  解决：确保d_model能被num_heads整除

问题2：注意力权重全为0或NaN
  解决：检查mask是否正确，梯度是否爆炸

问题3：某个头不学习（注意力均匀）
  解决：尝试不同的初始化，增加dropout

问题4：内存不足（OOM）
  解决：使用梯度检查点，减少batch_size，使用混合精度
""")

print("\n12. 现代大模型的实际实现")
print("""
以LLaMA为例的实际实现：

```python
# LLaMA的注意力实现（简化）
class LLaMAAttention(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.n_heads = args.n_heads
        self.head_dim = args.dim // args.n_heads
        
        # Q、K、V的线性变换
        self.wq = nn.Linear(args.dim, args.n_heads * self.head_dim, bias=False)
        self.wk = nn.Linear(args.dim, args.n_heads * self.head_dim, bias=False)
        self.wv = nn.Linear(args.dim, args.n_heads * self.head_dim, bias=False)
        self.wo = nn.Linear(args.n_heads * self.head_dim, args.dim, bias=False)
        
    def forward(self, x, freqs_cis, mask=None):
        bsz, seqlen, _ = x.shape
        
        # 1. 线性变换得到Q、K、V
        xq, xk, xv = self.wq(x), self.wk(x), self.wv(x)
        
        # 2. 应用旋转位置编码（RoPE）
        xq, xk = apply_rotary_emb(xq, xk, freqs_cis)
        
        # 3. 分头
        xq = xq.view(bsz, seqlen, self.n_heads, self.head_dim)
        xk = xk.view(bsz, seqlen, self.n_heads, self.head_dim)
        xv = xv.view(bsz, seqlen, self.n_heads, self.head_dim)
        
        # 4. 转置以便计算
        xq, xk, xv = xq.transpose(1, 2), xk.transpose(1, 2), xv.transpose(1, 2)
        
        # 5. 注意力计算
        scores = torch.matmul(xq, xk.transpose(2, 3)) / math.sqrt(self.head_dim)
        if mask is not None:
            scores = scores + mask
        scores = F.softmax(scores.float(), dim=-1).type_as(xq)
        output = torch.matmul(scores, xv)
        
        # 6. 合并多头 + 输出变换
        output = output.transpose(1, 2).contiguous().view(bsz, seqlen, -1)
        return self.wo(output)
```
""")

print("\n" + "=" * 70)
print("总结：实际应用中Q、K、V的获取")
print("=" * 70)
print("""
三步获取Q、K、V：

1. **输入准备**
   词嵌入 + 位置编码 → 输入向量 [batch, seq_len, d_model]

2. **线性变换**
   Q = W_q · 输入  # 查询变换
   K = W_k · 输入  # 键变换
   V = W_v · 输入  # 值变换
   
   其中W_q、W_k、W_v是可学习的权重矩阵

3. **多头处理**
   将Q、K、V分成多个头
   每个头独立计算注意力

关键点：
  - Q、K、V来自同一个输入，但经过不同变换
  - 三个变换矩阵独立学习不同功能
  - 多头机制让每个头关注不同方面
  - 实际代码中已经高度优化和封装

一句话记住：
