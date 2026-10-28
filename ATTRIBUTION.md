# 来源与改造 / Attribution and modifications

本仓库基于 [andyhuo520 / Berryxia 的 digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo)，最初参考的上游版本为 [`5fa9b19f52fb8920c83567468fa30e8391b8c503`](https://github.com/andyhuo520/digital-human-koubo/commit/5fa9b19f52fb8920c83567468fa30e8391b8c503)。感谢原作者开源项目和工作流程。

This repository is adapted from [digital-human-koubo](https://github.com/andyhuo520/digital-human-koubo) by andyhuo520 / Berryxia, based on upstream commit [`5fa9b19`](https://github.com/andyhuo520/digital-human-koubo/commit/5fa9b19f52fb8920c83567468fa30e8391b8c503). We thank the upstream author for the code and workflow.

## 沿用和改造的内容 / Reused and adapted

- **后期思路与时间轴**：参考原项目的分段检查、Whisper 比稿、字幕时间轴和 Remotion 口播工程组织。`scripts/align.py`、`scripts/assemble.py` 等以原项目代码为基础，已针对本版文件和审核流程修改。
- **包装参考与源码**：保留上游 `references/packaging-playbook.md` 和包装预设，并保留 `templates/huazi-916/src/kit/` 中原项目的部分组件和 `src/icons/` 的相关源码。默认基础口播画面经过重写；保留的高级组件没有全部接入默认工程，可能需要额外依赖和开发。
- **本地辅助工具**：`scripts/check_edit.py`、`scripts/cutout_video.py`、`scripts/personmask.swift` 等保留上游代码；`scripts/voicefx/` 在上游实现基础上调整。Google Noto 表情等第三方素材及工具的使用条件见 [THIRD_PARTY.md](THIRD_PARTY.md)。

The local alignment/assembly scripts adapt upstream code; the upstream packaging playbook and presets, selected original Remotion components and local utilities are retained. The default composition is rewritten, and retained advanced components are not all wired into it. Third-party terms are listed separately.

## 此版本新增 / Added in this edition

Muse 界面配合的离线请求及真实视频导入、人工选剪点后的尾帧图片接力、图片哈希检查、可选短语配音替换、防覆盖处理、干净的基础工程和自动测试，均针对本版流程新增或调整。Muse 参考图并非硬首帧锁定；后期配音不是音频驱动口型。

This edition adds or adapts the offline Muse workflow, reviewed tail-frame handoffs, reference-image hash checking, optional manually timed dubbing, no-overwrite safeguards, a clean base composition, and tests. Image reference is not hard first-frame locking; post-production dubbing does not drive lip movement.

## 许可和示例 / License and media

上游代码和文档的 [MIT LICENSE](LICENSE) 与 [NOTICE.md](NOTICE.md) 保留原作者署名。本发行版不包含原作者的示例主播照片、展示图、演示视频，也不包含本次使用者的人像、声音或视频。第三方依赖与外部服务有各自条款，代码的 MIT 许可不替代这些条款。

The upstream [MIT license](LICENSE) and [notice](NOTICE.md) retain the original copyright. Upstream demo presenters, pictures and videos, and this user's media are not included. External dependencies, services and media have their own terms.
