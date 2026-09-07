---
name: flutter-premium-ui-design
description: >-
  Flutter 高级感 UI 设计 8 条技巧：卡片留白、克制纯黑、柔和阴影、统一圆角、精简排版层级、
  微交互、空状态引导、骨架屏加载。Use when 打造高级感/精致/上档次 Flutter 界面, premium/polished UI,
  UI 看起来"差点意思"/太粗糙/太像 Demo, design polish, 或写卡片/阴影/圆角/排版/交互/空态/加载态。
alwaysApply: false
---

# Flutter 高级感 UI 设计 8 条技巧

功能相同的两个 App，一个让人心甘情愿付费，一个像练手 Demo。区别不在功能多寡，而在**微小的 UI 细节**。
Flutter 提供了强大组件，但真正精致的界面来自组件被**组合**的方式。当页面"技术正确却视觉差点意思"时，用下面 8 条逐一排查。

核心心法：**高级感 UI 很少是"添加更多"，而是"减少摩擦和视觉噪音"。**

---

## 1. 给卡片更多"呼吸空间"

不要把所有东西塞进一张卡片。与其增加装饰，**不如增加空间**。

- 用宽裕的 `padding`、一致的间距、更少的可视元素。
- 一张内部间距 **16–24px** 的简约卡片，通常比过度装饰的卡片好看得多。

> 核心原则：**留白本身就是一种设计元素。**

```dart
Padding(
  padding: const EdgeInsets.all(20), // 16–24 给出充足呼吸感
  child: Card(
    margin: EdgeInsets.zero, // 由外层统一控制间距
    elevation: 0, // 装饰交给阴影 skill，不在卡片里堆
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [/* ... */]),
    ),
  ),
)
```

## 2. 停止使用纯黑色

`Colors.black` 在白色背景对比下显得刺眼。用更柔和的深色做主文本，浅灰做辅助信息，不引入新颜色即可建立层级。

```dart
// ✅ 推荐
const primaryText = Color(0xFF1C1C1E);   // 主文本，柔和的近黑
const secondaryText = Color(0xFF8E8E93); // 辅助信息灰

// ❌ 而非
const primaryText = Colors.black;
```

## 3. 像用调味料一样使用阴影

高级感界面几乎不会让元素"浮"在屏幕上方，用的是**微妙的高程**。巨大深暗的阴影让卡片过时；低透明度柔和阴影提供恰到好处的分离感。

> 目标不是让阴影**被看见**，而是让它的**缺席**被察觉。

```dart
// ✅ 柔和
BoxShadow(
  color: Colors.black.withOpacity(0.08),
  blurRadius: 16,
  offset: Offset(0, 4),
)

// ❌ 刺眼
BoxShadow(
  color: Colors.black.withOpacity(0.3),
  blurRadius: 8,
  offset: Offset(0, 2),
)
```

## 4. 统一圆角半径

随机的圆角半径最破坏视觉节奏。卡片 16px、按钮 12px、对话框 28px 且毫无理由，界面就"拼凑"。
**建立小圆角系统并复用。**

```dart
// 定义设计令牌（design tokens），全局复用
const radiusSmall = 8.0;
const radiusMedium = 12.0;
const radiusLarge = 16.0;
const radiusXLarge = 24.0;
```

## 5. 将排版视为设计系统

不需要 10 种字体大小，精简层级即可：

| 层级 | 用途 |
|------|------|
| 大标题 Large Heading | 页面主标题 |
| 章节标题 Section Heading | 卡片标题、分组名 |
| 正文 Body Text | 主要内容 |
| 辅助/说明 Caption | 提示、时间戳 |

> 关键在**一致性**。排版层级清晰的页面，往往比堆满昂贵插画的页面更显精致。

```dart
// 统一 token，避免每处手写数字
const textLarge = TextStyle(fontSize: 28, fontWeight: FontWeight.w700, color: primaryText);
const textSection = TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: primaryText);
const textBody = TextStyle(fontSize: 15, height: 1.5, color: primaryText);
const textCaption = TextStyle(fontSize: 12, color: secondaryText);
```

