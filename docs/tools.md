# 工具是什么、去哪里安装

[返回首页](../README.md) · [Codex / Claude 配置](agent-setup.md) · [制作命令](usage.md)

## Muse：生成视频片段

这里的 Muse 指 **Meta 的 Muse AI 助手**，不是本仓库开发的视频模型。样稿通过 Muse 的应用/网页生成短片，再下载到本地继续处理。

- [Meta 官方产品页](https://ai.meta.com/muse/)
- [官方应用下载](https://ai.meta.com/muse/download/)

登录自己的账号后，先确认能用图片生成视频，以及当前单段时长、可用参数、额度和费用。仓库提供提示词、尾帧和剪辑辅助；生成请求在 Muse 界面提交。样稿记录没有披露实际后台视频模型，因此本项目不绑定某个未确认的型号。

## TTS2：Breeze TTS 2 配音

文档里的“TTS2”是 **Breeze TTS 2** 的简称。它把正确的台词变成语音，支持声音设计与声音克隆。样稿制作时，在 Apple Silicon Mac 上使用了社区 MLX BF16 移植版。

| 环境 | 入口 | 说明 |
|---|---|---|
| Linux + NVIDIA CUDA | [官方推理代码](https://github.com/breezeblue-ai/breeze-tts) · [原模型](https://huggingface.co/BreezeBlue/Breeze-TTS-2) | 按官方项目的硬件、Python 和安装要求准备。 |
| Apple Silicon Mac | [MLX-Audio](https://github.com/Blaizzy/mlx-audio) · [社区 BF16 权重](https://huggingface.co/mlx-community/Breeze-TTS-2-mlx) | 社区移植，并非 BreezeBlue 官方运行时；按对应版本说明安装。 |

**许可影响用途：** 官方将模型权重、衍生模型和自部署输出限定为研究与非商业用途；商业授权应按[模型许可证](https://huggingface.co/BreezeBlue/Breeze-TTS-2/blob/main/LICENSE)另行处理。推理源码的 Apache-2.0 与本仓库的 MIT 不替代模型许可。官方托管服务与自部署模型的授权范围不同，见[官方模型说明](https://huggingface.co/BreezeBlue/Breeze-TTS-2#license-and-responsible-use)。

本仓库接收生成后的 WAV 文件，不捆绑语音模型。若你选用其他获授权的 TTS 或自己的录音，仍可按[配音计划](../examples/voice-plan.json)执行本地短句对齐。

## 本地后期依赖

| 工具 | 负责什么 | 安装入口 |
|---|---|---|
| Python 3 | 请求、文件与时间轴处理 | [Python](https://www.python.org/downloads/) |
| FFmpeg / FFprobe | 取帧、裁切、拼接、音频变速与混音 | [FFmpeg](https://ffmpeg.org/download.html) |
| whisper.cpp 的 `whisper-cli` + 模型 | 识别语音，辅助定位短句和字幕 | [whisper.cpp](https://github.com/ggml-org/whisper.cpp) |
| Node.js 18+ 与 npm | Remotion 工程预览和渲染 | [Node.js](https://nodejs.org/en/download) |

安装后设置本地 Whisper 模型路径，并运行：

```bash
export WHISPER_MODEL="<你的本地模型完整路径>"
sh skills/ai-avatar-video-maker/scripts/doctor.sh
```

检查脚本会报告命令是否存在、Node 版本及模型路径是否就绪，不验证外部账号和生成能力。实际渲染时还会在新建的 Remotion 工程安装 npm 依赖。

主流程可在 macOS / Linux 使用。可选的 `cutout_video.py` 和 `personmask.swift` 使用 **macOS Vision 与 Swift**，仅适用于 macOS；基础剪接、配音替换和字幕包装不依赖它们。
