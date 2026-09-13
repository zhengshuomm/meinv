---
name: video-edit
description: 工业级全能视频编辑与后期处理技能。基于本地高性能 FFmpeg 与 Whisper 引擎，支持通过自然语言对视频进行精细化处理：精准裁剪(trim)、智能静音剔除跳剪(jumpcut)、爆款动态字幕压制(caption，支持 hormozi 单词加粗/standard 经典底框/minimal 极简三种模式与中文字体支持)、文字与水印贴片(overlay)、音调修正变速(speed)、多镜头平滑转场拼接(concat 与 xfade)，以及多工序串联自动化流水线(edit.sh)。
---

# 视频智能编辑技能 (video-edit)

本技能为 AI Agent 提供全面的视频后期处理能力，使用纯原生 Bash + 高性能 FFmpeg（ARM64 NEON 加速）及 Whisper 引擎驱动，支持通过自然语言指令完成视频粗剪、精剪、去无声片段、压制字幕、添加贴片与转场拼接。

---

## 🎯 核心功能一览

| 模块名称 | 对应脚本 | 核心功能说明 | 典型场景 |
| :--- | :--- | :--- | :--- |
| **全流程编排** | `scripts/edit.sh` | 串联裁剪、去静音、变速、字幕、贴片于一体 | “帮我把视频剪到前30秒，去静音，加速1.2倍并加上字幕” |
| **精确裁剪** | `scripts/trim.sh` | 按起始/结束时间戳或时长裁剪，毫秒级快速寻道 | “截取视频 00:01:10 到 00:02:30 的高潮镜头” |
| **静音跳剪** | `scripts/jumpcut.sh` | 自动检测音画无声/气口停顿并无缝剔除 | “口播视频气口太长，把所有静音停顿都剪掉” |
| **字幕压制** | `scripts/caption.sh` | 烧录 SRT 字幕，支持中文字体与三种爆款版式 | “给视频加上 Alex Hormozi 风格的黄字加粗居中字幕” |
| **文字贴片** | `scripts/overlay-text.sh` | 在任意时段和画面九宫格位置添加标题/水印 | “在第 5 秒到 10 秒顶部居中打上'必吃榜第一名'” |
| **片段拼接** | `scripts/concat.sh` | 多视频拼接，支持无缝直连或 xfade 平滑淡入淡出 | “把 shot1 和 shot2 拼起来，中间加 0.4 秒淡入淡出” |
| **语音转写** | `scripts/transcribe.sh` | 提取音轨并转写为标准 SRT 字幕文件 | “把视频里的口播提取成带有精确时间轴的字幕” |

---

## 🚀 快速上手与使用示例

### 1. 全自动流水线 (主推荐)
使用 `edit.sh` 可以在一条命令中按科学顺序自动执行：**裁剪 ➔ 去无声 ➔ 变速 ➔ 烧录字幕 ➔ 添加贴片**。

```bash
# 典型短视频流水线：裁剪前15秒 + 去无声 + 1.25倍速 + 烧录字幕 + 水印
scripts/edit.sh input.mp4 \
  --trim-start 00:00:00 --trim-duration 15 \
  --jumpcut \
  --speed 1.25 \
  --caption --caption-srt subtitles.srt --caption-style hormozi \
  --overlay-text "淄博烧烤探店" --overlay-position top \
  --output output/final_edited.mp4
```

---

### 2. 精确视频裁剪 (Trim)
支持指定开始时间 `--start`、结束时间 `--end` 或持续时间 `--duration`（支持 `HH:MM:SS` 或秒数）。

```bash
# 截取从 10 秒开始的 30 秒片段
scripts/trim.sh input.mp4 --start 00:00:10 --duration 30 --output clip.mp4

# 截取特定时间段
scripts/trim.sh input.mp4 --start 00:01:30 --end 00:03:00 --output highlight.mp4
```

---

### 3. 智能去除静音与停顿 (Jump Cut)
基于 FFmpeg 的 `silencedetect` 滤波器，自动识别说话停顿并平滑切除，显著提升完播率。

