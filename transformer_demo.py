import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class MultiHeadAttention(nn.Module):
    """多头注意力机制"""
    def __init__(self, d_model=512, num_heads=8, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # 线性变换层
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # 1. 线性变换并分头
        Q = self.W_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # 2. 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        # 3. 应用掩码（如果有）
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        # 4. Softmax 得到注意力权重
        attention = F.softmax(scores, dim=-1)
        attention = self.dropout(attention)
        
        # 5. 加权求和
        output = torch.matmul(attention, V)
        
        # 6. 合并多头
        output = output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model
        )
        
        # 7. 输出线性变换
        output = self.W_o(output)
        
        return output

class PositionalEncoding(nn.Module):
    """位置编码"""
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                           (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)  # [1, max_len, d_model]
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        # x: [batch_size, seq_len, d_model]
        return x + self.pe[:, :x.size(1)]

class FeedForward(nn.Module):
    """前馈神经网络"""
    def __init__(self, d_model=512, d_ff=2048, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        return self.linear2(self.dropout(F.relu(self.linear1(x))))

class EncoderLayer(nn.Module):
    """编码器层"""
    def __init__(self, d_model=512, num_heads=8, d_ff=2048, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        
    def forward(self, x, mask=None):
        # 1. 自注意力 + 残差连接 + 层归一化
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_output))
        
        # 2. 前馈网络 + 残差连接 + 层归一化
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout2(ff_output))
        
        return x

class DecoderLayer(nn.Module):
    """解码器层"""
    def __init__(self, d_model=512, num_heads=8, d_ff=2048, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.cross_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.dropout3 = nn.Dropout(dropout)
        
    def forward(self, x, encoder_output, src_mask=None, tgt_mask=None):
        # 1. 掩码自注意力
        attn_output = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout1(attn_output))
        
        # 2. 交叉注意力（关注编码器输出）
        attn_output = self.cross_attn(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout2(attn_output))
        
        # 3. 前馈网络
        ff_output = self.feed_forward(x)
        x = self.norm3(x + self.dropout3(ff_output))
        
        return x

class Transformer(nn.Module):
    """完整的 Transformer 模型"""
    def __init__(self, src_vocab_size=10000, tgt_vocab_size=10000,
                 d_model=512, num_heads=8, num_layers=6, d_ff=2048,
                 max_len=100, dropout=0.1):
        super().__init__()
        
        # 词嵌入
        self.src_embedding = nn.Embedding(src_vocab_size, d_model)
        self.tgt_embedding = nn.Embedding(tgt_vocab_size, d_model)
        
        # 位置编码
        self.positional_encoding = PositionalEncoding(d_model, max_len)
        
        # 编码器
        self.encoder_layers = nn.ModuleList([
            EncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # 解码器
        self.decoder_layers = nn.ModuleList([
            DecoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # 输出层
        self.output_layer = nn.Linear(d_model, tgt_vocab_size)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        # 编码器
        src_embedded = self.dropout(self.positional_encoding(self.src_embedding(src)))
        encoder_output = src_embedded
        for layer in self.encoder_layers:
            encoder_output = layer(encoder_output, src_mask)
        
        # 解码器
        tgt_embedded = self.dropout(self.positional_encoding(self.tgt_embedding(tgt)))
        decoder_output = tgt_embedded
        for layer in self.decoder_layers:
            decoder_output = layer(decoder_output, encoder_output, src_mask, tgt_mask)
        
        # 输出
        output = self.output_layer(decoder_output)
        
        return output

def create_mask(src, tgt, pad_idx=0):
    """创建掩码"""
    # 源序列掩码（padding掩码）
    src_mask = (src != pad_idx).unsqueeze(1).unsqueeze(2)
    
    # 目标序列掩码（padding掩码 + 未来掩码）
    tgt_pad_mask = (tgt != pad_idx).unsqueeze(1).unsqueeze(2)
    tgt_len = tgt.size(1)
    tgt_sub_mask = torch.tril(torch.ones(tgt_len, tgt_len)).bool()
    tgt_mask = tgt_pad_mask & tgt_sub_mask
    
    return src_mask, tgt_mask

# 测试代码
if __name__ == "__main__":
    print("=== Transformer 模型测试 ===")
    
    # 超参数
    BATCH_SIZE = 4
    SEQ_LEN = 10
    VOCAB_SIZE = 1000
    D_MODEL = 512
    NUM_HEADS = 8
    NUM_LAYERS = 6
    
    # 创建模型
    model = Transformer(
        src_vocab_size=VOCAB_SIZE,
        tgt_vocab_size=VOCAB_SIZE,
        d_model=D_MODEL,
        num_heads=NUM_HEADS,
        num_layers=NUM_LAYERS
    )
    
    print(f"模型参数量: {sum(p.numel() for p in model.parameters()):,}")
    
    # 创建模拟数据
    src = torch.randint(1, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    tgt = torch.randint(1, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    
    print(f"输入形状: src={src.shape}, tgt={tgt.shape}")
    
    # 创建掩码
    src_mask, tgt_mask = create_mask(src, tgt)
    
    # 前向传播
    output = model(src, tgt, src_mask, tgt_mask)
    
    print(f"输出形状: {output.shape}")  # [batch_size, seq_len, vocab_size]
    print(f"输出示例（第一个词的概率分布）:")
    print(f"  形状: {output[0, 0].shape}")
    print(f"  最大值索引: {torch.argmax(output[0, 0]).item()}")
    
    # 训练示例
    print("\n=== 训练示例 ===")
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    
    # 模拟训练步骤
    optimizer.zero_grad()
    loss = criterion(output.view(-1, VOCAB_SIZE), tgt.view(-1))
    loss.backward()
    optimizer.step()
    
    print(f"损失值: {loss.item():.4f}")
    
    # 推理示例（贪婪解码）
    print("\n=== 推理示例 ===")
    model.eval()
    with torch.no_grad():
        # 编码器输出
        src_embedded = model.dropout(model.positional_encoding(model.src_embedding(src)))
        encoder_output = src_embedded
        for layer in model.encoder_layers:
            encoder_output = layer(encoder_output, src_mask)
        
        # 自回归生成
        start_token = torch.ones(BATCH_SIZE, 1, dtype=torch.long) * 2  # 假设2是起始符
        generated = start_token
        
        for i in range(5):  # 生成5个词
            # 解码
            tgt_embedded = model.dropout(model.positional_encoding(model.tgt_embedding(generated)))
            decoder_output = tgt_embedded
            for layer in model.decoder_layers:
                decoder_output = layer(decoder_output, encoder_output, src_mask, None)
            
            # 预测下一个词
            next_token_logits = model.output_layer(decoder_output[:, -1, :])
            next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            generated = torch.cat([generated, next_token], dim=1)
        
        print(f"生成的序列: {generated[0].tolist()}")