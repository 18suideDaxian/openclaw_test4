---
name: multimodal-image
description: 必须用于图片生成和图片理解。触发词：画、帮我画、生成图片、生图、做张图、出图、图片、头像、海报、插画、改图、看图、截图、OCR、提取图片文字。遇到生图请求必须调用 generate 脚本并用 <qqmedia> 返回图片；不要只文字描述，也不要把主 session 切到 VLM 或图片模型。
metadata: {"openclaw":{"emoji":"🖼️"}}
---

# Multimodal Image Tool Layer

主 session 固定文本模型；图片理解/生图走旁路工具，避免 session swamp。

## 强制触发规则

用户只要表达以下意图，必须调用本 skill，不要只用文字回答：

- 画 / 帮我画 / 生成图片 / 生图 / 做张图 / 出图
- 头像 / 海报 / 插画 / 表情包 / logo / 封面 / 配图
- 改图 / 图生图 / 重绘 / 换风格 / 按这张图生成
- 看图 / 分析截图 / 提取图片文字 / OCR

---

## 🚀 生图流程（异步子代理模式）

**生图/图生图请求使用子代理异步执行，主 session 不阻塞。**

### 步骤 1：生成任务 ID
格式：`img-{YYYYMMDD}-{HHMMSS}-{随机3位hex}`
例如：`img-20260429-110500-a3f`

### 步骤 2：立即回复用户
```
收到，开始生成图片，预计2-3分钟。任务ID：{jobId}
```

### 步骤 3：启动子代理
使用 `sessions_spawn` 启动后台任务：

```
sessions_spawn(
  mode: "run",
  task: "生图任务 {jobId}。执行命令：python3 /root/clawd/skills/multimodal-image/scripts/mm_image.py generate --prompt \"{用户的完整生图需求}\" 。成功后输出路径在 /root/.openclaw/media/qqbot/outputs/。请回复：图片好了（{jobId}）<qqmedia>输出的文件路径</qqmedia>。如果失败，回复：图片任务失败（{jobId}）：具体错误原因。注意：不要传 --out 参数，使用脚本默认路径。",
  runTimeoutSeconds: 300
)
```

### 步骤 4：结束当前 turn
不要等待子代理完成，立即结束当前回复。用户可以继续聊天。

### 完整示例

用户说"画一只橘猫在阳台晒太阳"：

1. 生成 jobId = `img-20260429-110500-a3f`
2. 回复：`收到，开始生成图片，预计2-3分钟。任务ID：img-20260429-110500-a3f`
3. 调用：
```
sessions_spawn(
  mode: "run",
  task: "生图任务 img-20260429-110500-a3f。执行命令：python3 /root/clawd/skills/multimodal-image/scripts/mm_image.py generate --prompt \"一只橘猫在阳台晒太阳\" 。成功后回复：图片好了（img-20260429-110500-a3f）<qqmedia>文件路径</qqmedia>。失败则回复：图片任务失败（img-20260429-110500-a3f）：错误原因。",
  runTimeoutSeconds: 300
)
```
4. 当前 turn 结束。

---

## 图片理解 / 截图分析 / 图片文字提取（同步）

图片理解不需要异步，直接在当前 session 执行：

```bash
python3 /root/clawd/skills/multimodal-image/scripts/mm_image.py understand --image /absolute/path/or/url.png --prompt "用户的问题"
```

可多图：重复 `--image`。

适用：看图、截图排障、图片文字/表格理解、图片问答、图片对比。

---

## 图生图 / 改图（异步子代理模式）

和生图流程一样，使用子代理异步执行：

1. 生成 jobId
2. 回复：`收到，开始图生图/改图，预计2-3分钟。参考图{N}张。任务ID：{jobId}`
3. 调用 sessions_spawn，task 中使用 edit 子命令：
```
python3 /root/clawd/skills/multimodal-image/scripts/mm_image.py edit --image /absolute/source.png --prompt "改图需求"
```
4. 结束当前 turn。

---

## 失败防循环

同一个请求最多尝试 2 次：
- 第一次失败，可以修正明显参数问题后重试一次。
- 第二次仍失败，必须停止并把错误原因告诉用户。
- 不要第三次调用同一个子命令，不要只改 prompt 反复试。
- 失败时不要伪造图片路径或假装已生成。

## 规则

- 不要使用 `/model` 把当前会话切到 `qwen-vl-*`、`gpt-image-*`、`*-image`。
- 不要用 exec/curl 自己调 `/images/edits`，走本 skill 的 `edit` 子命令。
- 如果 `gpt-image-2` 失败，脚本会自动返回错误；不要假装已生成。
- 502/上游错误时，子代理内最多重试一次，仍失败则返回具体错误信息。

## ⚠️ 输出路径规则（重要）

**绝对不要手动指定 `--out /tmp/xdclaw-images` 或其他自定义路径。**
脚本默认输出到 `/root/.openclaw/media/qqbot/outputs/`，这是 OpenClaw QQ Bot 模块允许的媒体目录。
手动指定其他路径会导致图片无法发送（被安全校验拦截）。

## 🧪 图生图事实声明

`gpt-image-2` 的 `/images/edits` 端点**实测可用**。
如果调用返回 502 / upstream error，是上游偶发错误，不是 gpt-image-2 不支持 edits。
