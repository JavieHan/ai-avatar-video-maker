# AI Avatar Video Maker

用角色图片和台词，在 Muse 逐段生成视频，再在本地完成剪接、配音、字幕和包装。

[English](README.en.md) · [安装与命令](docs/usage.md) · [Agent Skill](skills/ai-avatar-video-maker/SKILL.md)

## 先看两条成片

点击封面观看或下载完整视频。

| 白衬衫口播 · 30 秒 | 小雅优雅版 · 27 秒 |
|:---:|:---:|
| [<img src="docs/demos/talking-head.jpg" width="250" alt="白衬衫口播，点击观看30秒完整样稿">](https://github.com/JavieHan/ai-avatar-video-maker/releases/download/samples-v1/talking-head-stickers.mp4) | [<img src="docs/demos/xiaoya.jpg" width="250" alt="小雅口播与舞蹈，点击观看27秒完整样稿">](https://github.com/JavieHan/ai-avatar-video-maker/releases/download/samples-v1/xiaoya-elegant.mp4) |
| 6 号配音 · 字幕 · 暖黄贴纸 | 10 号配音 · 口播与舞蹈 · 古琴古筝 |

## 1. 准备人物和稿子

固定人物、衣服和场景，把台词拆成能自然说完的短句。小雅这类有动作的内容，先安排好口播、起身和转身的顺序。

![两条样稿的人物与内容安排：白衬衫按短句口播，小雅把口播与动作分开规划](docs/guide/01-plan.jpg)

## 2. 逐段生成，用真实尾帧接力

先生成并审看第一段，再选保留剪点。**先剪视频，再从保留片提取最后一帧**；把这张图实际附到 Muse，要求下一段承接相同人物、姿态、机位和光线。

![尾帧接力图解：10秒原片保留173帧，提取F172，并把同一张PNG作为下一段图片附件](docs/guide/02-handoff.jpg)

图中是白衬衫早期测试的真实记录，不是两条成片的历史剪点。图片只能引导生成，不能保证首帧完全相同。

## 3. 检查接点，再拼接

并排比对上一段末帧和下一段首帧，再播放接点前后各约 1 秒。接得上时直接切接；有重复动作就剪掉，不额外停留或回播尾帧。

![真实尾帧与生成首帧对照：检查脸与头肩、衣领、背景和光线，连续音轨跨过剪接点](docs/guide/03-join.jpg)

**上一段必须保留到取尾帧时的同一剪点。** 改了剪点，就重新取尾帧并复核后续。接点顺畅后还要看完整下一段，检查人物和动作是否漂移；配乐或环境底音沿整条时间线连续编排。

## 4. 选声音，对齐发声与字幕

两条样稿使用外部 TTS2 配音，选自本次试听的 6 号和 10 号。先试听，再按正确台词生成短句，依据画面实际开口和停顿放置音频；`whisper-cli` 辅助制作字幕时间轴。

![白衬衫最终人声的真实波形与字幕示意：第一句约0.85秒开始，第二短句约2.52秒开始](docs/guide/04-voice.jpg)

后期换声不会改变嘴型。字幕使用确认稿，并按最终声音复核时间。

## 5. 加包装，导出并看完整片

白衬衫样稿加了字幕和暖黄贴纸；小雅保留动作空间，用古琴、古筝配合口播与舞蹈。按内容添加元素，最后检查字幕、音乐、接点和闪帧。

![白衬衫同时间画面的包装前后对比，以及小雅口播和展袖动作的成片截图](docs/guide/05-finish.jpg)

输出 **MP4 + 可编辑 Remotion 工程**。样稿包含人工剪辑与后期处理，基础模板不会一键复刻全部效果；[制作说明与配乐署名](docs/demos/README.md)。

## 开始使用

需要 Python 3、FFmpeg/FFprobe、`whisper-cli` 与本地模型、Node.js 18+ 和 npm。TTS 是可选外部工具，本项目不打包 TTS2。

[安装与完整命令 →](docs/usage.md)

Muse 生成在你自己的界面完成；本项目准备离线请求，不提供 Muse API/MCP，也不自动提交或代付。时长、可用参数和费用以当前 Muse 界面为准。

## 来源与许可

基于 [andyhuo520/digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo)，复用了字幕时间轴、部分本地脚本和 Remotion 包装组件，新增或改造了 Muse 尾帧接力与换声流程。详见 [来源与改造](ATTRIBUTION.md)。保留上游 [MIT LICENSE](LICENSE)、[NOTICE](NOTICE.md) 和 [第三方说明](THIRD_PARTY.md)；人物、声音、配乐和第三方服务的使用权另行适用。
