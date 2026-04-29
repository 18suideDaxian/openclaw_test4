"""
Transformer完整实现（基于《Attention Is All You Need》论文）
包含：Encoder、Decoder、Multi-Head Attention、Positional Encoding等
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np

# ==================== 1. 位置编码 ====================
class PositionalEncoding(nn.Module):
    """
    位置编码：使用正弦余弦函数编码位置信息
    公式：PE(pos, 2i) = sin(pos/10000^(2i/d_model))
         PE(pos, 2i+1) = cos(pos/10000^(2i/d_model))
    """
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        
        # 创建位置编码矩阵 [max_len, d_model]
        pe = torch.zeros(max_len, d_model)
        
        # 位置向量 [max_len, 1]
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        # 频率项：10000^(2i/d_model)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * 
            (-math.log(10000.0) / d_model)
        )
        
        # 正弦部分（偶数位置）
        pe[:, 0::2] = torch.sin(position * div_term)
        # 余弦部分（奇数位置）
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # 添加batch维度：[1, max_len, d_model]
        pe = pe.unsqueeze(0)
        
        # 注册为buffer（不参与训练，但会保存到模型）
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        """
        参数：
            x: [batch_size, seq_len, d_model]
        返回：
            [batch_size, seq_len, d_model] + 位置编码
        """
        # 取前seq_len个位置编码，加到输入上
        return x + self.pe[:, :x.size(1)]


# ==================== 2. 缩放点积注意力 ====================
def scaled_dot_product_attention(q, k, v, mask=None):
    """
    缩放点积注意力
    公式：Attention(Q, K, V) = softmax(QK^T/√d_k)V
    
    参数：
        q: [batch_size, num_heads, seq_len_q, depth]
        k: [batch_size, num_heads, seq_len_k, depth]
        v: [batch_size, num_heads, seq_len_v, depth]
        mask: 可选，[batch_size, 1, 1, seq_len]
    
    返回：
        output: [batch_size, num_heads, seq_len_q, depth]
        attention_weights: [batch_size, num_heads, seq_len_q, seq_len_k]
    """
    # 1. 计算QK^T
    # q: [batch, heads, seq_q, depth]
    # k: [batch, heads, seq_k, depth] -> 转置最后两维：[batch, heads, depth, seq_k]
    matmul_qk = torch.matmul(q, k.transpose(-2, -1))  # [batch, heads, seq_q, seq_k]
    
    # 2. 缩放：除以√d_k
    d_k = q.size(-1)
    scaled_attention_logits = matmul_qk / math.sqrt(d_k)
    
    # 3. 应用掩码（如果有）
    if mask is not None:
        # 将mask中为1的位置替换为非常大的负数，softmax后会接近0
        scaled_attention_logits = scaled_attention_logits.masked_fill(mask == 0, -1e9)
    
    # 4. softmax得到注意力权重
    attention_weights = F.softmax(scaled_attention_logits, dim=-1)  # [batch, heads, seq_q, seq_k]
    
    # 5. 乘以V得到输出
    output = torch.matmul(attention_weights, v)  # [batch, heads, seq_q, depth]
    
    return output, attention_weights


# ==================== 3. 多头注意力 ====================
class MultiHeadAttention(nn.Module):
    """
    多头注意力机制
    将输入分成多个头，分别计算注意力，然后合并
    """
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0, "d_model必须能被num_heads整除"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.depth = d_model // num_heads  # 每个头的维度
        
        # 线性变换层：生成Q、K、V
        self.wq = nn.Linear(d_model, d_model)  # W^Q
        self.wk = nn.Linear(d_model, d_model)  # W^K
        self.wv = nn.Linear(d_model, d_model)  # W^V
        
        # 输出线性层：W^O
        self.dense = nn.Linear(d_model, d_model)
        
    def split_heads(self, x, batch_size):
        """
        将输入分成多个头
        [batch_size, seq_len, d_model] -> [batch_size, num_heads, seq_len, depth]
        """
        x = x.view(batch_size, -1, self.num_heads, self.depth)
        return x.transpose(1, 2)  # [batch_size, num_heads, seq_len, depth]
    
    def forward(self, q, k, v, mask=None):
        """
        参数：
            q, k, v: [batch_size, seq_len, d_model]
            mask: 可选，[batch_size, 1, 1, seq_len]
        
        返回：
            output: [batch_size, seq_len, d_model]
            attention_weights: [batch_size, num_heads, seq_len_q, seq_len_k]
        """
        batch_size = q.size(0)
        
        # 1. 线性变换得到Q、K、V
        q = self.wq(q)  # [batch, seq_q, d_model]
        k = self.wk(k)  # [batch, seq_k, d_model]
        v = self.wv(v)  # [batch, seq_v, d_model]
        
        # 2. 分成多个头
        q = self.split_heads(q, batch_size)  # [batch, heads, seq_q, depth]
        k = self.split_heads(k, batch_size)  # [batch, heads, seq_k, depth]
        v = self.split_heads(v, batch_size)  # [batch, heads, seq_v, depth]
        
        # 3. 计算缩放点积注意力
        scaled_attention, attention_weights = scaled_dot_product_attention(
            q, k, v, mask
        )  # scaled_attention: [batch, heads, seq_q, depth]
        
        # 4. 合并多个头
        # 转置： [batch, heads, seq_q, depth] -> [batch, seq_q, heads, depth]
        scaled_attention = scaled_attention.transpose(1, 2)
        # 合并： [batch, seq_q, heads, depth] -> [batch, seq_q, d_model]
        concat_attention = scaled_attention.reshape(
            batch_size, -1, self.d_model
        )
        
        # 5. 输出线性变换
        output = self.dense(concat_attention)  # [batch, seq_q, d_model]
        
        return output, attention_weights


# ==================== 4. 前馈网络 ====================
class FeedForwardNetwork(nn.Module):
    """
    前馈网络：FFN(x) = max(0, xW1 + b1)W2 + b2
    通常：d_ff = 4 * d_model
    """
    def __init__(self, d_model, d_ff=2048):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)  # 扩大维度
        self.linear2 = nn.Linear(d_ff, d_model)  # 恢复维度
        self.dropout = nn.Dropout(0.1)
        
    def forward(self, x):
        """
        参数：
            x: [batch_size, seq_len, d_model]
        返回：
            [batch_size, seq_len, d_model]
        """
        # 扩大维度 -> ReLU -> 恢复维度
        return self.linear2(self.dropout(F.relu(self.linear1(x))))


# ==================== 5. Encoder层 ====================
class EncoderLayer(nn.Module):
    """
    Encoder层：
    1. Multi-Head Self-Attention
    2. Add & Norm
    3. Feed Forward Network
    4. Add & Norm
    """
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        
        self.mha = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForwardNetwork(d_model, d_ff)
        
        # 层归一化
        self.layernorm1 = nn.LayerNorm(d_model, eps=1e-6)
        self.layernorm2 = nn.LayerNorm(d_model, eps=1e-6)
        
        # Dropout
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        
    def forward(self, x, mask=None):
        """
        参数：
            x: [batch_size, seq_len, d_model]
            mask: 可选，用于padding mask
        
        返回：
            [batch_size, seq_len, d_model]
        """
        # 1. Multi-Head Self-Attention
        attn_output, _ = self.mha(x, x, x, mask)  # 自注意力：Q=K=V=x
        attn_output = self.dropout1(attn_output)
        
        # 2. Add & Norm (残差连接 + 层归一化)
        out1 = self.layernorm1(x + attn_output)
        
        # 3. Feed Forward Network
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output)
        
        # 4. Add & Norm
        out2 = self.layernorm2(out1 + ffn_output)
        
        return out2


# ==================== 6. Decoder层 ====================
class DecoderLayer(nn.Module):
    """
    Decoder层：
    1. Masked Multi-Head Self-Attention
    2. Add & Norm
    3. Multi-Head Cross-Attention (Encoder-Decoder Attention)
    4. Add & Norm
    5. Feed Forward Network
    6. Add & Norm
    """
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        
        # 两个注意力层
        self.masked_mha = MultiHeadAttention(d_model, num_heads)  # 掩码自注意力
        self.cross_mha = MultiHeadAttention(d_model, num_heads)   # 交叉注意力
        
        # 前馈网络
        self.ffn = FeedForwardNetwork(d_model, d_ff)
        
        # 三个层归一化
        self.layernorm1 = nn.LayerNorm(d_model, eps=1e-6)
        self.layernorm2 = nn.LayerNorm(d_model, eps=1e-6)
        self.layernorm3 = nn.LayerNorm(d_model, eps=1e-6)
        
        # 三个Dropout
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.dropout3 = nn.Dropout(dropout)
        
    def forward(self, x, enc_output, look_ahead_mask=None, padding_mask=None):
        """
        参数：
            x: [batch_size, target_seq_len, d_model] - Decoder输入
            enc_output: [batch_size, input_seq_len, d_model] - Encoder输出
            look_ahead_mask: 防止看到未来信息的掩码
            padding_mask: padding掩码
        
        返回：
            [batch_size, target_seq_len, d_model]
        """
        # 1. Masked Multi-Head Self-Attention
        attn1, attn_weights_block1 = self.masked_mha(
            x, x, x, look_ahead_mask
        )
        attn1 = self.dropout1(attn1)
        
        # 2. Add & Norm
        out1 = self.layernorm1(attn1 + x)
        
        # 3. Multi-Head Cross-Attention
        # Q来自Decoder，K、V来自Encoder
        attn2, attn_weights_block2 = self.cross_mha(
            out1, enc_output, enc_output, padding_mask
        )
        attn2 = self.dropout2(attn2)
        
        # 4. Add & Norm
        out2 = self.layernorm2(attn2 + out1)
        
        # 5. Feed Forward Network
        ffn_output = self.ffn(out2)
        ffn_output = self.dropout3(ffn_output)
        
        # 6. Add & Norm
        out3 = self.layernorm3(ffn_output + out2)
        
        return out3, attn_weights_block1, attn_weights_block2


# ==================== 7. Encoder ====================
class Encoder(nn.Module):
    """
    Encoder：多个Encoder层堆叠
    """
    def __init__(self, num_layers, d_model, num_heads, d_ff, input_vocab_size,
                 max_position_encoding, dropout=0.1):
        super().__init__()
        
        self.d_model = d_model
        self.num_layers = num_layers
        
        # 词嵌入层
        self.embedding = nn.Embedding(input_vocab_size, d_model)
        
        # 位置编码
        self.pos_encoding = PositionalEncoding(d_model, max_position_encoding)
        
        # 多个Encoder层
        self.enc_layers = nn.ModuleList([
            EncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x, mask=None):
        """
        参数：
            x: [batch_size, input_seq_len] - 输入序列
            mask: 可选，padding mask
        
        返回：
            [batch_size, input_seq_len, d_model]
        """
        seq_len = x.size(1)
        
        # 1. 词嵌入
        x = self.embedding(x)  # [batch, seq_len, d_model]
        x *= math.sqrt(self.d_model)  # 缩放，保持方差稳定
        
        # 2. 位置编码
        x = self.pos_encoding(x)
        x = self.dropout(x)
        
        # 3. 通过多个Encoder层
        for i in range(self.num_layers):
            x = self.enc_layers[i](x, mask)
        
        return x  # [batch, seq_len, d_model]


# ==================== 8. Decoder ====================
class Decoder(nn.Module):
    """
    Decoder：多个Decoder层堆叠
    """
    def __init__(self, num_layers, d_model, num_heads, d_ff, target_vocab_size,
                 max_position_encoding, dropout=0.1):
        super().__init__()
        
        self.d_model = d_model
        self.num_layers = num_layers
        
        # 词嵌入层
        self.embedding = nn.Embedding(target_vocab_size, d_model)
        
        # 位置编码
        self.pos_encoding = PositionalEncoding(d_model, max_position_encoding)
        
        # 多个Decoder层
        self.dec_layers = nn.ModuleList([
            DecoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x, enc_output, look_ahead_mask=None, padding_mask=None):
        """
        参数：
            x: [batch_size, target_seq_len] - 目标序列
            enc_output: [batch_size, input_seq_len, d_model] - Encoder输出
            look_ahead_mask: 防止看到未来信息的掩码
            padding_mask: padding掩码
        
        返回：
            [batch_size, target_seq_len, d_model]
            attention_weights: 字典，包含各层的注意力权重
        """
        seq_len = x.size(1)
        attention_weights = {}
        
        # 1. 词嵌入
        x = self.embedding(x)  # [batch, seq_len, d_model]
        x *= math.sqrt(self.d_model)  # 缩放
        
        # 2. 位置编码
        x = self.pos_encoding(x)
        x = self.dropout(x)
        
        # 3. 通过多个Decoder层
        for i in range(self.num_layers):
            x, block1, block2 = self.dec_layers[i](
                x, enc_output, look_ahead_mask, padding_mask
            )
            
            # 保存注意力权重
            attention_weights[f'decoder_layer{i+1}_block1'] = block1
            attention_weights[f'decoder_layer{i+1}_block2'] = block2
        
        return x, attention_weights


# ==================== 9. Transformer ====================
class Transformer(nn.Module):
    """
    完整的Transformer模型
    """
    def __init__(self, num_layers, d_model, num_heads, d_ff,
                 input_vocab_size, target_vocab_size,
                 max_position_encoding=5000, dropout=0.1):
        super().__init__()
        
        # Encoder
        self.encoder = Encoder(
            num_layers, d_model, num_heads, d_ff,
            input_vocab_size, max_position_encoding, dropout
        )
        
        # Decoder
        self.decoder = Decoder(
            num_layers, d_model, num_heads, d_ff,
            target_vocab_size, max_position_encoding, dropout
        )
        
        # 最后的线性层：将Decoder输出映射到词汇表
        self.final_layer = nn.Linear(d_model, target_vocab_size)
        
    def forward(self, inp, tar, enc_padding_mask=None,
                look_ahead_mask=None, dec_padding_mask=None):
        """
        参数：
            inp: [batch_size, input_seq_len] - 输入序列
            tar: [batch_size, target_seq_len] - 目标序列
            enc_padding_mask: Encoder的padding mask
            look_ahead_mask: Decoder的look-ahead mask
            dec_padding_mask: Decoder的padding mask
        
        返回：
            predictions: [batch_size, target_seq_len, target_vocab_size]
            attention_weights: 注意力权重字典
        """
        # 1. Encoder
        enc_output = self.encoder(inp, enc_padding_mask)  # [batch, inp_seq_len, d_model]
        
        # 2. Decoder
        dec_output, attention_weights = self.decoder(
            tar, enc_output, look_ahead_mask, dec_padding_mask
        )  # [batch, tar_seq_len, d_model]
        
        # 3. 最后的线性层
        predictions = self.final_layer(dec_output)  # [batch, tar_seq_len, target_vocab_size]
        
        return predictions, attention_weights


# ==================== 10. 掩码生成函数 ====================
def create_padding_mask(seq):
    """
    创建padding mask
    参数：
        seq: [batch_size, seq_len]
    返回：
        mask: [batch_size, 1, 1, seq_len]
        其中padding位置为0，非padding位置为1
    """
    # 找到padding位置（假设padding值为0）
    mask = (seq != 0).unsqueeze(1).unsqueeze(2)  # [batch, 1, 1, seq_len]
    return mask.float()


def create_look_ahead_mask(size):
    """
    创建look-ahead mask（防止看到未来信息）
    参数：
        size: 序列长度
    返回：
        mask: [size, size]
        下三角矩阵，对角线及以下为1，以上为0
    """
    # 创建下三角矩阵
    mask = torch.tril(torch.ones(size, size))
    return mask  # [size, size]


# ==================== 11. 示例：机器翻译 ====================
def create_masks(inp, tar):
    """
    为机器翻译任务创建所有需要的mask
    """
    # Encoder padding mask
    enc_padding_mask = create_padding_mask(inp)
    
    # Decoder padding mask（用于第二个注意力层）
    dec_padding_mask = create_padding_mask(inp)
    
    # Decoder look-ahead mask（用于第一个注意力层）
    look_ahead_mask = create_look_ahead_mask(tar.size(1))
    dec_target_padding_mask = create_padding_mask(tar)
    
    # 组合look-ahead mask和padding mask
    combined_mask = torch.max(dec_target_padding_mask, look_ahead_mask)
    
    return enc_padding_mask, combined_mask, dec_padding_mask


# ==================== 12. 训练示例 ====================
def train_step(model, optimizer, loss_fn, inp, tar):
    """
    单个训练步骤
    """
    # 设置训练模式
    model.train()
    
    # 创建mask
    enc_padding_mask, combined_mask, dec_padding_mask = create_masks(inp, tar)
    
    # 前向传播
    predictions, _ = model(
        inp, tar[:, :-1],  # 目标序列去掉最后一个token
        enc_padding_mask,
        combined_mask,
        dec_padding_mask
    )
    
    # 计算损失
    # 目标序列去掉第一个token（<start>标记）
    loss = loss_fn(
        predictions.reshape(-1, predictions.size(-1)),
        tar[:, 1:].reshape(-1)
    )
    
    # 反向传播
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    return loss.item()


# ==================== 13. 推理示例 ====================
def translate(model, sentence, tokenizer, max_length=50):
    """
    使用训练好的模型进行翻译
    """
    model.eval()
    
    # 编码输入句子
    encoder_input = tokenizer.encode(sentence)
    encoder_input = torch.tensor(encoder_input).unsqueeze(0)  # [1, seq_len]
    
    # 创建Encoder mask
    encoder_padding_mask = create_padding_mask(encoder_input)
    
    # Encoder前向传播
    encoder_output = model.encoder(encoder_input, encoder_padding_mask)
    
    # Decoder输入从<start>标记开始
    decoder_input = torch.tensor([[tokenizer.vocab['<start>']]])  # [1, 1]
    
    output_tokens = []
    
    for i in range(max_length):
        # 创建Decoder mask
        look_ahead_mask = create_look_ahead_mask(decoder_input.size(1))
        
        # Decoder前向传播
        predictions, _ = model.decoder(
            decoder_input, encoder_output,
            look_ahead_mask, encoder_padding_mask
        )
        
        # 预测下一个token
        predictions = model.final_layer(predictions)  # [1, seq_len, vocab_size]
        next_token_logits = predictions[:, -1, :]  # 取最后一个位置的logits
        next_token = torch.argmax(next_token_logits, dim=-1).item()
        
        # 如果是<end>标记，停止
        if next_token == tokenizer.vocab['<end>']:
            break
        
        output_tokens.append(next_token)
        
        # 将预测的token添加到Decoder输入
        decoder_input = torch.cat([
            decoder_input,
            torch.tensor([[next_token]])
        ], dim=1)
    
    # 解码为文本
    translated_text = tokenizer.decode(output_tokens)
    
    return translated_text


# ==================== 14. 模型配置示例 ====================
def create_transformer_model():
    """
    创建Transformer模型（基于论文的超参数）
    """
    # 论文中的超参数（base model）
    num_layers = 6          # Encoder和Decoder各有6层
    d_model = 512           # 模型维度
    num_heads = 8           # 注意力头数
    d_ff = 2048             # 前馈网络中间维度
    
    # 词汇表大小（示例）
    input_vocab_size = 10000   # 输入语言词汇表大小
    target_vocab_size = 10000  # 目标语言词汇表大小
    
    # 创建模型
    model = Transformer(
        num_layers=num_layers,
        d_model=d_model,
        num_heads=num_heads,
        d_ff=d_ff,
        input_vocab_size=input_vocab_size,
        target_vocab_size=target_vocab_size
    )
    
    return model


# ==================== 15. 测试代码 ====================
if __name__ == "__main__":
    print("=== Transformer完整实现测试 ===\n")
    
    # 1. 测试位置编码
    print("1. 测试位置编码:")
    pos_enc = PositionalEncoding(d_model=512, max_len=10)
    x = torch.randn(1, 5, 512)  # [batch=1, seq_len=5, d_model=512]
    output = pos_enc(x)
    print(f"   输入形状: {x.shape}")
    print(f"   输出形状: {output.shape}")
    print(f"   位置编码已添加: {not torch.allclose(x, output)}\n")
    
    # 2. 测试缩放点积注意力
    print("2. 测试缩放点积注意力:")
    batch_size = 2
    num_heads = 8
    seq_len_q = 5
    seq_len_k = 5
    depth = 64  # d_model / num_heads = 512/8 = 64
    
    q = torch.randn(batch_size, num_heads, seq_len_q, depth)
    k = torch.randn(batch_size, num_heads, seq_len_k, depth)
    v = torch.randn(batch_size, num_heads, seq_len_k, depth)
    
    output, attn_weights = scaled_dot_product_attention(q, k, v)
    print(f"   Q形状: {q.shape}")
    print(f"   注意力输出形状: {output.shape}")
    print(f"   注意力权重形状: {attn_weights.shape}")
    print(f"   注意力权重和为1: {torch.allclose(attn_weights.sum(dim=-1), torch.ones_like(attn_weights.sum(dim=-1)))}\n")
    
    # 3. 测试多头注意力
    print("3. 测试多头注意力:")
    mha = MultiHeadAttention(d_model=512, num_heads=8)
    x = torch.randn(batch_size, seq_len_q, 512)
    output, attn_weights = mha(x, x, x)
    print(f"   输入形状: {x.shape}")
    print(f"   输出形状: {output.shape}")
    print(f"   注意力权重形状: {attn_weights.shape}\n")
    
    # 4. 测试前馈网络
    print("4. 测试前馈网络:")
    ffn = FeedForwardNetwork(d_model=512, d_ff=2048)
    x = torch.randn(batch_size, seq_len_q, 512)
    output = ffn(x)
    print(f"   输入形状: {x.shape}")
    print(f"   输出形状: {output.shape}\n")
    
    # 5. 测试Encoder层
    print("5. 测试Encoder层:")
    encoder_layer = EncoderLayer(d_model=512, num_heads=8, d_ff=2048)
    x = torch.randn(batch_size, seq_len_q, 512)
    output = encoder_layer(x)
    print(f"   输入形状: {x.shape}")
    print(f"   输出形状: {output.shape}\n")
    
    # 6. 测试Decoder层
    print("6. 测试Decoder层:")
    decoder_layer = DecoderLayer(d_model=512, num_heads=8, d_ff=2048)
    x = torch.randn(batch_size, seq_len_q, 512)  # Decoder输入
    enc_output = torch.randn(batch_size, seq_len_q, 512)  # Encoder输出
    
    # 创建look-ahead mask
    look_ahead_mask = create_look_ahead_mask(seq_len_q)
    look_ahead_mask = look_ahead_mask.unsqueeze(0).unsqueeze(0)  # [1, 1, seq_len, seq_len]
    
    output, attn1, attn2 = decoder_layer(x, enc_output, look_ahead_mask)
    print(f"   Decoder输入形状: {x.shape}")
    print(f"   Encoder输出形状: {enc_output.shape}")
    print(f"   Decoder输出形状: {output.shape}")
    print(f"   掩码自注意力权重形状: {attn1.shape}")
    print(f"   交叉注意力权重形状: {attn2.shape}\n")
    
    # 7. 测试完整Transformer
    print("7. 测试完整Transformer:")
    model = create_transformer_model()
    
    # 模拟输入
    batch_size = 4
    input_seq_len = 10
    target_seq_len = 12
    
    inp = torch.randint(0, 10000, (batch_size, input_seq_len))
    tar = torch.randint(0, 10000, (batch_size, target_seq_len))
    
    # 创建mask
    enc_padding_mask, combined_mask, dec_padding_mask = create_masks(inp, tar)
    
    # 前向传播
    predictions, attention_weights = model(
        inp, tar[:, :-1],  # 目标序列去掉最后一个token
        enc_padding_mask,
        combined_mask,
        dec_padding_mask
    )
    
    print(f"   输入形状: {inp.shape}")
    print(f"   目标形状: {tar.shape}")
    print(f"   预测形状: {predictions.shape}")
    print(f"   注意力权重数量: {len(attention_weights)}")
    
    # 8. 模型参数统计
    print("\n8. 模型参数统计:")
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"   总参数量: {total_params:,}")
    print(f"   可训练参数量: {trainable_params:,}")
    
    # 9. 测试训练步骤
    print("\n9. 测试训练步骤:")
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    loss_fn = nn.CrossEntropyLoss(ignore_index=0)  # 忽略padding
    
    loss = train_step(model, optimizer, loss_fn, inp, tar)
    print(f"   训练损失: {loss:.4f}")
    
    print("\n=== 测试完成 ===")
    print("\n这个实现包含了Transformer的所有核心组件：")
    print("1. 位置编码 (Positional Encoding)")
    print("2. 缩放点积注意力 (Scaled Dot-Product Attention)")
    print("3. 多头注意力 (Multi-Head Attention)")
    print("4. 前馈网络 (Feed Forward Network)")
    print("5. Encoder层 (Encoder Layer)")
    print("6. Decoder层 (Decoder Layer)")
    print("7. 完整Transformer模型")
    print("8. 掩码生成函数")
    print("9. 训练和推理示例")
    
    print("\n使用方法：")
    print("1. 创建模型: model = create_transformer_model()")
    print("2. 准备数据: 将文本转换为token ID")
    print("3. 创建mask: enc_mask, combined_mask, dec_mask = create_masks(inp, tar)")
    print("4. 前向传播: predictions, attn = model(inp, tar, enc_mask, combined_mask, dec_mask)")
    print("5. 训练: 使用train_step函数")
    print("6. 推理: 使用translate函数")
    print("3. 添加学习率调度")
    print("1. 添加更复杂的tokenizer")
    print("2. 实现数据加载和预处理")
    print("3. 添加学习率
    print("
注意：这是一个教学实现，实际使用时需要：")
    print("1. 添加更复杂的tokenizer")
    print("2. 实现数据加载和预处理")
    print("3. 添加学习率调度")
    print("4. 添加模型保存和加载")
    print("5. 添加评估指标")
    print("6. 使用更大的数据集训练")
    
    print("
=== 代码运行完成 ===")
