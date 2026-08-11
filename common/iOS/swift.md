---
name: swift
description: Swift/SwiftUI 编码规范。编写或修改 Swift / SwiftUI 代码时使用；UIKit 混编或改 ObjC 时同时参考 objc。
globs: "**/*.swift,**/Package.swift"
alwaysApply: false
paths:
  - "**/*.swift"
  - "**/Package.swift"
---

您是一名 Swift / SwiftUI 专家级程序员，具有 iOS App 架构设计经验，并偏好干净的编程和设计模式。

生成符合基本原则和命名规范的代码、修正和重构。通用原则（中文回复、禁止自动 git commit、少改少抽象、外科手术式修改）见 `common/core.md`，此处不重复。横切安全 / 日志 / 性能 / 测试见 `common/shared/`，此处只写 Swift / SwiftUI 特有约束。涉及 `.h/.m/.mm` 或厚重 UIKit 坑时参考同目录 `objc.md`。

目标：以工程语言模式与并发设置为准；新代码优先现代 API（async/await、Actor、Observation、最新 SwiftUI）。能启用 Swift 6 / Strict Concurrency 时对齐工程；否则在现有模式下避免数据竞争与主线程违规。避免废弃 API 与 completion-handler 风格异步（遗留代码对接除外）。

## 运行与工具

- Xcode 用当前 Scheme / Destination；优先当前已选择的设备，若未选择则优先 iOS 模拟器。
- 改完相关 Swift 后尽量编译验证；有分析流程时再跑 Analyze / SwiftLint。UI 微调可用 Previews（若已启用）；改资源 / `Info.plist` / 工程配置后提醒完整 Rebuild。
- SPM / CocoaPods 变更后提醒解析并重编（Resolve Packages / `pod install` / `xcodebuild`）。
- 有 SwiftLint 的项目改完须通过其规则。

## Swift 语言

### 基本原则

- 所有代码注释和文档使用中文。
- 实现保持精简；删除纯转发函数，必要时重命名。
- 禁止 `print` 打业务日志；用项目既有日志（`DDLog` / `Logger` / `os.Logger`）。
- 禁止重复造轮子、无必要依赖、过度封装与无价值抽象层；不破坏现有公共 API。

### 文件与格式

- 不要在函数内部留空行。
- 每个文件优先一个主要公共类型（`struct` / `class` / `enum` / `actor`）；必要时允许同文件私有辅助类型与小型 View。
- `typealias`、文件级常量放在文件顶部；类型内分区可用 `// MARK: -`。
- 内部实现优先 `private` / `fileprivate`；SPM 模块对外 API 显式 `public`。

### 类型注解

- 函数参数、返回值、公共 API（含 View 初始化参数、存储属性）始终写清类型；避免无必要的 `Any` / 无约束泛型。
- 闭包参数、`map` / `compactMap` / `ForEach` 等可推断处不必重复注解。
- 方法内部：字面量可写类型；`let` / `var` 本地变量在类型可明显推断时一般不写注解。

### 命名规范

- 类型：UpperCamelCase；变量 / 函数 / 方法：lowerCamelCase；文件与项目既有风格一致（如 `*_ext.swift`）；编译期常量 / 环境变量：UPPERCASE。
- 避免魔法数字，用有意义的常量或 `enum` 管理。
- 函数名以动词开头（副作用如 `save` / `load` / `update`）；布尔用 `isX` / `hasX` / `canX` 等。
- 使用完整单词；允许 API、URL、UUID，以及循环 `i`/`j`、`err`、`ctx` 等惯用缩写。
- 遵循 Swift API Design Guidelines。

### 函数

- 本条同样适用于方法。
- 短小、单一职责；保持单一抽象级别。
- 返回布尔：`isX` / `hasX` / `canX`；无返回值副作用用清晰动词（`save` / `load` / `update` 等）。
- 提前返回，避免深嵌套；复杂逻辑提取工具函数或 `extension`。
- 优先高阶函数（`map` / `filter` / `compactMap` / `reduce` 等）；简单逻辑用短闭包，否则用具名函数或局部函数。
- 用默认参数，而不是散落的 `nil` 合并凑默认值。
- 多参数 / 多返回值用对象传递并声明类型；对外 API 优先具名类型。

