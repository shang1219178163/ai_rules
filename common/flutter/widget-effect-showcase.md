---
name: widget-effect-showcase
description: >-
  把 Flutter 组件 Demo 改成可动态调节全部属性并即时预览的效果展示页。
  Use when the user asks 组件效果展示, 动态调整属性, 查看显示效果, playground,
  property panel, 同样改造 XxxDemo, 美化 XxxDemo, 代码精简 playground,
  美化后精简, slim XxxDemo, or to expose all constructor/options
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
- 回调要看得见：`onTap` → `SnackUtil.show(...)`；`onPageChanged` → 预览下方状态字（`lastEvent`）。不要在效果展示页写本地 `onSnack` / `ScaffoldMessenger.of(context).showSnackBar`。

## 控件映射

| 属性类型 | 控件 |
|---------|------|
| `double` / `int` | `NSliderListTile`（`title` 为标签；`sliderWidthFactor` 默认 `0.5`，相对**整块**宽度） |
| 小数（0~1、aspectRatio） | `NSliderListTile` + `valueBuilder` 保留 2 位小数 |
| `Duration` | 同上，`valueBuilder` 显示 `4s` / `800ms` |
| `bool` | `NSwitchListTile` |
| enum / 有限集合 | `NChoiceChipListItem` |
| `Color?` | `NChoiceColorListItem`（圆形色点，默认 `AppColor.colorOptions`，含「默」表示 `null`） |
| `ShapeBorder` | rounded / stadium 等预设 + 半径滑块；形状枚举用公共 `ShapeKind` |
| `ScrollPhysics?` | `PhysicsKind`（platform / always / bouncing / clamping / never） |
| `Curve` | `NDecorationCard.curvePresets`，不开放任意 Curve |
| 构造函数分支 | `NChoiceChipListItem`；切换后重建 controller / Key |

某参数只属于某个构造函数或某开关打开才生效时，用 `if` 隐藏，不要堆一排无效滑块。

调参控件 **直接写在卡片 `children` 里**，禁止再套一层只转调公共组件的方法：

| 禁止（套壳） | 直接用 |
|-------------|--------|
| `buildSlider(...)` | `NSliderListTile(...)` |
| `buildSwitch(...)` | `NSwitchListTile(...)` |
| `buildChoiceChips` / `buildColorDots` / `buildColorRow` | `NChoiceChipListItem` / `NChoiceColorListItem` |

典型滑块（调用处内联，不要抽 `buildSlider`）：

```dart
NSliderListTile(
  dense: true,
  contentPadding: EdgeInsets.zero,
  title: const Text('height'),
  min: 120,
  max: 400,
  value: height.clamp(120, 400),
  onChanged: (v) => onMark('height ${v.round()}', () => height = v),
  activeColor: theme.colorScheme.primary,
);
```

import：

```dart
import 'package:flutter_templet_project/basicWidget/list_tile/n_slider_list_tile.dart';
import 'package:flutter_templet_project/basicWidget/list_tile/n_switch_list_tile.dart';
import 'package:flutter_templet_project/basicWidget/list_tile/n_choice_chip_list_item.dart';
import 'package:flutter_templet_project/basicWidget/list_tile/n_choice_color_list_item.dart';
```

- 不要用 `NSlider` / `Slider.adaptive` / 固定像素 `sliderWidth` 做属性面板滑块。
- `sliderWidthFactor` 是整块 `NSliderListTile` 的占比，不是标题剩下来的空间；默认 **0.5**。数值 / 时长放在这 50% 槽里（`valueBuilder`），避免 Row overflow。
- 不要传 `inactiveColor`。
- **保留**有真实结构的 `buildPreview` / `buildConstructCard` / `buildBody` 等；只删「参数进、组件出」的薄包装。

## 流程

