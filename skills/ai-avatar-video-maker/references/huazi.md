# 口播工程

使用 `prepare_edit.py --video <成片.mp4> --timeline <tl.json> --output <新目录>`；视频尺寸以源视频为准。可选 `--voice`、`--music`、`--stickers` 和 `--badge`；输出全部另存。进入新工程 `npm install`，再用 `bash scripts/render.sh <新成片.mp4>`。

字幕由实际时间轴和文本驱动。默认不加载示例文案、示例角色或自动白闪；贴纸的文本和时间由使用者提供。视觉和音频效果需要实际检查，单线程渲染不是消除所有渲染问题的保证。
