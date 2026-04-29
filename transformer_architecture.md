# Transformer 代码架构详解

## 🏗️ 整体架构
```
Transformer
├── 编码器 (Encoder)
│   ├── 词嵌入 (Embedding)
│   ├── 位置编码 (PositionalEncoding)
│   └── N × 编码器层 (EncoderLayer)
│       ├── 多头注意力 (MultiHeadAttention)
│       ├── 前馈网络 (FeedForward)
│       ├── 残差连接 (Add)
│       └── 层归一化 (LayerNorm)
│
├── 解码器 (Decoder)
│   ├── 词嵌入 (Embedding)
│   ├── 位置编码 (PositionalEncoding)
│   └── N × 解码器层 (DecoderLayer)
│       ├── 掩码多头注意力 (Masked MultiHeadAttention)
│       ├── 交叉注意力 (Cross Attention)
│       ├── 前馈网络 (FeedForward)
│       ├── 残差连接 (Add)
│       └── 层归一化 (LayerNorm)
│
└── 输出层 (Output Layer)
    └── 线性变换 + Softmax
```

## 🔑 核心类详解

### 1. MultiHeadAttention（多头注意力）
```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model=512, num_heads=8):
        # 四个线性变换层
        self.W_q = nn.Linear(d_model, d_model)  # Query
        self.W_k = nn.Linear(d_model, d_model)  # Key
        self.W_v = nn.Linear(d_model, d_model)  # Value
        self.W_o = nn.Linear(d_model, d_model)  # 输出
        
    def forward(self, Q, K, V, mask=None):
        # 1. 线性变换 + 分头
        Q = self.W_q(Q).view(batch, seq_len, heads, d_k)
        
        # 2. 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / sqrt(d_k)
        
        # 3. 应用掩码
        if mask: scores = scores.masked_fill(mask == 0, -1e9)
        
        # 4. Softmax
        attention = F.softmax(scores, dim=-1)
        
        # 5. 加权求和
        output = torch.matmul(attention, V)
        
        # 6. 合并多头
        output = output.transpose(1, 2).reshape(batch, seq_len, d_model)
        
        return self.W_o(output)
```

### 2. PositionalEncoding（位置编码）
```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        # 使用 sin/cos 函数生成位置编码
        pe[pos, 2i] = sin(pos / 10000^(2i/d_model))
        pe[pos, 2i+1] = cos(pos / 10000^(2i/d_model))
```

### 3. EncoderLayer（编码器层）
```python
class EncoderLayer(nn.Module):
    def forward(self, x, mask=None):
        # 1. 自注意力 + 残差 + 层归一化
        attn = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn))
        
        # 2. 前馈网络 + 残差 + 层归一化
        ff = self.feed_forward(x)
        x = self.norm2(x + self.dropout2(ff))
        
        return x
```

### 4. DecoderLayer（解码器层）
```python
class DecoderLayer(nn.Module):
    def forward(self, x, encoder_output, src_mask, tgt_mask):
        # 1. 掩码自注意力（防止看到未来）
        attn1 = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout1(attn1))
        
        # 2. 交叉注意力（关注编码器输出）
        attn2 = self.cross_attn(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout2(attn2))
        
        # 3. 前馈网络
        ff = self.feed_forward(x)
        x = self.norm3(x + self.dropout3(ff))
        
        return x
```

## 📈 数据流示例

### 翻译任务："I love you" → "我爱你"

```
输入序列: ["I", "love", "you"]
目标序列: ["我", "爱", "你"]

步骤1: 编码器处理输入
   词嵌入 → 位置编码 → 6层编码器 → 上下文向量

步骤2: 解码器自回归生成
   起始符: <SOS>
   第1步: 解码器看到 <SOS>，结合编码器输出 → 预测"我"
   第2步: 解码器看到 <SOS> "我"，结合编码器输出 → 预测"爱"
   第3步: 解码器看到 <SOS> "我" "爱"，结合编码器输出 → 预测"你"
   结束符: <EOS>
```

## ⚙️ 关键超参数

```python
# 典型配置
config = {
    "vocab_size": 30000,      # 词表大小
    "d_model": 512,           # 模型维度
    "num_heads": 8,           # 注意力头数
    "num_layers": 6,          # 编码器/解码器层数
    "d_ff": 2048,             # 前馈网络隐藏层维度
    "dropout": 0.1,           # Dropout 率
    "max_len": 512,           # 最大序列长度
}
```

## 🚀 实际应用扩展

### 1. BERT（仅编码器）
```python
# 用于理解任务：分类、NER、问答
class BERT(nn.Module):
    def __init__(self):
        self.encoder = TransformerEncoder()
        
    def forward(self, x):
        return self.encoder(x)
```

### 2. GPT（仅解码器）
```python
# 用于生成任务：文本生成、续写
class GPT(nn.Module):
    def __init__(self):
        self.decoder = TransformerDecoder()
        
    def forward(self, x):
        return self.decoder(x, None, None, causal_mask)
```

### 3. T5（编码器-解码器）
```python
# 用于转换任务：翻译、摘要、改写
class T5(nn.Module):
    def __init__(self):
        self.encoder = TransformerEncoder()
        self.decoder = TransformerDecoder()
```

## 🧪 训练技巧

```python
# 学习率预热
def get_lr(step, warmup_steps=4000):
    return min(step ** -0.5, step * warmup_steps ** -1.5)

# 梯度裁剪
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# 标签平滑
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

# 混合精度训练
from torch.cuda.amp import autocast, GradScaler
```

## 📚 学习路径建议

1. **入门**：理解注意力机制数学公式
2. **基础**：实现简化版 Transformer（纯 NumPy）
3. **进阶**：学习 PyTorch 完整实现
4. **实战**：在具体任务上微调预训练模型
5. **优化**：学习 Flash Attention、混合精度等技巧

## 🔗 相关资源

- 论文：[Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- 官方代码：[Tensor2Tensor](https://github.com/tensorflow/tensor2tensor)
- PyTorch 实现：[The Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html)
- 可视化工具：[Transformer Visualization](https://jalammar.github.io/illustrated-transformer/)