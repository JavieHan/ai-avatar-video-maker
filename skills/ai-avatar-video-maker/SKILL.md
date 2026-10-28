---
name: ai-avatar-video-maker
description: 使用用户现有的 Muse 与本地 FFmpeg、whisper-cli、Remotion 共同制作分段数字人口播；支持人工检查、剪后尾帧图片接力、可选本地配音替换和可编辑工程。
---
# 数字人口播 · Muse 社区版

先阅读仓库 README 的图解和 `docs/usage.md` 的命令，确定用户的稿子、授权角色图片、声音选择与希望输出的形式。工具身份与安装见 `docs/tools.md`；Muse 指 Meta 的 Muse，TTS2 指 Breeze TTS 2，后者自部署模型与输出有非商业用途限制。此版本基于上游 digital-human-koubo 代码改造，实际视频由用户或 Agent 在 Muse 界面提交生成；不猜测模型、价格、额度或音频驱动能力。

通过 `bash setup.sh codex|claude|both` 接入后，从包含 `setup.sh` 的仓库根目录使用此技能。先运行 `scripts/doctor.sh`（相对此技能目录）检查依赖；将技能已接入、依赖就绪和实际生成/渲染成功分别报告。配置与使用入口见仓库 `docs/agent-setup.md`。

## 工作原则

- `build_tasks.py` 只生成离线请求，不提交、不收费。根据用户给定的范围与实际 Muse 界面信息执行；先核对能力、单次时长和成本，不擅自重试或切换供应商。
- 用真实附件上传参考图。上一段先审看台词和表情，选实际保留的剪点，再用 `handoff.py` 导出保留片段、实际尾帧及绑定下一段的新任务清单。参考图不代表首帧硬锁。检查操作者选择的视频确为上一段。
- `import_muse.py` 只导入真实下载视频。审核状态必须来自实际审看，不把哈希、音轨存在或 Whisper 分数说成口型或台词通过；待审可用 `--allow-pending` 预览，不能当最终验收。
- `assemble.py` 使用 whisper-cli 质检并拼接，保留参考帧对应的 `--keep-frames`。识别误差和实际错词使用不同复核参数。输出与中间目录不会覆盖已有内容；检查重新编码后的接点。
- 本次样稿的 Muse 中文曾出现错词或含糊，采用下载后本地重配：Whisper 辅助定位，波形修正发声区间，TTS2 按用户确认稿生成声音，再切短句、保音高调时长、移动到原画面开口处。先读 `references/voice.md` 与 `docs/redubbing.md`。`timed_voice.py` 只执行已确认的计划，不生成声音、不自动找嘴唇，也不驱动嘴部。用户未选择时不要默认克隆音色或替换原声；换声后按最终声音复核字幕时间与口型。
- 使用 `align.py` 和 `prepare_edit.py` 准备 Remotion 工程，配音、贴纸和音乐均可选且需真实素材；单线程渲染后检查整片，不把抽帧或解码成功当成完整视听验收。
- 保护用户素材、正式版本和私有账户信息；输出另存。不要将用户图片、视频、声音或密钥提交到公开仓库。只使用获得授权的脸、声音和音乐；按需要进行 AI 数字人标识。

参考 `references/muse.md`、`references/voice.md` 与仓库 README。当前发行版聚焦口播基础模板；如需上游其他模板和原作者展示图，查看上游仓库及其独立素材使用说明。
