# HEARTBEAT.md — 1号心跳

> 每次被唤醒时想一想"现在最值得做什么"。

## Phase 0: 感知

读 `memory/thinking-state.json`，判断距上次用户消息多久。

判断阶段：
- **在线**（< 30min）→ Phase 1
- **短离**（30min-2h）→ Phase 1 + 2
- **深度空闲**（> 2h）→ Phase 1 + 2 + 3
- **深夜**（23:00-08:00）→ 仅 Phase 1
- **请求数 > 300** → 仅 Phase 1
- **日期变更** → 重置 todayRequestCount

## Phase 1: 系统守护（每次必跑）

**⚡ 预警检查**（每次必跑，发现问题立即通知 Discord #虾广场运营）：
```bash
# A) Brave Search API 有效性（抽查一个 key）
KEY=$(python3 -c "import json; d=json.load(open('/opt/xdclaw/users/u-hukid-ceef3a/openclaw.json')); print(d.get('tools',{}).get('web',{}).get('search',{}).get('apiKey',''))" 2>/dev/null)
status=$(curl -s --max-time 8 "https://api.search.brave.com/res/v1/web/search?q=test&count=1" -H "Accept: application/json" -H "X-Subscription-Token: $KEY" | python3 -c "import json,sys; d=json.load(sys.stdin); print('invalid' if d.get('type')=='ErrorResponse' else 'ok')" 2>/dev/null)
if [ "$status" = "invalid" ]; then echo "ALERT: Brave API Key 已失效 ($KEY)"; fi

# B) New API root 用户余额（低于 $500 预警）
quota=$(sqlite3 /data/new-api/one-api.db "SELECT quota FROM users WHERE id=1" 2>/dev/null)
if [ -n "$quota" ] && [ "$quota" -lt 250000000 ]; then
  dollar=$((quota/500000))
  echo "ALERT: New API root 余额不足 \$$dollar，需补充"
fi

# C) 容器 token 余额（低于 $100 预警）
sqlite3 /data/new-api/one-api.db "SELECT name, remain_quota FROM tokens WHERE name LIKE 'xdclaw-u-%' AND COALESCE(unlimited_quota,0)=0 AND remain_quota < 50000000 AND remain_quota > 0" 2>/dev/null | while IFS='|' read name quota; do
  dollar=$((quota/500000))
  echo "ALERT: $name 余额偏低 \$$dollar"
done
```
- 有 ALERT → 写日志 + 通知老板（Discord #虾广场运营）
- 无 ALERT → 不写日志，静默跳过

