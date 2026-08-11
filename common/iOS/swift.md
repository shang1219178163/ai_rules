---
name: swift
description: Swift/SwiftUI 编码规范。编写或修改 Swift / SwiftUI / UIKit 混编代码时使用。
globs: "**/*.{swift,h,m,mm}"
alwaysApply: false
paths:
  - "**/*.swift"
  - "**/*.{h,m,mm}"
  - "**/Package.swift"
  - "**/*.pbxproj"
---

您是一名 Swift / SwiftUI 专家级程序员，具有 iOS App 架构设计经验，并偏好干净的编程和设计模式。

生成符合基本原则和命名规范的代码、修正和重构。通用原则（中文回复、禁止自动 git commit、少改少抽象、外科手术式修改）见 `common/core.md`，此处不重复。

## 运行与工具

- Xcode 默认使用项目当前选中的 Scheme / Destination；优先 iOS 模拟器。
- 改完相关 Swift 文件后尽量编译验证；UI 微调可用 Previews / 热重载（若项目已启用），新增资源或改 `Info.plist` / 工程配置后提醒完整 Rebuild。
- SPM / CocoaPods 依赖变更后提醒解析与重新编译（`xcodebuild` / Xcode Resolve Packages / `pod install`）。

## Swift 语言

### 基本原则

- 所有代码注释和文档使用中文。
- 实现保持精简；删除纯转发函数，必要时重命名。
- 禁止用 `print()` 打业务日志；使用项目既有日志（如 `DDLog` / `Logger` / `os.Logger`）。调试临时输出须在交付前去掉或改为正式日志。

### 文件与格式

- 不要在函数内部留空行。
- 每个文件优先一个主要公共类型（`struct` / `class` / `enum` / `actor`）；必要时允许同文件私有辅助类型与小型 View。
- `typealias`、文件级常量放在文件顶部（或紧挨首个类型之前）。

### 类型注解

- 函数参数、返回值、公共 API（含 View 初始化参数、类 / 结构体存储属性）始终写清类型；避免不必要的 `Any` / 无约束泛型。
- 闭包参数、`map` / `compactMap` / `ForEach` 等可推断处不必重复注解。
- 方法内部：字面量可写类型；`let` / `var` 本地变量在类型可明显推断时一般不写注解。

### 命名规范

- 类型：PascalCase；变量 / 函数 / 方法：camelCase；文件与目录：与类型名一致或项目既有风格（如 `*_ext.swift`）；环境变量 / 编译常量：UPPERCASE。
- 避免魔法数字，用有意义的常量或 `enum` 管理。
- 函数名以动词开头；布尔用 `isX` / `hasX` / `canX` 等。
- 使用完整单词；允许 API、URL、UUID，以及循环 `i`/`j`、`err`、`ctx` 等惯用缩写。

### 函数

- 本条同样适用于方法。
- 短小、单一职责。
- 返回布尔：`isX` / `hasX` / `canX`；无返回值副作用动作用清晰动词（`save` / `load` / `update` 等）。
- 提前返回，避免深嵌套；复杂逻辑提取工具函数或 `extension`。
- 优先高阶函数（`map` / `filter` / `compactMap` / `reduce` 等）；简单逻辑可用单行闭包，否则用具名函数或局部函数。
- 用默认参数，而不是散落的 `nil` 合并凑默认值。
- 多参数 / 多返回值用结构体或元组并声明类型；对外 API 优先具名类型。
- 保持单一抽象级别。

### 数据与类

- 少用裸原始类型堆业务含义；封装成复合类型。
- 校验放在类型构造 / 工厂方法里，避免在散落函数里重复校验。
- 优先不可变：能用 `struct` + `let` 就不用引用可变类；需要引用语义与观察再用 `class` / `@Observable` / `ObservableObject`。
- 优先组合而非继承；用 `protocol` 表达契约。
- 优先使用 `extension` 管理可复用逻辑（含按文件拆分的 `*_ext.swift`）。
- 小型类型、功能单一；需要序列化的模型遵循 `Codable`（或项目既有方案，如 SmartCodable），字段与 JSON key 对齐清晰。

### 错误处理

- 用 `throws` / `Result` 表达可恢复失败；非预期用断言或日志，勿空 `catch`。
- `catch` 时须：处理预期情况、补充上下文再抛出 / 上报，或交给统一错误层；禁止吞掉错误。

## 模块与状态

