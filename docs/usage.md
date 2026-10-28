# 安装与命令参考

[返回首页图解](../README.md) · [Agent Skill](../skills/ai-avatar-video-maker/SKILL.md)

## 安装和准备

在 macOS / Linux 的终端中运行；其他系统需要可用的 Python、FFmpeg、whisper.cpp 和 Node 环境。使用自己的 Muse 账号及有权使用的角色、声音和音乐。制作所需的原始人物图片、配音和片段由使用者准备；首页样稿另行授权展示，完整成片单独放在 Releases。

- Python 3、FFmpeg/FFprobe：准备请求、剪接、导入和换声。
- [whisper.cpp](https://github.com/ggml-org/whisper.cpp) 的 `whisper-cli` 和一个本地模型：台词检查与时间轴；模型路径通过 `WHISPER_MODEL` 或 `--model` 指定。
- Node.js 18+、npm：创建 Remotion 工程后安装其依赖并渲染；Remotion 使用条件见 [THIRD_PARTY.md](../THIRD_PARTY.md)。
- 本机或其他渠道的 TTS 是**可选外部工具**。本项目不打包 TTS2，也不要求使用特定音色。

```bash
git clone https://github.com/JavieHan/ai-avatar-video-maker.git
cd ai-avatar-video-maker
AVATAR_SKILL="$PWD/skills/ai-avatar-video-maker"
mkdir -p work/demo/downloads work/demo/kept
cp examples/persona.json examples/script.json work/demo/
cd work/demo
```

把有权使用的人物图片放在本目录，命名为 `portrait.png`，或修改 `persona.json` 的 `reference_image`。编辑 `script.json` 为真实台词，编辑人物、画幅及 `voice.description`。示例内容只是格式，不是用户资料。项目输出默认放在 Git 忽略的 `work/` 下。

## 1. 准备请求并生成第一段

```bash
python3 "$AVATAR_SKILL/scripts/build_tasks.py" script.json tasks-s1.json --persona persona.json
```

打开 `tasks-s1.json`，把 `s1` 的 `prompt` 和 `reference_image` **实际作为图片附件**交给 Muse；文件路径文字本身不会上传图片。下载视频到 `downloads/s1.mp4`。每次提交前核对 Muse 的实际时长、额度和请求次数；首段审看通过后再继续。

## 2. 逐段剪辑和尾帧接力

先看第一段结尾，选择一句说完、表情和机位适合衔接的位置；例如决定保留 6 秒（命令示例，不是样稿历史剪点）：

```bash
python3 "$AVATAR_SKILL/scripts/handoff.py" \
  --video downloads/s1.mp4 --keep-seconds 6 \
  --trimmed kept/s1.mp4 --tail kept/s1-tail.png \
  --tasks tasks-s1.json --next-id s2 --output-tasks tasks-s2.json
```

该命令仅在本机处理，所有输出必须是新文件。它导出 30 fps 保留片段、从该片段实际提取最后一帧，并在新清单中将 `s2` 绑定到这张图，同时打印保留帧数（例中为 180 帧）。请**实际附上 `kept/s1-tail.png`**，把 `tasks-s2.json` 中 `s2` 的提示词发送给 Muse；下载并审看第二段。

更多段时，用上一轮的新任务清单、实际上一段视频和新的输出文件名继续接力。不要把源视频路径或截图文字当作已上传。重做某段后，必须重新检查它的尾帧及后续片段。首帧只是参考，视频生成结果可能改变表情、构图或人物。

## 3. 导入、审核与拼接

以两段为例，先手工创建 `results.json`，其中 `s1` 使用上一步的保留片，`s2` 使用实际下载片段；路径相对 `results.json`：

```json
{
  "s1": {"src": "kept/s1.mp4"},
  "s2": {"src": "downloads/s2.mp4"}
}
```

```bash
python3 "$AVATAR_SKILL/scripts/import_muse.py" tasks-s2.json results.json clips.json
```

导入只验证文件及音轨、记录哈希；它**不会**替你判断台词、人物或口型。逐段看听后，在 `clips.json` 中将符合要求的 `review_status` 改成 `approved`；有问题则保持 `pending` 或设为 `rejected`。改变已绑定图片的内容会使旧请求失效。

```bash
export WHISPER_MODEL="<本机 Whisper 模型的完整路径>"
python3 "$AVATAR_SKILL/scripts/assemble.py" script.json clips.json \
  --tasks tasks-s2.json --out main.mp4 --cut-dir cut \
  --keep-frames s1=180
python3 "$AVATAR_SKILL/scripts/align.py" script.json --cut-dir cut --out tl.json
```

将 `s1=180` 改成接力工具实际打印的帧数；多段时为每个已用作参考的保留段分别加 `--keep-frames 段号=帧数`。此步骤可能重新编码，因此仍需比较成片接点。未指定帧数的段按 Whisper 估计的语音结束点裁尾，**不适用于已用于续接但未登记剪点的段**。

识别与原稿相似度低时会暂停。实际听审后，如果仅是识别误差，使用 `--accept-asr-mismatch s2 --review-note "实际复核依据"`；如果原声确实有错且准备后期换声，用 `--accept-spoken-error s2 --review-note "实际复核依据"`。两者都不会标记口型通过。重跑请换用全新 `--out` 和 `--cut-dir`，不会覆盖已有成片或缓存。

## 4. 可选：替换配音

可以用 TTS2、其他 TTS 或自己录制的声音，**先把配音分成短句并人工确定各句的发声时间**。在当前工作目录复制[配音计划示例](../examples/voice-plan.json)：

```bash
cp "$AVATAR_SKILL/../../examples/voice-plan.json" voice-plan.json
```

将每项的 `audio` 改成该文件旁的音频，`at` 改为视频中实际发声秒数；`rate` 是可选语速倍率（0.5–2）。示例时间仅为格式演示。编辑好后运行：

```bash
python3 "$AVATAR_SKILL/scripts/timed_voice.py" main.mp4 voice-plan.json --out main-redub.mp4
```

这一步保留视频画面、替换原音，不会自动识别或保证准确的口型同步，也不会自动保留原视频的背景声。时间重叠、超出片长或输出已存在时会停止。请听审，并根据实际新配音复核 `tl.json` 的时间；原音生成的字幕时间不一定适用于新声音。

## 5. 创建可编辑工程并渲染

```bash
python3 "$AVATAR_SKILL/scripts/prepare_edit.py" \
  --video main.mp4 --timeline tl.json --output community-edit
cd community-edit
npm install --no-audit --no-fund
bash scripts/render.sh ../finished.mp4
```

使用 `main-redub.mp4` 可制作换声版；也可以在准备工程时加 `--voice 已对齐音轨.wav`、`--music 已授权音乐.mp3` 或 `--stickers 贴纸.json`。贴纸数组格式见[贴纸示例](../examples/stickers.json)，秒数按实际视频填写。默认没有额外配音、音乐、贴纸、广告文案或白闪，画布取源视频尺寸并保持完整画面。`render.sh` 默认单线程，已有输出不会覆盖；渲染后仍需核查整条视频，而不是仅看静帧。若遇到渲染异常，可先用 `npx remotion studio` 检查。

