# OpenClaw 模型配置

## 当前配置
- **当前模型**: xdclaw-pool/deepseek-v3.2
- **上下文长度**: 128k
- **API 密钥**: 已配置 (models.json)

## 可用模型池
1. xdclaw-pool/deepseek-v3.2 (默认)
2. xdclaw-pool/qwen-plus (128k 上下文)
3. xdclaw-pool/qwen-max (32k 上下文)
4. xdclaw-pool/glm-5 (32k 上下文)
5. xdclaw-pool/qwen-vl-max (支持图像，128k 上下文)

## 切换方法
使用命令: `/session_status(model: "模型名称")`

## 注意事项
- 某些模型可能因权限限制无法使用
- 切换前确认模型在可用列表中

## 相关对话
- 2026-04-13: GitHub 仓库操作与记忆管理

## 标签
#openclaw #models #ai #configuration