---
id: k002
topic: OpenClaw 运维知识
tags: [运维, 知识]
updated: 2026-04-14
---
## 关键认知
- 切换模型后 skills 和定时任务不会丢失（存在文件系统，不依赖模型）
- skill-vetter 用于安装新 skill 前的安全检查
- 备份可通过 git push 到 GitHub 实现
- PKM skill 需要主动调用，不是自动触发

## 每日检查清单
1. 容器状态（docker ps）
2. QQ bot 连接状态（Gateway ready）
3. 模型可用性
4. 磁盘/内存使用
5. 日志异常检查