```bash
# 默认配置（阈值 -30dB，静音持续大于 0.5s，保留 0.1s 气口边距）
scripts/jumpcut.sh input.mp4 --output tight_speech.mp4

# 激进剪辑（适合短视频快节奏，切除 >0.3s 的停顿）
scripts/jumpcut.sh input.mp4 --threshold -25 --duration 0.3 --padding 0.08
```

---

### 4. 爆款字幕压制 (Captions)
支持三种精心调校的短视频爆款样式，内置苹方（PingFang SC）中文字体渲染，绝无方块乱码。

| 样式名称 | 参数 `--style` | 视觉效果 | 适用视频类型 |
| :--- | :--- | :--- | :--- |
| **hormozi** | `hormozi` | **亮黄色加粗居中**，3px 黑色高对比度描边，大字冲击力 | 探店、干货、短视频第一视点 Hook |
| **standard** | `standard` | 经典底部白色字幕，带半透明黑色气泡背景框，优雅护眼 | 故事讲述、纪录片、常规美食解说 |
| **minimal** | `minimal` | 左下角小字，纯净微阴影，极简无边框设计 | 美学生活 Vlog、电影感空镜抒情 |

```bash
# 压制 Hormozi 风格亮黄爆款字幕
scripts/caption.sh input.mp4 input.srt --style hormozi --output final_hormozi.mp4

# 压制经典标准底部字幕
scripts/caption.sh input.mp4 input.srt --style standard --output final_standard.mp4
```

---

### 5. 画面文字与水印贴片 (Overlay Text)
支持设置位置（`center`, `top`, `bottom`, `top-left`, `top-right`, `bottom-left`, `bottom-right`）、显示时间区间、字号与颜色。

```bash
# 在前 5 秒画面顶部显示醒目标题
scripts/overlay-text.sh input.mp4 \
  --text "🔥 淄博烧烤灵魂吃法" \
  --position top \
  --fontsize 44 \
  --fontcolor yellow \
  --start 00:00:00 --end 00:00:05 \
  --output with_title.mp4
```

---

### 6. 多镜头拼接与平滑转场 (Concat / Xfade)
将多个视频片段拼接为一个长视频，支持直连模式（秒级完成）或专业级转场（淡入淡出、擦除、溶解）。

```bash
# 无缝淡入淡出转场拼接（转场时长 0.4 秒）
scripts/concat.sh shot1.mp4 shot2.mp4 shot3.mp4 \
  --xfade 0.4 \
  --transition fade \
  --output full_story.mp4

# 极速直连模式（无转场损耗）
scripts/concat.sh shot1.mp4 shot2.mp4 --output merged.mp4
```

---

### 7. 语音转写 (Transcribe)
将视频中的口播音轨提取并转写为标准 `.srt` 字幕：
- 本地优先使用 `faster-whisper`（8-bit 量化，极速运行）；
- 支持云端 OpenAI Whisper API（当配置 `OPENAI_API_KEY` 时自动加速）；
- 支持直接传入预先准备好的 SRT 文件（推荐在视频生成工作流中直接由脚本生成并压制）。

```bash
scripts/transcribe.sh input.mp4 --language zh --output output.srt
```

---

## 🛠️ 底层环境与依赖路径

本技能已为本工作区完成深度适配，开箱即用：
- **FFmpeg / FFprobe**：已集成至 `bin/ffmpeg` 与 `bin/ffprobe`（支持 Apple Silicon ARM64 NEON 加速与 libass 字幕库）；
- **Whisper 运行器**：集成于 `bin/whisper`，由本地专用环境支持；
- **免权限运行**：所有执行脚本自动检索工作区 `bin/` 目录，沙箱内执行无需额外授权。

---

## 📋 Agent 响应工作准则

当用户要求编辑、剪辑、加字幕或合成视频时：
1. **意图拆解**：分析用户需要的一项或多项操作（裁剪、跳剪、字幕、贴片、转场等）；
2. **多任务首选 `edit.sh`**：如果是链式复合操作，调用 `scripts/edit.sh` 一键执行；
3. **单任务直调专项脚本**：若仅需裁剪调用 `scripts/trim.sh`，仅需字幕调用 `scripts/caption.sh`，以获得最快执行速度；
4. **汇报规范**：完成后向用户汇报生成的目标文件绝对路径、视频时长、分辨率及文件大小。
