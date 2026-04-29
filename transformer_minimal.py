"""
Transformer 最小实现 - 纯 Python + NumPy
用于理解核心原理
"""

import numpy as np

class MinimalTransformer:
    """最小化 Transformer 实现"""
    
    def __init__(self, vocab_size=100, d_model=64, num_heads=4):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # 初始化权重（简化版）
        np.random.seed(42)
        self.W_q = np.random.randn(d_model, d_model) * 0.01
        self.W_k = np.random.randn(d_model, d_model) * 0.01
        self.W_v = np.random.randn(d_model, d_model) * 0.01
        self.W_o = np.random.randn(d_model, d_model) * 0.01
        
        self.embedding = np.random.randn(vocab_size, d_model) * 0.01
        
    def attention(self, Q, K, V, mask=None):
        """注意力机制"""
        # 计算注意力分数
        scores = np.dot(Q, K.T) / np.sqrt(self.d_k)
        
        # 应用掩码（如果有）
        if mask is not None:
            scores = scores + mask * -1e9
        
        # Softmax
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        
        # 加权求和
        output = np.dot(attention_weights, V)
        return output, attention_weights
    
    def multi_head_attention(self, x):
        """多头注意力"""
        batch_size, seq_len, _ = x.shape
        
        # 线性变换
        Q = np.dot(x, self.W_q)
        K = np.dot(x, self.W_k)
        V = np.dot(x, self.W_v)
        
        # 分头
        Q = Q.reshape(batch_size, seq_len, self.num_heads, self.d_k)
        K = K.reshape(batch_size, seq_len, self.num_heads, self.d_k)
        V = V.reshape(batch_size, seq_len, self.num_heads, self.d_k)
        
        # 转置以便批量计算
        Q = Q.transpose(0, 2, 1, 3)  # [batch, heads, seq_len, d_k]
        K = K.transpose(0, 2, 1, 3)
        V = V.transpose(0, 2, 1, 3)
        
        # 计算注意力
        scores = np.matmul(Q, K.transpose(0, 1, 3, 2)) / np.sqrt(self.d_k)
        attention = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attention = attention / np.sum(attention, axis=-1, keepdims=True)
        
        # 加权求和
        output = np.matmul(attention, V)
        
        # 合并多头
        output = output.transpose(0, 2, 1, 3).reshape(batch_size, seq_len, self.d_model)
        
        # 输出线性变换
        output = np.dot(output, self.W_o)
        
        return output
    
    def feed_forward(self, x):
        """前馈网络（简化版）"""
        # 实际中会有两个线性层 + 激活函数
        return x  # 简化，直接返回
    
    def layer_norm(self, x):
        """层归一化（简化版）"""
        mean = np.mean(x, axis=-1, keepdims=True)
        std = np.std(x, axis=-1, keepdims=True)
        return (x - mean) / (std + 1e-6)
    
    def encoder_layer(self, x):
        """编码器层"""
        # 自注意力
        attn_output = self.multi_head_attention(x)
        
        # 残差连接 + 层归一化
        x = self.layer_norm(x + attn_output)
        
        # 前馈网络
        ff_output = self.feed_forward(x)
        
        # 残差连接 + 层归一化
        x = self.layer_norm(x + ff_output)
        
        return x
    
    def forward(self, input_ids):
        """前向传播"""
        # 词嵌入
        x = self.embedding[input_ids]  # [batch, seq_len, d_model]
        
        # 编码器层（简化：只有一层）
        output = self.encoder_layer(x)
        
        return output
    
    def generate(self, prompt, max_len=10):
        """生成文本（简化版）"""
        print(f"生成示例（简化版）:")
        print(f"  输入: {prompt}")
        
        # 模拟生成过程
        generated = list(prompt)
        
        for i in range(max_len - len(prompt)):
            # 模拟注意力机制
            print(f"  步骤{i+1}: 模型关注输入中的关键词...")
            
            # 模拟下一个词预测
            next_word = f"[词{i}]"
            generated.append(next_word)
            
            print(f"    生成: '{next_word}'")
        
        print(f"  完整生成: {' '.join(generated)}")
        return generated