1. 定位 Demo 与目标 Widget。
2. 打开 Flutter SDK 或 pub-cache 源码，列出全部构造参数和 Options 字段。
3. 改成 `StatefulWidget`；沿用该 Demo 已有的 `hideApp` / `Get` / `title`。
4. 按上表铺控制面板；赋值回调直接走 `onMark`，不要先堆一堆 `onX` 再等精简。
5. 下列变化必须换 `ValueKey` 并重建 controller（若有）：构造方式、`scrollDirection`、`reverse`、`initialPage` / `initialItem`、无限循环。
6. 其余数值/开关 `setState` 即可，让 `didUpdateWidget` 生效。
7. AppBar 提供重置，重置时同步重建 controller。
8. **按「美化后精简」再收一轮**，属性覆盖保持不变。
9. `dart analyze` 目标文件；闭包参数不要写类型。
10. 不要 commit。

## 美化后精简

铺完面板后立刻精简同一文件，不要另开一轮等用户催。**属性覆盖不能少，预览行为不能变。**

### 收 onX

琐碎赋值收到 `onMark`：

```dart
void onMark(String event, [VoidCallback? apply]) {
  apply?.call();
  lastEvent = event;
  setState(() {});
}
```

调用处：`onChanged: (v) => onMark('foo $v', () => foo = v)`。

**保留**有副作用的方法，不要内联丢逻辑：

- 重建 `controller` / `ValueKey`（构造方式、`scrollDirection`、`reverse`、`initialPage` / `initialItem`、无限循环）
- min / max 互相钳制
- SnackBar 反馈用 `SnackUtil.show`（`import 'package:flutter_templet_project/util/snack_util.dart';`），不要本地 `onSnack` / 手写 `ScaffoldMessenger.showSnackBar`
- focus、`showSearch`、鉴权流程
- `onReset`（全量还原并重建 controller）

### 收结构

- `NDecorationCard` 合并到 2～3 张。常见拆法：「构造+行为 / 表面 / 尺寸」或「构造+尺寸 / 表面+行为」。
- `NDescriptionCard` 只留 1～2 条，不要再写一条只解释 `lastEvent`。
- `bool?` 用 `[null, true, false]` Chip，不要为三态再写 `_Tri`。
- 小映射（`nameOfX` / `shapeOf` / `clipOf`）用 `switch` 表达式；若映射绑在页面私有 enum 上，优先收进枚举字段（见「枚举收状态」），不要在 State 里再留一份。
- 去掉组件 API 以外的 controller / ValueNotifier / 空 `onPressed`。
- 不要抽公共 Playground helper 到其它文件。
- **去掉套壳方法**：删除 `buildSlider` / `buildSwitch` / `buildChoiceChips` / `buildColorDots` 等薄包装，调用处直接写 `NSliderListTile` / `NSwitchListTile` / `NChoiceChipListItem` / `NChoiceColorListItem`。
- **枚举收状态**：页面私有 `_XxxKind` 把 Chip 文案、对应 API 值、静态 Widget 等合并进枚举（命名参数）；删掉 State 里平行的 `nameOfX` / `labelOf` switch / `*Of()` 薄映射。

### 枚举收状态

页面专属 enum 的「文案 / 静态值 / 静态 Widget」进枚举字段，不要散落在 State。参考 `AutoLayoutDemo._PrefixKind`、`PlatformDispatcherDemo._ListenKind`。

```dart
enum _PrefixKind {
  none(label: 'none', widget: SizedBox.shrink()),
  notice(
    label: 'Icon',
    widget: Padding(
      padding: EdgeInsets.only(right: 6),
      child: Icon(Icons.notifications_active),
    ),
  );

  const _PrefixKind({required this.label, required this.widget});
  final String label;
  final Widget widget;
}
```

调用处：`labelOf: (e) => e.label`，取值用 `prefixKind.widget` / `physicsKind.physics` 等。

- 构造用**命名参数**；字段顺序：先 `label`，再其它。
- 仅 `e.name` 且无额外映射时可不加 `label`。
- 依赖 State / Theme / controller 的动态构建（Zoom 参数、日期依赖 `now`、Anchor builder）可留在 State；能收的静态部分仍进枚举。
- 不要改公共 `ShapeKind` / `ClipKind` / `OverlayKind` / `PhysicsKind`。

### 批量精简（用户点名 `lib/pages/demo`）

