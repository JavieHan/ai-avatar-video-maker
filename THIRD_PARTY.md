# Third-party components / 第三方组件

| Component | Where | License | Notes |
|---|---|---|---|
| [Remotion](https://www.remotion.dev/) | npm dependency of every template | [Remotion License](https://www.remotion.dev/license) | Free for individuals and companies of up to 3 people; larger companies need a company license. 个人和 3 人以内公司免费，更大公司需购买授权。 |
| [Google Noto Emoji Animation](https://googlefonts.github.io/noto-emoji-animation/) | `templates/*/public/emoji/*.json` | CC BY 4.0 | Credit "Animated emoji: Google Noto" in videos that use them. 使用时署名。 |
| [lottie-web](https://github.com/airbnb/lottie-web) | npm | MIT | Plays the Noto emoji frame by frame. |
| [world-atlas](https://github.com/topojson/world-atlas) | npm | ISC | Data from [Natural Earth](https://www.naturalearthdata.com/) (public domain). Check border depictions against local rules for formal publications. |
| [d3-geo](https://github.com/d3/d3-geo), [topojson-client](https://github.com/topojson/topojson-client) | npm | ISC | Map projection. |
| [whisper.cpp](https://github.com/ggerganov/whisper.cpp) | installed by you | MIT | Speech recognition for QA and alignment. |
| Apple Vision | macOS system framework | Apple SDK | Person segmentation for the text-behind effect (`scripts/personmask.swift`, compiled locally on first use; macOS only). |

Services you connect with your own account / 需要你自己账号的服务:
- Muse — 本分支通过用户现有应用/网页生成，额度、能力和素材条款以实际服务为准；不安装或连接上游远程生成 MCP。
- [Xiaomi MiMo](https://platform.xiaomimimo.com/) — an independent optional TTS service; not integrated in this release. Use only voices you own or are licensed to use.

Upstream research reports and demo visuals are not included in this community release. See the upstream repository for their descriptions and terms.

本发行版保留部分上游包装组件源码，但默认工程仅安装基础渲染依赖；自行接入其他组件时，应自行核对并安装各组件所需依赖及其许可。