def create_causal_mask(seq_len):
    """创建因果掩码（防止看到未来信息）"""
    mask = np.triu(np.ones((seq_len, seq_len)), k=1)
    return mask

# 演示
print("=" * 60)
print("Transformer 最小实现演示")
print("=" * 60)

# 创建模型
model = MinimalTransformer(vocab_size=100, d_model=64, num_heads=4)

print(f"\n1. 模型参数:")
print(f"   词表大小: {model.vocab_size}")
print(f"   模型维度: {model.d_model}")
print(f"   注意力头数: {model.num_heads}")
print(f"   每个头维度: {model.d_k}")

print(f"\n2. 权重矩阵形状:")
print(f"   W_q: {model.W_q.shape}")
print(f"   W_k: {model.W_k.shape}")
print(f"   W_v: {model.W_v.shape}")
print(f"   W_o: {model.W_o.shape}")
print(f"   词嵌入: {model.embedding.shape}")

print(f"\n3. 注意力机制演示:")
# 创建模拟输入
batch_size = 2
seq_len = 5
input_ids = np.random.randint(0, 100, (batch_size, seq_len))

print(f"   输入形状: {input_ids.shape}")
print(f"   示例输入: {input_ids[0]}")

# 前向传播
output = model.forward(input_ids)
print(f"   输出形状: {output.shape}")

print(f"\n4. 因果掩码示例:")
mask = create_causal_mask(seq_len)
print(f"   序列长度: {seq_len}")
print(f"   掩码矩阵（下三角为0，上三角为1）:")
print(mask.astype(int))

print(f"\n5. 注意力权重可视化（简化）:")
# 模拟注意力计算
Q = np.random.randn(seq_len, model.d_k)
K = np.random.randn(seq_len, model.d_k)
V = np.random.randn(seq_len, model.d_k)

output, attention_weights = model.attention(Q, K, V, mask)
print(f"   注意力权重矩阵形状: {attention_weights.shape}")
print(f"   每行和为1（Softmax结果）:")
for i in range(min(3, seq_len)):
    row_sum = np.sum(attention_weights[i])
    print(f"     第{i}行和: {row_sum:.6f}")

print(f"\n6. 文本生成演示:")
model.generate(["我", "爱", "你"], max_len=8)

print(f"\n" + "=" * 60)
print("关键概念总结:")
print("=" * 60)
print("""
1. 词嵌入 (Embedding)
   - 将离散的词ID转换为连续向量
   - 形状: [vocab_size, d_model]

2. 注意力机制 (Attention)
   - Query: 要查询的内容
   - Key: 被查询的内容  
   - Value: 实际返回的内容
   - 公式: Attention(Q,K,V) = softmax(QK^T/√d_k)V

3. 多头注意力 (Multi-Head)
   - 将模型维度分成多个头
   - 每个头学习不同的特征表示
   - 最后合并所有头的输出

4. 残差连接 (Residual)
   - 输出 = 输入 + 子层(输入)
   - 解决梯度消失问题

5. 层归一化 (LayerNorm)
   - 对每个样本单独归一化
   - 加速训练收敛

6. 前馈网络 (FeedForward)
   - 两个线性变换 + 激活函数
   - 增加模型表达能力

7. 位置编码 (Positional Encoding)
   - 使用 sin/cos 函数编码位置信息
   - 让模型知道词序
""")

print(f"\n实际 Transformer 的改进:")
print("""
1. 实际使用 PyTorch/TensorFlow 框架
2. 使用 dropout 防止过拟合
3. 使用学习率预热和衰减
4. 使用梯度裁剪防止梯度爆炸
5. 使用混合精度训练节省内存
6. 使用 Flash Attention 加速计算
7. 使用预训练和微调策略
""")