- 只收效果展示页（有 `NDecorationCard` / 属性面板），不要动业务页（聊天、商城、天气等）。
- 多代理并行时文件列表互斥，禁止两路改同一文件。
- 每文件先 Read 再 StrReplace；禁止 Write 整文件覆盖。
- 每个文件 `/Users/shang/fvm/default/bin/dart analyze <file>` 干净再交差。
- 不要改 `lib/basicWidget/`（含 `n_slider_list_tile.dart`），除非用户点名。
- 不要 commit。

## 代码约定

- 中文注释；函数内不留空行。
- 每个 `State` **顶部只声明一次** `late final theme = Theme.of(context);`。方法里不要再写 `Theme.of(context)` / `final theme = Theme.of(context)`；需要配色时用 `theme.colorScheme`（或方法内 `final scheme = theme.colorScheme`）。文件里每个 `StatefulWidget` 各自声明自己的 `theme`。
- 每文件一个公共类型；页面专属分支 enum 用 `_` 前缀私有，相关文案/静态值收到枚举命名字段（见「枚举收状态」）。
- `ShapeKind` / `ClipKind` / `OverlayKind` / `PhysicsKind` 用 `n_decoration_card.dart` 顶部公共枚举，不要在 Demo 里再写一份。`ShapeKind` 已含 `label` / `radius` / `borderRadius()` / `shape()` / `outlinedBorder()`；`ClipKind` 含 `label` / `clip`；`OverlayKind` 含 `label` / `style`；`PhysicsKind` 含 `label` / `physics`。Demo 直接用枚举字段，不要再写 `shapeOf` / `clipOf` / `overlayOf` / 私有 `_PhysicsKind`。页面自己的缺口形状（如 BottomAppBar `NotchedShape`）继续用私有 `_ShapeKind`。
- 调参控件在卡片内直接写 `NSliderListTile` / `NSwitchListTile` / `NChoiceChipListItem` / `NChoiceColorListItem`，不要再套 `buildSlider` / `buildSwitch`。卡片内容 `Column` 用 `crossAxisAlignment: CrossAxisAlignment.start`，子项默认左对齐。ListItem 间距用 `const SizedBox(height: 8)`（不要用 16）。
- 色点一律 `AppColor.colorOptions`，不要在 Demo 里再写一份数组。
- `Alignment` 一律 `AlignmentExt.allCases`，不要在 Demo 里再写九宫方位数组。
- `Curve` 一律 `NDecorationCard.curvePresets`，Chip 文案用 `NDecorationCard.nameOfCurve`，不要在 Demo 里再写一份预设。
- `SwitchListTile` 不要设置 `inactiveTrackColor`。不要给 `NSlider` / `NSliderListTile` 传 `inactiveColor`。
- 禁止 `print`，用 `DLog` / `debugPrint`。
- 不要在效果展示页为私有 enum 另写 `nameOfX` / Chip `switch` 文案表（应收进枚举 `label`）。
- 交互反馈用 `SnackUtil.show(message)`；需要同步 `lastEvent` 时配合 `onMark`，不要再写 `onSnack`。

## 不要做

- 不要为调参再加 GetX controller。
- 不要把预览放进同一个 `SingleChildScrollView`（嵌套滚动会拖死轮播）。
- 不要猜测包 API。Flutter 自带 `CarouselController`、carousel_slider v4 `CarouselController`、v5 `CarouselSliderController` 会重名，按实际 import 来。
- 不要把 `sliderWidthFactor` 当成「标题剩下空间的占比」。
- 不要在精简 Demo 时顺手改 `NSliderListTile` 组件本身。
- 不要在效果展示页保留 `buildSlider` / `buildSwitch` 等只包装公共 list_tile 的套壳方法。
- 不要把私有 enum 的 Chip 文案 / 静态 API 值散落在 State 的 `switch` / `nameOfX` 里（应收进枚举）。
- 不要在效果展示页手写 `ScaffoldMessenger.of(context).showSnackBar` / 本地 `onSnack`（用 `SnackUtil.show`）。
