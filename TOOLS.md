# TOOLS.md - 本地环境速查

## 本机（1号机）
- **OS**: Linux 5.10 (Alibaba Cloud, x64)
- **IP**: 47.57.13.82
- **CPU**: 8核 / **内存**: 14GB / **磁盘**: 197GB (67%已用)
- **角色**: Xdclaw 主服务器 + OpenClaw 主实例

## SSH
- 2号机（Mac mini，无 OpenClaw）：`ssh apple@100.109.210.40`（免密已配）
- 3号机（美国VPS）：`ssh root@104.168.94.238`（密码见 .env VPS3_SSH_PASSWORD）
- 5号机（宿主OpenClaw/Telegram，⚠️与Xdclaw无关！禁止操作Xdclaw相关）：`ssh -i ~/.ssh/openclaw_saas_hk root@43.99.48.34`

## 常用端口（本机）
- OpenClaw Gateway：localhost:18789
- New API（模型转发）：localhost:3000
- SearXNG（搜索）：localhost:8888
- Qdrant（向量库）：localhost:6333/6334
- Changedetection：localhost:5000

## Docker 容器（本机）
- xdclaw-u-* — Xdclaw 用户实例（10个左右）
- new-api — 模型 API 转发
- xdclaw-searxng / redis — 搜索引擎
- changedetection — 网页变更监控
- qdrant — 向量数据库
- memu-api-server — 案件分析 API

## URL/搜索 决策链（遇到链接或搜索需求时，按顺序走）

### 收到 URL 时
1. **X/Twitter 链接** → `python3 /root/clawd/x-tweet-fetcher/scripts/fetch_tweet.py --url "URL" --text-only`（首选，最快最稳）
   - 备选：`curl -s "https://r.jina.ai/URL"`
2. **微信公众号** → agent-reach 的 camoufox 方式（jina 读不了微信）
3. **B站/YouTube** → `yt-dlp --dump-json "URL"`（元数据）或 jina.ai
4. **其他链接** → `web_fetch` 先试；失败 → `curl -s "https://r.jina.ai/URL"`
5. **以上全失败** → camofox 浏览器打开

### 搜索时
1. **通用搜索** → `web_search`（Brave API，内置工具）
2. **Twitter 搜索** → x-tweet-fetcher 或 web_search "site:x.com query"
3. **小红书/微博/雪球** → agent-reach 的 mcporter 命令（见 SKILL.md）
4. **GitHub** → `gh` CLI
5. **技术问题** → web_search + web_fetch 组合

### 已装工具清单
- **x-tweet-fetcher**：`/root/clawd/x-tweet-fetcher/scripts/fetch_tweet.py` — Twitter/X 专用，秒出
- **agent-reach** skill：`~/.openclaw/skills/agent-reach/SKILL.md`
  - jina.ai（任意 URL）、mcporter（小红书/微博/雪球/抖音/LinkedIn）
  - yt-dlp（YouTube/B站）、gh（GitHub）、feedparser（RSS）
- **web_search**：Brave API（内置工具，直接调用）
- **web_fetch**：内置
- **camofox**：反检测浏览器（最后手段）
- **SearXNG**：localhost:8888（备用搜索）

### ⚠️ 不要犯的错
- ❌ 不要先用 web_fetch 抓 X/Twitter（必失败）
- ❌ 不要试 nitter（已死）
- ❌ 不要在有现成工具时绕远路
- ✅ 先查这个决策链，再动手

## 临时文件管理

- **目录**: `tmp/`（工作区根目录下）
- **规则**: skill 生成的文档、临时输出、中间文件一律放 `tmp/`
- **git**: `tmp/` 已在 `.gitignore` 中，不会进版本控制
- **清理**: 超过 7 天的文件可安全删除
- **不要**: 不要把临时文件放到工作区根目录或 memory/ 下

## TTS
- 待配置

## 摄像头
- 无

---
*更新: 2026-03-22 迁移至1号机*