**Xdclaw 容器巡查**（本机，每次必查）：
```
# 1) 检查所有容器是否运行
docker ps --filter 'name=xdclaw-u-' --format '{{.Names}} {{.Status}}' | sort

# 2) 检查 qqbot 插件加载失败
for c in $(docker ps --filter 'name=xdclaw-u-' --format '{{.Names}}'); do
  errs=$(docker logs --tail 20 $c 2>&1 | grep -c 'Cannot find module')
  if [ "$errs" -gt 0 ]; then echo "BROKEN: $c (missing module)"; fi
done

# 3) 检查 IP 白名单 / 连接失败
for c in $(docker ps --filter 'name=xdclaw-u-' --format '{{.Names}}'); do
  wl=$(docker logs --tail 20 $c 2>&1 | grep -c '白名单\|Connection failed')
  if [ "$wl" -gt 0 ]; then echo "CONN_FAIL: $c"; fi
done

# 4) 联合 readiness 判定（HTTP 探活 / 命令退出码 / Docker health / 日志兜底）
for c in $(docker ps --filter 'name=xdclaw-u-' --format '{{.Names}}'); do
  running=$(docker inspect "$c" --format '{{.State.Running}}' 2>/dev/null)
  health=$(docker inspect "$c" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null)

  if [ "$running" != "true" ]; then
    echo "NOT_READY: $c (not running)"
    continue
  fi

  if docker exec "$c" sh -lc 'python3 - <<'"'"'PY'"'"'
import sys, urllib.request
try:
    r = urllib.request.urlopen("http://127.0.0.1:18789/", timeout=3)
    sys.exit(0 if r.status == 200 else 2)
except Exception:
    sys.exit(1)
PY'; then
    continue
  fi

  if [ "$health" = "healthy" ]; then
    continue
  fi

  ready=$(docker logs --tail 120 "$c" 2>&1 | grep -E -c 'Gateway ready|\[gateway\] ready')
  if [ "$ready" -gt 0 ] && [ "$health" = "starting" ]; then
    continue
  fi

  if [ "$health" = "unhealthy" ]; then
    echo "NOT_READY: $c (health=unhealthy,http!=200)"
  elif [ "$health" = "starting" ]; then
    echo "NOT_READY: $c (health=starting,http!=200)"
  else
    echo "NOT_READY: $c (http!=200,no-healthcheck)"
  fi
done

# 5) New API 健康
curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://localhost:3000/

# 6) 宿主机 Gateway 健康（用 HTTP 检测，不要用 pgrep/pidof）
curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://localhost:18789/
# 200 = 正常，非200 = 异常
```
- 修复策略：
  - `Cannot find module` → `docker exec $c sh -c 'cd /root/.openclaw/extensions/openclaw-qqbot && npm install --production'` 然后 `docker restart $c`
  - `白名单` → 通知老板去 QQ 开放平台加 IP
  - `NOT_READY` 且无 qqbot 错误 → `docker restart $c`
  - New API 非 200 → `docker restart new-api`

⚠️ **禁止**：不要用 pgrep/pidof/ps 检测宿主机 Gateway 进程。Docker 容器内也有同名进程，会导致误判。**只用 HTTP 状态码判断**。
⚠️ **禁止**：不要在巡查中添加 HEARTBEAT.md 未定义的检查项。所有检查项以本文件为准。

**巡查**（状态变更驱动，去重）：
1. 磁盘（> 80% 才报）
2. 内存使用率
3. 对比 `thinking-state.json` 的 `lastPatrolStatus`
4. 状态不变 → 不写日志；状态变更 → 写日志 + 通知老板
5. 同一问题最多通知 2 次

**NOW.md 刷新**：覆写当前状态。

## Phase 2: 思考（短离+，每 90min）

前置：距 lastThinkingRun < 90min → 跳过。
读今日日志最后 50 行 → 提炼 1-3 个问题入队 `thinking-queue.json` → 取一个快速思考写入 `memory/thoughts/YYYY-MM-DD.md`。

## Phase 3: 探索（深度空闲，每 4h）

前置：距 lastExploreRun < 4h → 跳过。
从 thinking-queue 或老板近期关注选题 → web_search 研究（限时 10min，只看前 3 条）→ 写摘要到 thoughts/。

## Phase 4: 记忆维护（Memory Maintenance）

前置：每次心跳都检查，但完整维护每 6h 一次。

### 4.1 WAL Flush（每次心跳必检）
检查 `wal-buffer.md` 中 `status:pending` 条目 → 逐条 flush 到目标文件 → 标记 `flushed` → 清除已 flush 条目。

### 4.2 日志压缩（条件触发）
若昨日日志存在 且 昨日 reflections 不存在 → 读昨日日志 → 提炼结论写入 reflections/ → 经验追加到 lessons/ → 决策写入 decisions/。

### 4.3 冷归档（每周一次）
>30天日志 → 移到 `.archive/`；>30天 reflections → 检查是否已沉淀到 lessons，是则归档。

### 4.4 索引校验（每周一次）
扫描 `memory/` 实际文件 vs `INDEX.md` → 新增补入，不存在删除。

### 4.5 active.md 结项检查
已完成 → 移到"待沉淀"；沉淀超 7 天 → 从 active.md 删除。

## 全局

- heartbeat 完成后 todayRequestCount +1
- 状态全持久化在文件里，不依赖内存