### 数据与类

- 少用裸原始类型堆业务含义；封装成复合类型。
- 校验放在类型构造 / 工厂方法里，避免在散落函数里重复校验。
- 优先 `struct` / `enum` + `let`；仅在需要身份、引用语义、UIKit/AppKit 继承或明确生命周期时用 `class`。
- 优先组合而非继承；用 `protocol` 表达契约。
- 优先使用 `extension` 管理可复用逻辑（含 `*_ext.swift`）。
- 小型类型、功能单一；需要序列化的模型用 `Codable`（或项目既有方案，如 SmartCodable），字段与 key 对齐清晰。

### Optional

- 禁止业务路径随意 `!` 强制解包；优先 `guard let` / `if let` / `??` / 可选链。
- `try!` / `as!` 仅在可证明不会失败处使用，并写清理由。

### 异常

- 可恢复失败用 `throws` / `Result`；非预期用断言或日志；禁止空 `catch` 与无说明的 `try!`。
- 捕获时须：处理预期情况、补充上下文再抛 / 上报，或交给统一错误层；勿用 `print(error)` 代替处理。

### Protocol 与依赖

- Protocol 只做真实抽象（可替换实现、可测边界）；禁止为「架构感」堆无意义协议。
- 新代码优先构造注入；避免新增 `Service.shared` 式全局单例（项目既有单例可沿用，勿扩散）。

### 内存

- 闭包 / `Task` 捕获注意循环引用；需要时用 `[weak self]`，并处理 `self?` 为 nil。
- `Timer` / `CADisplayLink` / 通知 / KVO 写清失效与移除路径。

## 模块与状态

- **新增模块时参考当前架构设计**：对齐既有目录分层、命名、`page` / `View` / `Models` / `Navigation` / `extension` 等组织方式与依赖方向，不另起一套结构；编码风格参考项目既有业务页。
- 绿场或明确重构时可采用 MVVM（View / ViewModel / Model）+ Coordinator/导航 + Repository/Service；分层职责：
  - **View**：布局、交互、状态绑定；不直接网络 / 持久化 / 业务规则。
  - **ViewModel（或等价层）**：页面状态、用例编排、展示用数据转换；UI 相关标 `@MainActor`。
  - **Repository / Service**：API、缓存、持久化与外部 I/O。
- 页面本地 UI 状态优先 `@State` / `@Binding`；跨视图共享用项目既有方案，勿混用多套状态库：

| 场景 | 方式 |
|------|------|
| 页面内部状态 | `@State` |
| 父子绑定 | `@Binding` |
| 环境 / 依赖 | `@Environment` / `@EnvironmentObject`（跟项目） |
| 新状态模型 | `@Observable` |
| 老项目兼容 | `ObservableObject` + `@StateObject` / `@ObservedObject` |

- 新代码优先 `@Observable`。`@ObservedObject` / `@StateObject` / `@EnvironmentObject` **仅用于** SwiftUI `View`；普通 helper 用普通引用，避免非 View 挂属性包装器触发 MainActor 隔离错误。
- 常量与文案：一次性、仅当前方法使用的放函数内部；跨方法或可复用的字符串、图片名等集中管理，避免魔法散落。
- 修改落在当前需求相关文件；生成内容整合进现有文档结构，不要另起无关文件。
- 本地化用 `String(localized:)` / `Localizable.xcstrings`（或项目既有本地化方案）管理。
- 改前先读结构与依赖；保持 API 兼容；说明关键修改点；不做无关重构。

## View 与布局

