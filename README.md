# seedance-skill

**[English](README_EN.md)** | 中文

ByteDance Seedance AI 视频创意工作台 — 让 AI Agent 变身视频创意总监的技能包。

> 不是提示词模板，是一套有审美门槛的创意系统。

## 特色

- **自主创意总监** — 没有固定流程，Agent 自行决定分析顺序、迭代轮数、输出方式
- **创意审核机制** — 每条 prompt 必须过四关：记忆点、意外感、情绪弧线、叙事变化；不够好就推翻重来
- **零文案创意发散** — 只给一张图不说话？Agent 发散 2-3 个创意方向，挑最有意思的展开
- **完整词库** — 镜头语言 12 类 100+ 词条、导演风格速查 10 位、动漫作画术语 9 项
- **Seedance 2.0 全模态** — 文本 / 图片 / 视频 / 音频输入，运动复刻、音乐卡点、多镜头叙事
- **一键 API 生成** — Python CLI 覆盖全部 Seedance 模型（2.0 / 1.5 Pro / 1.0 系列）

## 项目结构

```
seedance-skill/
├── SKILL.md          # 技能主文档 · 中文（Agent 读取入口）
├── SKILL_EN.md       # 技能主文档 · English
├── reference.md      # 词库、技巧、官方示例
├── scripts/
│   └── seedance.py   # Volcengine Ark API CLI 工具
├── README.md         # 本文件（中文）
└── README_EN.md      # English README
```

## 快速开始

### 1. 安装

将本仓库克隆到你的 Agent 技能目录：

```bash
git clone https://github.com/yourname/seedance-skill.git
```

### 2. 设置 API Key

```bash
export ARK_API_KEY="your-volcengine-ark-api-key"
```

在 [火山引擎控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey) 获取 API Key。

### 3. 生成视频

```bash
# 文本生成视频
python3 scripts/seedance.py create --prompt "镜头跟随黑衣男子快速逃亡，后面一群人在追" --ratio 16:9 --duration 5 --wait --download ~/Desktop

# 图片生成视频
python3 scripts/seedance.py create --prompt "画面中的人物缓缓转身" --image photo.jpg --ratio adaptive --wait --download ~/Desktop

# 视频参考 + 运动复刻（Seedance 2.0）
python3 scripts/seedance.py create --prompt "参考视频的运镜和节奏" --video reference.mp4 --wait --download ~/Desktop

# 音频卡点（Seedance 2.0）
python3 scripts/seedance.py create --prompt "画面随音乐节拍切换" --audio bgm.mp3 --wait --download ~/Desktop
```

更多用法见 `python3 scripts/seedance.py create --help`。

## 接入 AI Agent

本技能兼容任何支持 Skill / Tool 加载的 AI Agent 平台。中文环境使用 `SKILL.md`，英文环境使用 `SKILL_EN.md`。Agent 读取后即获得完整的创意工作流和 API 调用能力。

### OpenClaw

将本目录放入 OpenClaw 的 skills 目录（如 `~/.openclaw/workspace/skills/seedance-skill/`），Agent 会在用户提到「即梦」「Seedance」「视频生成」等关键词时自动加载。

### Cursor

将本目录放入 `~/.cursor/skills/seedance-skill/`，作为 Agent Skill 使用。触发词同上。

### 其他平台

将 `SKILL.md`（或 `SKILL_EN.md`）作为 system prompt 或工具描述注入即可，`reference.md` 作为补充参考材料按需加载。

## 支持的模型

| 模型 | Model ID | 能力 |
|------|----------|------|
| **Seedance 2.0**（默认） | `doubao-seedance-2-0-260128` | 文/图/视频/音频多模态、运动复刻、多镜头叙事 |
| Seedance 1.5 Pro | `doubao-seedance-1-5-pro-251215` | 文/图生视频、音画同生、Draft 样片、Flex 离线推理 |
| Seedance 1.0 Pro | `doubao-seedance-1-0-pro-250528` | 文/图生视频、首尾帧、精确帧数控制 |
| Seedance 1.0 Pro Fast | `doubao-seedance-1-0-pro-fast-251015` | 文/图生视频、速度优先 |
| Seedance 1.0 Lite I2V | `doubao-seedance-1-0-lite-i2v-250428` | 多参考图（[图1][图2]语法） |

## CLI 完整参数

| 参数 | 说明 |
|------|------|
| `--prompt` | 视频描述提示词 |
| `--image` | 首帧图片（URL 或本地文件） |
| `--last-frame` | 尾帧图片 |
| `--ref-images` | 参考图（1-9 张） |
| `--video` | 参考视频（1-3 个，Seedance 2.0） |
| `--audio` | 参考音频（1-3 个，Seedance 2.0） |
| `--model` | 模型 ID（默认 Seedance 2.0） |
| `--ratio` | 宽高比：16:9 / 4:3 / 1:1 / 3:4 / 9:16 / 21:9 / adaptive |
| `--duration` | 时长（秒），-1 为自动 |
| `--resolution` | 分辨率：480p / 720p / 1080p |
| `--draft` | 样片模式（低成本预览） |
| `--service-tier` | `default` 或 `flex`（离线半价） |
| `--generate-audio` | 是否生成音频 |
| `--return-last-frame` | 返回尾帧（用于视频接龙） |
| `--callback-url` | Webhook 回调地址 |
| `--wait` | 等待任务完成 |
| `--download` | 下载目录 |

## 创意系统

这个 Skill 的核心不是 API 调用，而是**创意审核机制**：

1. **记忆点** — 观众看完能记住什么？
2. **意外感** — 是否有反转、对比、夸张？
3. **情绪** — 有没有情绪弧线？
4. **叙事** — 哪怕 5 秒也要有变化

Agent 会反复自检 prompt 质量，不够好就推翻重来，直到"有意思"为止。

## 依赖

- Python 3.6+（仅标准库，无第三方依赖）
- [火山引擎 Ark API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)

## 许可

MIT
