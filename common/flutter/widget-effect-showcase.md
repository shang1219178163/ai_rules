---
name: widget-effect-showcase
description: >-
  把 Flutter 组件 Demo 改成可动态调节全部属性并即时预览的效果展示页。
  Use when the user asks 组件效果展示, 动态调整属性, 查看显示效果, playground,
  property panel, 同样改造 XxxDemo, 美化 XxxDemo, or to expose all constructor/options
  of a widget in a demo. After the playground is in place, slim the same file
  before finishing.
alwaysApply: false
---

# 组件效果展示

把现有 Demo 改成「上方预览、下方调参」的实验页，覆盖目标组件**全部**构造参数，改完立刻看到效果。

参考：`lib/pages/demo/CarouselViewDemo.dart`、`lib/pages/demo/CarouselSliderDemo.dart`。

## 铁律

1. **属性来自源码**：读 SDK / pub-cache 里的构造函数与 `Options` 类，不要凭记忆列属性。多个构造函数（如 `CarouselView` / `.weighted`、`CarouselSlider` / `.builder`）都要能切换。
2. **只暴露组件自己的 API**：不要加组件没有的演示开关，除非它映射到真实参数（如 `height` 覆盖 `aspectRatio` 时用 `useHeight`）。
3. **保留原预览内容**：原 Demo 的 children / 图片 / 卡片继续用。
4. **只改点名的 Demo 文件**：用 StrReplace；不要抽公共 Playground 框架到其它文件。
5. **默认值对齐原 Demo**：重置后应回到改造前的观感；其余参数用官方默认值。
6. **美化完立刻精简**：属性覆盖不能少；只砍重复结构。不要等用户再说「代码精简」。

## 布局

```
Scaffold
  AppBar：标题 + 重置
  body: Column
    预览区（不随控制面板滚动）
    Expanded + Scrollbar + SingleChildScrollView
      控制面板
```

- 预览区浅底 + 底部分割线，看出组件边界。
- 切到纵向滚动且预览过矮时，自动加大高度。
- 回调要看得见：`onTap` → SnackBar；`onPageChanged` → 预览下方状态字。

## 控件映射

| 属性类型 | 控件 |
|---------|------|
| `double` / `int` | `NSlider`，`leading` 固定宽度标签 |
| 小数（0~1、aspectRatio） | `NSlider` + `trailingBuilder` 保留 2 位小数 |
| `Duration` | 滑块，显示 `4s` / `800ms` |
| `bool` | `SwitchListTile(dense: true)` |
| enum / 有限集合 | `NSectionBox` + `Wrap` + `ChoiceChip` |
| `Color?` | 色点用 `AppColor.colorOptions`，含「默」表示 `null` |
| `ShapeBorder` | rounded / stadium 等预设 + 半径滑块 |
| `ScrollPhysics?` | platform / bouncing / clamping / never |
| `Curve` | `NDecorationCard.curvePresets`，不开放任意 Curve |
| 构造函数分支 | ChoiceChip；切换后重建 controller / Key |

某参数只属于某个构造函数或某开关打开才生效时，用 `if` 隐藏，不要堆一排无效滑块。

## 流程

1. 定位 Demo 与目标 Widget。
2. 打开 Flutter SDK 或 pub-cache 源码，列出全部构造参数和 Options 字段。
3. 改成 `StatefulWidget`；沿用该 Demo 已有的 `hideApp` / `Get` / `title`。
4. 按上表铺控制面板；事件方法一律 `onX`。
5. 下列变化必须换 `ValueKey` 并重建 controller（若有）：构造方式、`scrollDirection`、`reverse`、`initialPage` / `initialItem`、无限循环。
6. 其余数值/开关 `setState` 即可，让 `didUpdateWidget` 生效。
7. AppBar 提供重置，重置时同步重建 controller。
8. **按「美化后精简」再收一轮**，属性覆盖保持不变。
9. `dart analyze` 目标文件；闭包参数不要写类型。
10. 不要 commit。

## 美化后精简

铺完面板后立刻精简同一文件，不要另开一轮等用户催。

- 琐碎赋值类 `onX` 收到 `onMark(String event, [VoidCallback? apply])`：`apply` 里改字段，再写 `lastEvent`、`setState`。
- 卡片合并到 2～3 张；`NDescriptionCard` 只留 1～2 条。
- `bool?` 用 `[null, true, false]` Chip，不要为三态再写 `_Tri`。
- 小映射用 `switch` 表达式。
- 去掉组件 API 以外的 controller / ValueNotifier / 空 `onPressed`。
- 不要抽公共 Playground helper 到其它文件。

## 代码约定

- 中文注释；函数内不留空行。
- 每文件一个公共类型；页面专属分支 enum 用 `_` 前缀私有。
- `ShapeKind` / `ClipKind` / `OverlayKind` 用 `n_decoration_card.dart` 顶部公共枚举，不要在 Demo 里再写一份。
- helper 留在同一 State：`buildSlider` / `buildSwitch` / `buildChoiceChips`。卡片内容 `Column` 用 `crossAxisAlignment: CrossAxisAlignment.start`，子项默认左对齐。
- 色点一律 `AppColor.colorOptions`，不要在 Demo 里再写一份数组。
- `Alignment` 一律 `AlignmentExt.allCases`，不要在 Demo 里再写九宫方位数组。
- `Curve` 一律 `NDecorationCard.curvePresets`，Chip 文案用 `NDecorationCard.nameOfCurve`，不要在 Demo 里再写一份预设。
- `SwitchListTile` 不要设置 `inactiveTrackColor`。不要给 `NSlider` 传 `inactiveColor`。
- 禁止 `print`，用 `DLog` / `debugPrint`。

## 不要做

- 不要为调参再加 GetX controller。
- 不要把预览放进同一个 `SingleChildScrollView`（嵌套滚动会拖死轮播）。
- 不要猜测包 API。Flutter 自带 `CarouselController`、carousel_slider v4 `CarouselController`、v5 `CarouselSliderController` 会重名，按实际 import 来。
