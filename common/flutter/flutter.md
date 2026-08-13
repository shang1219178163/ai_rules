---
name: flutter
description: Flutter/Dart 编码规范。编写或修改 Dart/Flutter 代码时使用。
globs: "**/*.dart,**/pubspec.yaml,**/analysis_options.yaml"
alwaysApply: false
paths:
  - "**/*.dart"
  - "**/pubspec.yaml"
  - "**/analysis_options.yaml"
---

您是一名 Flutter 专家级程序员，具有 Flutter 框架和 App 架构设计的经验，并偏好干净的编程和设计模式。

生成符合基本原则和命名规范的代码、修正和重构。通用原则（中文回复、禁止自动 git commit、少改少抽象、外科手术式修改）见 `common/core.md`，此处不重复。

## 运行与工具

- Flutter SDK 默认使用 fvm 默认版本。
- 运行优先当前已选择的设备（`flutter devices` / IDE Destination）；若未选择则优先 iOS 模拟器。
- 调整完 UI 后执行 hot reload；新增/变更 assets 或 `pubspec.yaml` 后提醒热重启或 `flutter pub get`。

## Dart 语言

### 基本原则

- 所有代码注释和文档使用中文。
- 实现保持精简；删除纯转发函数，必要时重命名。
- 禁止 `print()`, 使用 `debugPrint()`。

### 文件与格式

- 不要在函数内部留空行。
- 每个文件只导出一个公共类型（必要时允许同文件私有 Widget）。
- `typedef` 定义放在文件顶部。

### 类型注解

- 函数参数、返回值、公共 API（含 Widget 构造参数、类字段）始终声明类型；避免 `dynamic` / 不必要的弱类型。
- `map` / `builder` 等闭包参数不需要类型注解。
- 方法内部或 `StatefulWidget` 的 `State` 中：字面量可写类型；`final` 与其它本地变量一般不写类型注解。

### 命名规范

- 类：PascalCase；变量 / 函数 / 方法：camelCase；文件与目录：underscores_case；环境变量：UPPERCASE。
- 避免魔法数字，用有意义的常量管理常量值。
- 函数名以动词开头；布尔用 `isX` / `hasX` / `canX` 等。
- 使用完整单词；允许 API、URL，以及循环 `i`/`j`、`err`、`ctx`、`req`/`res`/`next` 等惯用缩写。

### 函数

- 本条同样适用于方法。
- 短小、单一职责。
- 返回布尔：`isX` / `hasX` / `canX`；无返回值：`executeX` / `saveX` 等。
- 提前返回，避免深嵌套；复杂逻辑提取工具函数。
- 优先高阶函数（`map` / `where` / `fold` 等）；简单逻辑用箭头函数，否则用具名函数。
- 用默认参数，而不是空检查凑默认值。
- 多参数 / 多返回值用对象传递并声明类型。
- 保持单一抽象级别。

### 数据与类

- 少用裸原始类型堆业务含义；封装成复合类型。
- 校验放在带内部验证的类型里，避免在散落函数里校验。
- 优先不可变；字面量用 `const`（Dart 用 `final` / `const` 表达不变性）。
- 优先组合而非继承；用抽象类 / 接口表达契约。
- 优先使用 `extension` 管理可复用逻辑。
- 小型类、功能单一；需要序列化的模型提供 `fromJson` / `toJson`。

### 异常

- 用异常处理非预期错误。
- 捕获时须：修复预期问题、补充上下文，或交给全局处理；禁止空 `catch`。

## 模块与状态

- **新增模块时参考当前架构设计**：对齐既有目录分层、命名、`page` / `controller` / `widgets` / `model` 等组织方式与依赖方向，不另起一套结构；编码风格参考 `lib/pages` 既有业务页。
- 页面 / 模块数据：若有 `controller.dart`，其中仅保存集合类型；其余非集合变量转为方法 / 组件函数本地变量。
- 常量与文案：一次性、仅当前方法使用的放函数内部；跨方法或可复用的字符串、图片路径等用成员集合 / 变量集中管理，避免魔法散落。
- 控制器接受方法（动作）作为输入，并更新影响 UI 的状态。
- 优先 `StatelessWidget`；需要本地 UI 状态再用 `StatefulWidget`。
- 不要在 `setState(() { ... })` 回调内部写业务逻辑；先算好状态再 `setState` 触发重建（或先改字段再调用无逻辑的 `setState`）。
- 修改落在当前需求相关文件；生成内容整合进现有文档结构，不要另起无关文件。
- 翻译用 `AppLocalizations`（或项目既有本地化方案）管理。

## Widget 与布局

- 拆成更小、更专注的 Widget；避免过深嵌套（可读性、状态与性能）。
- 需要 `const` 或隔离重建时，优先抽独立 Widget，少用返回 Widget 的私有方法；若仍用私有方法，不以下划线开头（与项目既有风格一致）。
- 能 `const` 的构造函数尽量 `const`，减少重建。
- 列表用 `ListView.builder` 等按需构建；列表项在结构可能变化时加 `Key`（如 `ValueKey`）。
- `State` 中创建的 `AnimationController` / `TextEditingController` / `ScrollController` / `FocusNode` 等，在 `dispose` 中释放。
- 组件宽度自适应，避免无必要的固定宽度。
- 非必须不使用 `Stack` / `Positioned`；背景图优先 `Container.decoration.image`。
- 同类多状态用 `enum`，枚举定义放类外（独立文件或文件顶层），枚举值加中文注释；尽量把该状态下的相关参数收进枚举侧。

## 主题与样式

- 用 `ThemeData` 管理主题；不要重复创建整份 `ThemeData`。
- 主题色变化优先走 `ThemeData.colorScheme`（或项目既有 `AppColorModel` 等扩展），禁止硬编码散落主题色。
- 禁止贴图凑 UI；优先内置组件与自定义绘制；不规则外形可用自绘。
- 响应式用 `LayoutBuilder` 或 `MediaQuery`。

## 资源与 pubspec

- assets 文件名默认英文下划线。
- Figma导出小图标默认透明底。大图或背景图要带背景色。
- 导入 / 导出 **WebP** 默认带透明通道（alpha）；勿用带白底截图直接转 WebP。从 SVG 或带 alpha 的 PNG 转出，并用 `webpinfo`（或等价）确认 `Alpha: 1`。占位图、空状态插画、小图标一律透明底；仅全屏 / 卡片不透明背景图可例外。
- 在 `assets/`（含 `assets/images/` 等）下**新增文件夹**时，必须在 `pubspec.yaml` 的 `flutter.assets` 注册该路径（例如 `- assets/images/common/`）。
  - 只落盘不注册 → 运行时 `Unable to load asset`。
  - 父目录已注册不能替代本仓库对子目录的显式条目；与现有 `pubspec.yaml` 一致，单独加一行。
  - 任务结束前确认已注册。

## Web（仅 Web 目标）

- 使用 `package:web` + `dart:js_interop`；禁止 `js_interop_unsafe` 与 `dart:html`。

## 质量门禁

- 所有方法 / 函数都要有中文注释；复杂逻辑与非显而易见的决策写清注释。
- 代码审查或精简时不要删除代码注释。
- 新增较大模块或架构相关改动时，交付前做一次自审并按结果修改；小改动以 analyze / 编译通过为准。
- 改完相关 Dart 文件后跑 `dart analyze`（或项目既有分析命令），有问题先修再结束。
- 如果遇到无法判断的场景，遵循官方 Flutter 文档最佳实践。
