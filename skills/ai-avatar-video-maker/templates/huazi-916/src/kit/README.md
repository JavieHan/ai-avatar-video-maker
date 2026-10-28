# 上游高级包装组件

这里保留了 digital-human-koubo 的 Map、Beast、Wangan、Depth 等组件源码，作为扩展参考。默认工程入口 [Huazi.tsx](../Huazi.tsx) 没有引用这些组件，默认 TypeScript 检查也仅包含基础工程入口。

这些组件不属于默认依赖安装范围。例如 `Map.tsx` 需要 `d3-geo`、`topojson-client` 与 `world-atlas`；`src/icons/NotoEmoji.tsx` 的 Lottie 播放需要 `lottie-web`。准备启用时，应先阅读对应源码、补齐依赖及类型声明，并按实际画幅调整布局。

基础口播的字幕和可选贴纸直接在 `Huazi.tsx` 中实现。保留组件的来源、代码许可及第三方素材条款见仓库根目录 `ATTRIBUTION.md`、`LICENSE` 与 `THIRD_PARTY.md`。