- 拆成更小、更专注的 `View`；避免 `body` 过深嵌套（可读性、状态与性能）。
- 需要隔离重建或复用时，优先抽独立 `View`，少用返回 `some View` 的私有方法；若仍用私有方法，命名与项目既有风格一致。
- 列表用 `List` / `LazyVStack` / `LazyHStack` 等懒加载；动态列表项在结构可能变化时加稳定 `id`。
- 少用 `AnyView`；避免高频无意义 `@State` 更新与主线程重活；图片缓存 / 异步加载 / 重计算放后台（详见 `shared/performance.md`）。
- `UIViewRepresentable` / `UIViewControllerRepresentable` 的 Coordinator 与桥接对象注意生命周期；在 `make` / `update` 中保持职责清晰。
- 布局宽度自适应，避免无必要的固定宽度；优先 `frame(maxWidth:)`、`padding`、`Spacer` 与对齐指南。
- 非必须不使用过度 `ZStack` / 绝对偏移；背景优先 `.background` / `overlay`。
- 同类多状态用 `enum`，枚举定义放类型外（独立文件或文件顶层），枚举值加中文注释；尽量把该状态下的相关参数收进枚举侧。

## 主题与样式

- 用 Asset Catalog 颜色 / 动态 Color、以及项目既有主题扩展管理色板；禁止硬编码散落主题色（演示页除外且应可收敛）。
- 字体与间距优先系统语义或项目统一 Token，避免魔法字号遍地开花。
- 禁止贴图凑 UI；优先系统组件、SF Symbols 与自定义 `Shape` / 绘制。
- 响应式用 `GeometryReader`、`ViewThatFits`、Size Class 或项目既有适配方式。

## 资源与工程

- 图片 / 资源名默认英文；Assets 中区分 `@1x/@2x/@3x` 或用 Single Scale + 矢量（PDF/SVG）按项目约定。
- 除不透明背景图外，小图标默认透明底。
- 新增资源 / `.swift` 文件后确认已加入正确 Target Membership；改 `Info.plist` 权限文案时同步中英文（若项目有多语言）。
- 权限、URL Scheme、后台模式等能力变更须在工程配置与说明中可追踪，勿只改代码。

## 并发（Swift 特有）

- 优先 `async`/`await` 与 `Task`；新 API 避免 completion handler（对接遗留除外）。
- UI / `@Observable` / `ObservableObject` 更新在 `@MainActor`；后台用 `MainActor.run` 或隔离类型回切，少散落 `DispatchQueue.main.async`。
- 新增类型默认考虑隔离（SwiftUI `View`、UIKit 回调等多已在主线程）；跨线程共享状态显式 `@MainActor`、值传递或 `actor`。
- 勿给持有 `UIImage` 等非 Sendable 的类型轻易标 `Sendable`；`@unchecked Sendable` 须有理由。
- `Task` 取消与视图生命周期可预期；勿在后台线程碰 UIKit/SwiftUI 状态。

## UIKit（Swift 侧，若涉及）

- 避免 Massive ViewController：拆 View / 逻辑层 / 导航；`viewDidLoad` 只做 `setup` + `bind` 类编排；禁止在 `init` 里访问 `view`（触发过早加载）。
- UI 更新必须主线程；列表 Cell 必须复用；优先 Auto Layout，尊重 Safe Area。
- 委托 / 通知 / `Timer` / `CADisplayLink` 写清移除与失效路径。
- 更细的 ObjC/UIKit 踩坑与 Cocoa 命名见同目录 `objc.md`；纯 `.h/.m` 改动由 `objc` 规则覆盖，本规则不再匹配这些扩展名。

## SPM（若项目使用）

- 模块边界清晰（如 Core / Networking / UIComponents / Features）；公共 API 显式 `public`，内部默认不暴露。
- 禁止无必要的跨模块反向依赖。

## 质量门禁

- 所有方法 / 函数都要有中文注释；复杂逻辑与非显而易见的决策写清注释。
- 代码审查或精简时不要删除代码注释。
- 新增较大模块或架构相关改动时，交付前做一次自审并按结果修改；小改动以编译 / 分析通过为准。
- 新增可测逻辑时补充或更新测试（XCTest / Swift Testing）；优先覆盖 ViewModel/Repository/Service 等非 UI 层（通则见 `shared/testing.md`）。
- 改完相关 Swift 文件后尽量编译通过（Xcode / `xcodebuild`）；有并发、隔离、弃用 API 警告时优先修再结束。
- 如果遇到无法判断的场景，遵循 Apple Swift / SwiftUI / HIG 与 Swift API Design Guidelines。
