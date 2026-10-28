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
| [Breeze TTS 2](https://huggingface.co/BreezeBlue/Breeze-TTS-2) | optional external speech model; sample narration used a [community MLX port](https://huggingface.co/mlx-community/Breeze-TTS-2-mlx) | [BreezeBlue Research and Non-Commercial License](https://huggingface.co/BreezeBlue/Breeze-TTS-2/blob/main/LICENSE) | Model materials, derivatives and self-hosted outputs are for research/non-commercial use; inference code's Apache-2.0 does not grant commercial model rights. See [tool setup](docs/tools.md). |

Services you connect with your own account / 需要你自己账号的服务:
- [Muse by Meta](https://ai.meta.com/muse/) — 本分支通过用户现有应用/网页生成，额度、能力和素材条款以实际服务为准；[官方下载](https://ai.meta.com/muse/download/)。
- [Xiaomi MiMo](https://platform.xiaomimimo.com/) — an independent optional TTS service; not integrated in this release. Use only voices you own or are licensed to use.

Upstream research reports and demo visuals are not included in this community release. See the upstream repository for their descriptions and terms.

本发行版保留部分上游包装组件源码，但默认工程仅安装基础渲染依赖；自行接入其他组件时，应自行核对并安装各组件所需依赖及其许可。

`templates/huazi-916/public/emoji/` 还保留了来自上游仓库的静态 SVG 表情；其具体来源及适用许可尚未逐一核实。默认基础口播工程不使用这些 SVG；如需在自己的作品中使用，请先核对来源和许可。动态 JSON 的 CC BY 4.0 说明不应自动套用到这些静态文件。

首页样稿的配乐来源、作者、许可和修改方式见 [样稿配乐署名](docs/demos/README.md#配乐来源--music-credits)。
