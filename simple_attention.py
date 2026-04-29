import numpy as np

def simple_attention(Q, K, V):
    """
    简化的注意力机制实现
    Q: Query 矩阵 [n, d]
    K: Key 矩阵 [n, d]  
    V: Value 矩阵 [n, d]
    """
    # 1. 计算注意力分数
    scores = np.dot(Q, K.T)  # [n, n]
    
    # 2. 缩放
    d_k = Q.shape[1]
    scores = scores / np.sqrt(d_k)
    
    # 3. Softmax 归一化
    exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
    attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
    
    # 4. 加权求和
    output = np.dot(attention_weights, V)  # [n, d]
    
    return output, attention_weights

# 示例：理解"苹果"在不同上下文中的含义
print("=== 注意力机制示例 ===")

# 定义词向量（简化版）
words = {
    "苹果": np.array([0.8, 0.2]),      # 水果特征强
    "吃": np.array([0.9, 0.1]),        # 动作特征
    "手机": np.array([0.1, 0.9]),      # 科技特征强
    "买": np.array([0.7, 0.3])         # 购买动作
}

# 句子1："吃苹果"
sentence1 = ["吃", "苹果"]
Q1 = words["苹果"].reshape(1, -1)  # 查询"苹果"
K1 = np.array([words["吃"], words["苹果"]])  # 键
V1 = K1  # 值

output1, weights1 = simple_attention(Q1, K1, V1)
print(f"句子'吃苹果'中'苹果'的注意力权重: {weights1[0]}")
print(f"  对'吃'的注意力: {weights1[0, 0]:.3f}")
print(f"  对'苹果'的注意力: {weights1[0, 1]:.3f}")
print(f"  输出向量（结合了'吃'的特征）: {output1[0]}")

print("\n" + "="*50 + "\n")

# 句子2："苹果手机"
sentence2 = ["苹果", "手机"]
Q2 = words["苹果"].reshape(1, -1)
K2 = np.array([words["苹果"], words["手机"]])
V2 = K2

output2, weights2 = simple_attention(Q2, K2, V2)
print(f"句子'苹果手机'中'苹果'的注意力权重: {weights2[0]}")
print(f"  对'苹果'的注意力: {weights2[0, 0]:.3f}")
print(f"  对'手机'的注意力: {weights2[0, 1]:.3f}")
print(f"  输出向量（结合了'手机'的特征）: {output2[0]}")

print("\n" + "="*50 + "\n")

# 多头注意力示例
print("=== 多头注意力示例 ===")

def multi_head_attention(Q, K, V, num_heads=2):
    d_model = Q.shape[1]
    d_k = d_model // num_heads
    
    outputs = []
    for i in range(num_heads):
        # 每个头关注不同的子空间
        Q_head = Q[:, i*d_k:(i+1)*d_k]
        K_head = K[:, i*d_k:(i+1)*d_k]
        V_head = V[:, i*d_k:(i+1)*d_k]
        
        output_head, _ = simple_attention(Q_head, K_head, V_head)
        outputs.append(output_head)
    
    # 合并多头
    output = np.concatenate(outputs, axis=1)
    return output

# 测试多头注意力
Q = np.random.randn(3, 8)  # 3个词，8维
K = np.random.randn(3, 8)
V = np.random.randn(3, 8)

output_multi = multi_head_attention(Q, K, V, num_heads=2)
print(f"输入形状: Q={Q.shape}, K={K.shape}, V={V.shape}")
print(f"多头注意力输出形状: {output_multi.shape}")
print(f"每个头关注不同的特征组合，最后合并")

print("\n" + "="*50 + "\n")

# 位置编码示例
print("=== 位置编码示例 ===")

def positional_encoding(seq_len, d_model):
    """生成位置编码"""
    pe = np.zeros((seq_len, d_model))
    
    for pos in range(seq_len):
        for i in range(0, d_model, 2):
            pe[pos, i] = np.sin(pos / (10000 ** (i / d_model)))
            if i + 1 < d_model:
                pe[pos, i + 1] = np.cos(pos / (10000 ** (i / d_model)))
    
    return pe

# 生成位置编码
seq_len = 5
d_model = 4
pe = positional_encoding(seq_len, d_model)

print(f"位置编码矩阵 ({seq_len}个位置, {d_model}维):")
for pos in range(seq_len):
    print(f"  位置{pos}: {pe[pos]}")

print("\n位置编码让模型知道词序：")
print("  '我 爱 你' ≠ '你 爱 我'")
print("  通过不同的位置编码区分")