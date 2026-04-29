# MEMORY.md — 1号记忆系统

> 受 [MSA（Memory Sparse Attention）](https://github.com/EverMind-AI/MSA) 启发的三层稀疏记忆架构。
> 核心原则：**压缩存储、稀疏加载、多跳推理**。

## 架构总览

```
工作台层 (Hot):  NOW.md + wal-buffer.md — 每次session必读
时间轴层 (Warm): memory/YYYY-MM-DD.md + reflections/ — 按需加载近1-2天
知识图谱层 (Compressed): core.md + active.md + INDEX.md + lessons/ + decisions/ — 索引常驻，内容按需
冷存储 (Cold): .archive/ + .vector/ — 语义检索兜底
```

## 启动协议（Startup Protocol · 唯一权威）

> 此协议是 **唯一权威启动顺序**。AGENTS.md 中的 Memory 段指向此处，不再独立定义。

```
1. NOW.md               ← 恢复工作台（热记忆）
2. memory/core.md       ← 核心事实+红线（必读）
3. memory/active.md     ← 在做什么（必读）
4. memory/wal-buffer.md ← 检查未落盘的 WAL（必读，有pending则先flush）
5. memory/YYYY-MM-DD.md ← 当天日志（必读；若不存在则创建并写一条初始化日志）
6. 按需: memory/INDEX.md → memory/lessons/ / memory/decisions/ / memory/projects/
7. 困惑时: SOUL.md + USER.md
```

### 边界情况规则
- **第一天无日志**: 启动时若 `memory/YYYY-MM-DD.md` 不存在，创建并写入 `[时间] session启动，日志初始化`
- **WAL 多条指向同一文件**: 按时间顺序依次追加，不合并，不去重
- **WAL 目标文件不存在**: 自动创建该文件后写入
- **active.md 待沉淀但 lessons 文件不存在**: 创建对应 lessons 文件，写入沉淀内容，然后删除 active 条目

### 路径约定（Canonical Path）
- **外部引用统一用** `memory/...`（如 `memory/lessons/`、`memory/INDEX.md`）
- `memory/knowledge/...` 仅为实现目录，不在文档中引用
- 符号链接只在 `memory/` 层设置，`knowledge/` 子目录内不放链接

## 写入路由

| 写到哪 | 什么时候 | 规则 |
|--------|---------|------|
| `NOW.md` | 状态变化时 | **唯一可覆写**的文件 |
| `wal-buffer.md` | 重要记忆产生时 | 先写WAL，心跳时flush |
| `memory/YYYY-MM-DD.md` | 对话中 | append-only，用memlog |
| `memory/core.md` | 极少 | 局部修改，不整段重写 |
| `memory/active.md` | 项目变动时 | 完成→沉淀lessons→删条目 |
| `memory/lessons/` | 经验总结时 | 按主题聚合 |
| `memory/decisions/` | 重大决策时 | 含背景/方案/决策/原因 |
| `memory/.archive/` | 心跳维护时 | >30天日志自动归档 |

## 记忆压缩循环（Compaction Loop）

```
每日日志 ──心跳提炼──→ reflections/ ──积累──→ lessons/decisions
    │                                            │
    └──>30天──→ .archive/              core.md ←─┘(红线/永久事实)
                    │
              .vector/ ←── 语义索引（冷存储路由）
```

## 禁止事项

- ❌ 不用 `write` 覆盖 `memory/*.md`（除 NOW.md）
- ❌ 不写无信息量的流水账
- ❌ 不在记忆里硬编码一次性命令输出
- ❌ 不在群聊/共享环境加载 MEMORY.md

## Memory Interleave 协议（多跳推理）

当单次检索不够时，交替"检索→扩展→生成→发现缺口→再检索"。最多 3 轮，每轮新增加载不超过 3 个文件。第 3 轮才允许访问冷存储或外部搜索。

## Adaptive Top-k 加载预算

简单查询: core.md + 0-1 文件 | 项目工作: core.md + active.md + 1-3 文件 | 复杂推理: + INDEX.md + 3-5 文件 | 全局维护: 全量扫描
原则: 先少加载，不够再追加。

## 凭证

`~/clawd/.env`（勿提交 Git）

## 导航

- → **[知识库索引](memory/INDEX.md)** — 全量知识导航
- → **[核心记忆](memory/core.md)** — 身份/拓扑/红线
- → **[活跃项目](memory/active.md)** — 当前在做什么
- → **[当前状态](NOW.md)** — 实时工作台
- → **[蓝图原文](memory/MEMORY_BLUEPRINT.md)** — 设计依据
