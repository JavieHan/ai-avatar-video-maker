# AI Avatar Video Maker

用 Muse 生成连续人物画面，再下载到本地，用 Whisper + TTS2 修正中文配音，按现有口型节奏剪辑，完成字幕与包装。

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

## 4. 下载到本地，重配中文并对齐口型节奏

**本次 Muse 中文口播出现过错词、含糊和语速不自然，所以两条样稿都没有直接采用原生中文配音作为最终人声。** 画面通过后下载到本地，这一步按以下顺序完成：

1. 提取原声，用 `whisper-cli` 找到短语的大致位置，再按波形修正发声起止，结合画面核对。
2. 用 TTS2 读**用户确认的正确稿**；Whisper 识别出的错字不能当作新台词。白衬衫选了试听 6 号，小雅选了 10 号。
3. 将新配音裁成短句，去多余静音，保音高调整时长，再移动到画面实际开口处，保留原有停顿。
4. 替换 Muse 原声音轨，按最终声音复核字幕时间；背景音乐随后单独混合。

![本地中文重配图解：下载视频、Whisper定位、TTS2读正确稿，比较原声、未对齐配音和最终短句对齐后的真实波形](docs/guide/04-voice.jpg)

白衬衫这次是先生成整稿，再切成 **12 个短语**对齐；30 秒成片第一句约在 **0.85 秒**发声，不能把整条新配音直接从 0 秒铺上去。这里调整的是声音的起止和节奏，嘴部画面保留，不能保证改错词后逐字嘴型都一致。[本次实际做法与可复用命令 →](docs/redubbing.md)

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