## 6. 添加微交互

瞬间切换状态的按钮"能用"；轻触时微妙响应的按钮才"有生命力"。这些小交互值得做：

- 按下时轻微**缩放**
- 图标变化时的**过渡动画**
- 内容切换用**淡入淡出**而非生硬替换
- 加载状态加**平滑动画**
- 用 `AnimatedContainer` 处理简单过渡

> 保持交互**快速**。动画应该传达信息，而不是让用户等待（通常 ≤ 200ms）。

```dart
AnimatedContainer(
  duration: const Duration(milliseconds: 200),
  curve: Curves.easeInOut,
  transform: Matrix4.identity()..scale(isPressed ? 0.95 : 1.0),
  child: ...,
)
```

## 7. 精心设计空状态

空屏幕不该被当"残羹剩饭"。没有通知/收藏/记录时，不要只展示空 `ListView`。
**解释发生了什么 + 下一步能做什么**，把"什么都没有"变成有引导的旅程起点。

> 空状态不是终点，而是用户旅程的起点。

```dart
// 空状态 = 图标 + 一句解释 + 行动按钮，而不是空列表
Column(
  mainAxisAlignment: MainAxisAlignment.center,
  children: [
    const Icon(Icons.inbox_outlined, size: 56, color: secondaryText),
    const SizedBox(height: 12),
    const Text('还没有收藏', style: textBody),
    const SizedBox(height: 4),
    const Text('点击 ❤ 把你喜欢的内容收藏在这里', style: textCaption),
    const SizedBox(height: 16),
    FilledButton(onPressed: _goDiscover, child: const Text('去发现')),
  ],
)
```

## 8. 不要忽视加载状态

让应用显"未完成"的最简单方式，就是到处放转圈 Spinner。内容较重页面用**骨架屏 / 部分加载**。
用户应在网络请求完成前，就理解内容将出现在哪里。

```dart
// 骨架屏 vs 转圈圈
if (state.isLoading) {
  return ShimmerPlaceholder(); // 告诉用户"这里将出现什么"
} else {
  return ContentWidget(data);
}
```

---

## 高级感 UI 检查清单

在添加下一个渐变、动画或装饰元素之前，先自检：

- [ ] 间距是否一致？（同一套间距 token）
- [ ] 层级是否明显？（主/次文本、分组标题清晰）
- [ ] 颜色是否克制？（无纯黑、无刺眼阴影、调色板收敛）
- [ ] 圆角是否统一？（同一套 radius token）
- [ ] 交互是否有响应？（微缩放 / 过渡，且够快）
- [ ] 加载状态是否刻意为之？（骨架屏优先于 Spinner）
- [ ] 每个元素是否都有明确目的？（无用装饰就是噪音）

## 铁律

1. **留白优先于装饰**：间距不够时先加空间，别加渐变/描边/插画。
2. **颜色克制**：主文本用 `#1C1C1E` 一类近黑，辅助用灰度；避免裸 `Colors.black`。
3. **阴影低透明**：`withOpacity(0.05–0.12)`、`blurRadius ≥ 12`；过度深暗显得过时。
4. **圆角成系统**：全局 radius token，不要每处手写。
5. **排版少而精**：4 层足矣，保持一致；不要 10 种字号。
6. **微交互快**：≤ 200ms；动画传达信息，不拖时间。
7. **空状态给引导**：解释 + 下一步行动，拒绝裸空列表。
8. **骨架屏优先**：内容重页面用 skeleton/部分加载，胜过一个转圈圈。

## 反例

```dart
// ❌ 纯黑 + 硬阴影 + 随机圆角 + 堆装饰
Card(
  elevation: 8,
  color: Colors.white,
  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
  child: Padding(
    padding: const EdgeInsets.all(8), // 太挤
    child: Text('内容', style: TextStyle(color: Colors.black, fontSize: 15, fontWeight: FontWeight.bold)),
  ),
)
```
