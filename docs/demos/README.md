# 演示样稿 / Video samples

这两条成片由本项目维护者提供并明确授权在此展示，不是上游 digital-human-koubo 的演示人物或作品。完整 MP4 放在 [样稿 Release](https://github.com/JavieHan/ai-avatar-video-maker/releases/tag/samples-v1)，不打包进源码下载。

| 样稿 | 规格 | 制作内容 |
|---|---|---|
| [白衬衫口播](https://github.com/JavieHan/ai-avatar-video-maker/releases/download/samples-v1/talking-head-stickers.mp4) | 30 秒，704×1088，30 fps | Muse 分段生成与剪接，TTS2 6 号音色，按发声点后期对齐，字幕、暖黄贴纸和配乐；展示的是闪帧修正版。 |
| [小雅优雅版](https://github.com/JavieHan/ai-avatar-video-maker/releases/download/samples-v1/xiaoya-elegant.mp4) | 27 秒，736×1248，24 fps | Muse 分段口播与舞蹈，TTS2 10 号音色，古琴古筝配乐和收尾混音。 |

这些是经过人工审看、剪点调整和本地后期制作的成片，用来展示工作流程的结果，不代表默认基础模板一键产生相同效果。后期换声不驱动视频嘴型。公开内容为两条成片及教程所需截图、图解；角色母版文件、原始音频和私有会话不随仓库分发。

These two finished samples were provided and approved for display by this project's maintainer. They are not the upstream author's demo media. They include manual review, editing, external TTS and post-production; they do not claim one-click generation or audio-driven lip animation. MP4 hashes and technical metadata are listed in [samples.json](samples.json).

## 配乐来源 / Music credits

**白衬衫口播：** `M35_轻松对话`，维护者提供的配乐，制作记录标记为 Google Lyria 3 Pro 生成；本片进行了截取、音量调整及混音。未单独分发音乐原件，不将其标为代码 MIT 素材。

**小雅优雅版：**

- “guqin-concert-2.wav” by **xserra** — [Freesound 原始页面](https://freesound.org/people/xserra/sounds/162029/)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。本片对素材进行了截取、保音高放慢至 0.75 倍速、音量调整、淡入淡出与混音。
- “guzheng solo” by **neolein** — [Freesound 原始页面](https://freesound.org/people/neolein/sounds/472707/)，[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)。本片截取了前 8 秒并调整音量、淡入淡出与混音。

The code's MIT license does not grant rights to reuse sample characters, voices, or third-party music. Individual music licenses remain applicable.

## 首页图解的来源 / Walkthrough figures

- `01-plan.jpg`：两条公开成片的人物截图，用于说明短句和动作规划，不是可供下载的角色母版。
- `02-handoff.jpg`、`03-join.jpg`：白衬衫角色的早期真实接力测试。第一段原片 10 秒，实际保留 173 帧 / 30 fps；从保留片导出的末帧为 F172，PTS 5.733333 秒。此图确实作为第二段的图片参考；对照图右侧是该次生成的第二段 F0。它没有硬首帧锁定证据，第二段声音曾因错词或含糊未通过用户验收。
- 这些早期测试帧只用于解释取尾帧、上传与接点检查，不能当作两条公开成片的真实分段或剪点记录。两条成片的原始 Muse 分段记录未随项目提供；不把 10 秒、20 秒猜作它们的生成接点。
- `04-voice.jpg`：曲线来自白衬衫 V4 工程的最终人声音轨；字幕块与时间取自该工程 `tl.json`。它说明短句时间安排，不代表已验证逐音素口型。
- `05-finish.jpg`：白衬衫包装前、后都是 11 秒的对应帧；小雅为公开 V3 的 8 秒口播、23 秒动作帧。

The handoff comparison is a real earlier test of the same white-shirt character, not a claimed reconstruction of either sample's generation history. Other figures use final-sample screenshots, the corresponding unwrapped footage and the final voice track. Diagrams are explanations, not Muse interface screenshots or proof of locked-frame generation.
