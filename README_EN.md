# seedance-skill

English | **[中文](README.md)**

ByteDance Seedance AI Video Creative Studio — a skill pack that turns any AI Agent into a video creative director.

> Not a prompt template. A creative system with taste.

## Highlights

- **Autonomous Creative Director** — No fixed pipeline. The Agent decides analysis order, iteration rounds, and output format on its own.
- **Creativity Gate** — Every prompt must pass four checks: memorability, surprise factor, emotional arc, and narrative progression. If it's boring, it gets rewritten.
- **Zero-Copy Creative Mode** — User drops an image with no text? The Agent brainstorms 2-3 creative directions and picks the most interesting one.
- **Comprehensive Vocabulary** — 100+ cinematography terms across 12 categories, 10 director style references, 9 anime animation techniques.
- **Seedance 2.0 Full Multimodal** — Text / image / video / audio input. Motion replication, beat-sync, multi-shot narrative.
- **One-Command API Generation** — Python CLI covering all Seedance models (2.0 / 1.5 Pro / 1.0 series).

## Project Structure

```
seedance-skill/
├── SKILL.md          # Skill document · Chinese (Agent entry point)
├── SKILL_EN.md       # Skill document · English
├── reference.md      # Vocabulary, techniques, official examples
├── scripts/
│   └── seedance.py   # Volcengine Ark API CLI tool
├── README.md         # 中文 README
└── README_EN.md      # This file (English)
```

## Quick Start

### 1. Install

Clone this repo into your Agent's skill directory:

```bash
git clone https://github.com/zhanghaonan777/Seedance2-skill.git
```

### 2. Set Up API Key

```bash
export ARK_API_KEY="your-volcengine-ark-api-key"
```

Get your API Key from the [Volcengine Console](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey).

### 3. Generate Videos

```bash
# Text-to-video
python3 scripts/seedance.py create --prompt "A man in black running through a crowded market" --ratio 16:9 --duration 5 --wait --download ~/Desktop

# Image-to-video
python3 scripts/seedance.py create --prompt "The character slowly turns around" --image photo.jpg --ratio adaptive --wait --download ~/Desktop

# Video reference / motion replication (Seedance 2.0)
python3 scripts/seedance.py create --prompt "Follow the camera movement from the reference" --video reference.mp4 --wait --download ~/Desktop

# Audio beat-sync (Seedance 2.0)
python3 scripts/seedance.py create --prompt "Visuals shift with every beat" --audio bgm.mp3 --wait --download ~/Desktop
```

Run `python3 scripts/seedance.py create --help` for all options.

## Agent Integration

This skill is compatible with any AI Agent platform that supports skill/tool loading. Use `SKILL_EN.md` for English-context Agents, or `SKILL.md` for Chinese-context Agents. Both produce Chinese prompts (Seedance works best with Chinese input).

### OpenClaw

Place this directory in OpenClaw's skills folder (e.g. `~/.openclaw/workspace/skills/seedance-skill/`). The Agent loads automatically when users mention "Seedance", "video generation", "AI video", etc.

### Cursor

Place this directory in `~/.cursor/skills/seedance-skill/` to use as an Agent Skill. Same trigger words apply.

### Other Platforms

Inject `SKILL_EN.md` (or `SKILL.md`) as a system prompt or tool description. Load `reference.md` as supplementary context on demand.

## Supported Models

| Model | Model ID | Capabilities |
|-------|----------|-------------|
| **Seedance 2.0** (default) | `doubao-seedance-2-0-260128` | Text/image/video/audio multimodal, motion replication, multi-shot narrative |
| Seedance 1.5 Pro | `doubao-seedance-1-5-pro-251215` | Text/image-to-video, native audio, draft preview, flex offline inference |
| Seedance 1.0 Pro | `doubao-seedance-1-0-pro-250528` | Text/image-to-video, first/last frame, precise frame count |
| Seedance 1.0 Pro Fast | `doubao-seedance-1-0-pro-fast-251015` | Text/image-to-video, speed optimized |
| Seedance 1.0 Lite I2V | `doubao-seedance-1-0-lite-i2v-250428` | Multi-reference images ([img1][img2] syntax) |

## CLI Reference

| Flag | Description |
|------|-------------|
| `--prompt` | Video description prompt |
| `--image` | First frame image (URL or local file) |
| `--last-frame` | Last frame image |
| `--ref-images` | Reference images (1-9) |
| `--video` | Reference videos (1-3, Seedance 2.0) |
| `--audio` | Reference audio (1-3, Seedance 2.0) |
| `--model` | Model ID (defaults to Seedance 2.0) |
| `--ratio` | Aspect ratio: 16:9 / 4:3 / 1:1 / 3:4 / 9:16 / 21:9 / adaptive |
| `--duration` | Duration in seconds, -1 for auto |
| `--resolution` | Resolution: 480p / 720p / 1080p |
| `--draft` | Draft mode (low-cost preview) |
| `--service-tier` | `default` or `flex` (offline, 50% cheaper) |
| `--generate-audio` | Generate synchronized audio |
| `--return-last-frame` | Return last frame URL (for video chaining) |
| `--callback-url` | Webhook URL for status notifications |
| `--wait` | Wait for task completion |
| `--download` | Download directory |

## The Creativity System

The core of this Skill isn't API calls — it's the **creativity gate**:

1. **Memorability** — What will the viewer remember after watching?
2. **Surprise** — Is there a twist, contrast, exaggeration, or unusual detail?
3. **Emotion** — Does it have an emotional arc (tension → release, calm → explosion)?
4. **Narrative** — Even in 5 seconds, there should be a change from A to B.

The Agent self-reviews every prompt and rewrites until it passes. No mediocre output allowed.

## Requirements

- Python 3.6+ (stdlib only, no third-party dependencies)
- [Volcengine Ark API Key](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)

## License

MIT
