# 依赖

仓库 `docs/tools.md` 提供工具身份和安装入口，`docs/agent-setup.md` 提供 Codex / Claude Code 的项目范围配置，`docs/usage.md` 提供制作命令。用本技能的 `scripts/doctor.sh` 检查依赖。

离线任务用 Python 3；视频读取和剪辑需要 FFmpeg/FFprobe；语音转写需要 whisper.cpp 的 whisper-cli 和本地模型；Remotion 预览/渲染需要 Node 18+、npm 和工程依赖。`cutout_video.py` / `personmask.swift` 依赖 macOS Vision 与 Swift，仅 macOS 可用；基础流程支持 macOS / Linux。

不包含 Muse 账号、Muse SDK、TTS2、用户声音或任何模型权重。使用自己的 Muse 界面和合法素材；不要将个人媒体、账户或 API 凭据加入公开代码仓库。
