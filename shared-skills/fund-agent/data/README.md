# Fund-Agent 数据目录

此目录存储用户的持仓数据和风险状态。

## 文件说明

| 文件 | 用途 | 是否跟踪 |
|------|------|---------|
| `positions.json` | 用户持仓数据 | ❌ 已 gitignore |
| `risk-state.json` | 风险评估状态 | ❌ 已 gitignore |
| `trade-log.json` | 交易日志 | ❌ 已 gitignore |
| `example-positions.json` | 示例数据 | ✅ 公开可见 |

## 数据格式

参考 `example-positions.json` 了解数据结构。

## 安全说明

- 真实持仓数据已通过 `.gitignore` 排除，不会推送到 GitHub
- 如需备份，请使用本地加密存储或私有仓库