- **新增模块时参考当前架构设计**：对齐既有目录分层、命名、`page` / `View` / `Models` / `Navigation` / `extension` 等组织方式与依赖方向，不另起一套结构；编码风格参考项目既有业务页。
- 页面本地 UI 状态优先 `@State` / `@Binding`；跨视图共享用项目既有方案（`@Observable`、`ObservableObject` + `@StateObject` / `@ObservedObject`、环境对象等），勿混用多套状态库。
- `@ObservedObject` / `@StateObject` / `@EnvironmentObject` 仅用于 SwiftUI `View`；普通 helper / 服务类型用普通引用即可，避免在非 View 上挂属性包装器触发 MainActor 隔离错误。
- 常量与文案：一次性、仅当前方法使用的放函数内部；跨方法或可复用的字符串、图片名等集中管理，避免魔法散落。
- 修改落在当前需求相关文件；生成内容整合进现有文档结构，不要另起无关文件。
- 本地化用 `String(localized:)` / `Localizable.xcstrings`（或项目既有本地化方案）管理。

## View 与布局

- 拆成更小、更专注的 `View`；避免 `body` 过深嵌套（可读性、状态与性能）。
- 需要隔离重建或复用时，优先抽独立 `View`，少用返回 `some View` 的私有方法堆叠；若仍用私有方法，命名与项目既有风格一致。
- 列表用 `List` / `LazyVStack` / `LazyHStack` 等懒加载；动态列表项在结构可能变化时加稳定 `id`。
- `UIViewRepresentable` / `UIViewControllerRepresentable` 的 Coordinator 与桥接对象注意生命周期；在 `makeCoordinator` / `updateUIView` 中保持职责清晰。
- 布局宽度自适应，避免无必要的固定宽度；优先 `frame(maxWidth:)`、`padding`、`spacer` 与对齐指南。
- 非必须不使用过度 `ZStack` / 绝对偏移；背景优先 `.background` / `overlay`。
- 同类多状态用 `enum`，枚举定义放类型外（独立文件或文件顶层），枚举值加中文注释；尽量把该状态下的相关参数收进枚举侧。

## 并发与 Actor

- UI 与 `ObservableObject` / `@Published` / `@Observable` 更新必须在主线程；后台完成后用 `@MainActor` / `MainActor.run` / `DispatchQueue.main` 回切。
- 新增类型默认考虑隔离：SwiftUI `View`、UIKit 代理回调等多已在主线程；跨线程共享状态显式标注 `@MainActor` 或改为值传递 / actor。
- 勿给持有 `UIImage`、非 Sendable 引用类型的结构体轻易标 `Sendable`；需要跨并发域时用 `@unchecked Sendable` 须有充分理由并写清约束。
- `Task` / `async` 优先于随意开全局队列；取消与生命周期（视图消失）要可预期。

## 主题与样式

- 用 `Asset Catalog` 颜色 / 动态 Color、以及项目既有主题扩展管理色板；禁止硬编码散落主题色（演示页除外且应可收敛）。
- 字体与间距优先系统语义（`.font(.headline)` 等）或项目统一 Token，避免魔法字号遍地开花。
- 禁止贴图凑 UI；优先系统组件、SF Symbols 与自定义 `Shape` / 绘制。
- 响应式用 `GeometryReader`、`ViewThatFits`、Size Class 或项目既有适配方式。

## 资源与工程

- 图片 / 资源名默认英文；Assets 中区分 `@1x/@2x/@3x` 或用 Single Scale + 矢量（PDF/SVG）按项目约定。
- 除不透明背景图外，小图标默认透明底。
- 新增资源后确认已加入正确 Target Membership；改 `Info.plist` 权限文案时同步中英文（若项目有多语言）。
- 权限、URL Scheme、后台模式等能力变更须在工程配置与说明中可追踪，勿只改代码。

## 质量门禁

- 所有方法 / 函数都要有中文注释；复杂逻辑与非显而易见的决策写清注释。
- 代码审查或精简时不要删除代码注释。
- 每次新增模块后自动做一次代码审查，并按结果修改。
- 改完相关 Swift 文件后尽量编译通过（Xcode / `xcodebuild`）；有并发、隔离、弃用 API 警告时优先修再结束。
- 如果遇到无法判断的场景，遵循 Apple Swift / SwiftUI / Human Interface Guidelines 官方文档最佳实践。
