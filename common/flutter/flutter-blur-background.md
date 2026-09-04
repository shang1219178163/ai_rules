---
name: flutter-blur-background
description: >-
  Flutter 整页高斯模糊背景：用 Container DecorationImage 铺图 + ClipRect/BackdropFilter 模糊 + 半透明遮罩，
  Scaffold 透明叠内容。Use when implementing 高斯模糊背景, blur background, BackdropFilter page background,
  frosted/blurred avatar cover background, or LiveEndView-style full-page blur.
alwaysApply: false
---

# Flutter 整页高斯模糊背景

参考实现：`lib/pages/live_room_v2/widget/live_end_view.dart`。

## 结构（不要用 Stack 铺背景）

```
Container（decoration 铺网络图 / 底色）
 └─ ClipRect
     └─ BackdropFilter（ImageFilter.blur）
         └─ ColoredBox（半透明遮罩，保证文字可读）
             └─ Scaffold(backgroundColor: transparent)
                 └─ 页面内容
```

## 模板

```dart
import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';

Widget buildBlurBackground({
  required String imageUrl,
  required Widget child,
  double sigma = 40,
  Color overlay = const Color(0xA3000000), // ~64% black
}) {
  return Container(
    decoration: BoxDecoration(
      color: Colors.black,
      image: imageUrl.isEmpty
          ? null
          : DecorationImage(
              image: CachedNetworkImageProvider(imageUrl),
              fit: BoxFit.cover,
            ),
    ),
    child: ClipRect(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: sigma, sigmaY: sigma),
        child: ColoredBox(
          color: Colors.black.withValues(alpha: 0.64),
          child: Scaffold(
            backgroundColor: Colors.transparent,
            body: child,
          ),
        ),
      ),
    ),
  );
}
```

## 铁律

1. **模糊只作用背景**：`BackdropFilter` 模糊的是其**背后**的 `DecorationImage`，不要用 `ImageFiltered` 包住整页（会把文字/按钮一起糊掉）。
2. **必须 `ClipRect`**：包住 `BackdropFilter`，避免模糊越界与性能问题。
3. **`Scaffold` 透明**：`backgroundColor: Colors.transparent`，否则盖住模糊层。
4. **遮罩**：叠 `ColoredBox` / `Container`（如 `Colors.black.withValues(alpha: 0.64)`），保证白字可读。
5. **铺图**：`BoxFit.cover` 铺满；空 URL 时只用底色，不要传空 `NetworkImage`。
6. **不要用 `Stack` 叠背景层**（除非设计明确要求多层叠加）；优先 `Container.decoration` + `BackdropFilter`。
7. **import**：需要 `import 'dart:ui';`（`ImageFilter`）。

## BottomSheet / 弹层注意

页面含 `Scaffold` + `Expanded` 时：

- 父级若是 `SingleChildScrollView`（无限高度），会触发 `RenderCustomMultiChildLayoutBox ... infinite size`。
- 用 `BottomSheetHelper.showCustom` 时传 `isScrollable: false`，并用 `heightFactor` / 有界约束包住子树。

## 参数建议

| 参数 | 建议 | 说明 |
|------|------|------|
| `sigmaX/Y` | `40` | 头像/封面作背景时够糊；可按稿面调 24–50 |
| overlay alpha | `0.64` | 对齐常见暗色稿；浅色稿可降低 |
| `fit` | `BoxFit.cover` | 裁切铺满，避免留边 |

## 反例

```dart
// ❌ 模糊了整页内容
ImageFiltered(
  imageFilter: ImageFilter.blur(sigmaX: 40, sigmaY: 40),
  child: Scaffold(body: pageContent),
)

// ❌ Stack 多层背景（本 skill 不采用）
Stack(children: [blurredImage, overlay, Scaffold(...)])
```
