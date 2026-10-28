# 在 Codex / Claude Code 中一条命令配置

[返回首页](../README.md) · [先准备工具](tools.md) · [制作命令](usage.md)

## 终端执行

先安装 Git、Python 3，以及你使用的 Codex 或 Claude Code 客户端。在 macOS / Linux 运行：

```bash
git clone https://github.com/JavieHan/ai-avatar-video-maker.git
cd ai-avatar-video-maker
bash setup.sh both
```

只用一个工具时，把最后一行改为 `bash setup.sh codex` 或 `bash setup.sh claude`。

配置器把仓库内的同一份技能接到两个客户端的项目目录，然后运行 `doctor.sh` 检查依赖：

| 客户端 | 项目内入口 | 开始使用 |
|---|---|---|
| Codex | `.agents/skills/ai-avatar-video-maker` | 打开此仓库，输入 `$ai-avatar-video-maker` |
| Claude Code | `.claude/skills/ai-avatar-video-maker` | 在此仓库启动 Claude Code，输入 `/ai-avatar-video-maker` |

技能目录使用相对符号链接指向 `skills/ai-avatar-video-maker`，因此仓库更新后沿用同一份脚本与说明。该配置只作用于当前仓库，保留已有同名冲突文件；重复运行安全。目录规则来自 [Codex 官方文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)和 [Claude Code 官方文档](https://code.claude.com/docs/en/skills#choose-where-skills-load)。

若当前会话尚未发现技能，在这个仓库中新开一个会话，再调用上面的名字。Claude Code 可在 `/` 菜单检查入口。这里的 Claude 指本地 **Claude Code**；普通网页聊天和云会话使用各自的技能机制。

## 看懂配置结果

- **退出 0**：技能配置与依赖检查通过。
- **退出 3**：技能已经接入，但本地工具或 Whisper 模型尚未就绪；按报告补齐后再次运行。
- **退出 1 / 2**：配置冲突、写入失败或参数错误，按提示处理。

配置内容是项目技能入口与环境检查。Muse 账号、TTS2 等大模型、Whisper 权重和制作素材另行准备；见[工具与安装](tools.md)。环境检查通过之后，仍要在开始制作时核对账号能力、实际媒体与视听结果。

## 也可以直接把这段话交给 Agent

```text
请将 https://github.com/JavieHan/ai-avatar-video-maker 克隆到新的本地目录，
阅读 README.md 和 docs/agent-setup.md，运行 bash setup.sh both，
告诉我技能配置与环境检查各自是否通过，并列出缺少的依赖。
配置完成后，使用 ai-avatar-video-maker 技能，先和我确定人物图片、台词和声音，
再准备第一段 Muse 请求。
```

制作时可以这样开始：

```text
使用 ai-avatar-video-maker，帮我制作一条中文口播。
人物图片：<本地路径>
完整台词：<粘贴台词>
希望声音：<声音描述或有权使用的参考音频>
请先检查环境，给出分段稿和第一段请求，按 README 的图解流程推进。
```

其他能读取本地文件、执行命令的 Agent，可以直接读取 `skills/ai-avatar-video-maker/SKILL.md`。生成视频与审片仍需要实际操作 Muse；自动接入技能不等于自动完成整条成片。
