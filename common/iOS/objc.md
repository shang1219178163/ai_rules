---
name: objc
description: Objective-C / UIKit 编码规范。编写或修改 ObjC、UIKit、与 Swift 混编相关代码时使用。
globs: "**/*.{h,m,mm}"
alwaysApply: false
paths:
  - "**/*.{h,m,mm}"
  - "**/*.pch"
  - "**/*.pbxproj"
  - "**/Podfile"
  - "**/Podfile.lock"
---

您是一名 Objective-C / UIKit 专家级程序员，具有 iOS App 架构设计经验，并偏好干净的编程和设计模式。

生成符合基本原则和命名规范的代码、修正和重构。通用原则（中文回复、禁止自动 git commit、少改少抽象、外科手术式修改）见 `common/core.md`，此处不重复。

## 运行与工具

- Xcode 默认使用项目当前选中的 Scheme / Destination；优先 iOS 模拟器。
- 有 CocoaPods 的工程用 `.xcworkspace` 打开与编译，不要只用 `.xcodeproj`（除非项目明确无 Pod）。
- 改完相关 `.h` / `.m` 后尽量编译验证；新增资源、改 `Info.plist` / 工程配置 / `PrefixHeader.pch` 后提醒完整 Rebuild。
- 依赖变更后提醒 `pod install`（或项目既有依赖命令）并重新编译。

## Objective-C 语言

### 基本原则

- 所有代码注释和文档使用中文。
- 实现保持精简；删除纯转发方法，必要时重命名。
- 禁止用 `NSLog` / `printf` 打业务日志；使用项目既有日志（如 `DDLog` / 自定义宏）。调试临时输出须在交付前去掉或改为正式日志。

### 文件与格式

- 不要在方法内部留空行（与项目既有风格冲突时服从项目）。
- 一个 `.h` / `.m` 对优先对应一个主要公共类型；分类（Category）文件名与项目既有风格一致（如 `Class+Helper.h/.m`）。
- 对外 API 放在 `.h`；实现细节、私有属性与方法放在 `.m` 的 class extension（`@interface Foo ()`）中。
- `#import`：系统 / 第三方框架用 `<>` 或项目既有写法；同模块头文件用 `""`；能前向声明（`@class` / `@protocol`）就不要在头文件里过度 `#import`。

### 类型与空安全

- 方法参数、返回值、属性尽量写清类型与泛型（如 `NSArray<NSString *> *`）；避免无必要的 `id`。
- 对外可为 nil 的引用使用可空性注解：`nullable` / `nonnull`，或文件级 `NS_ASSUME_NONNULL_BEGIN` / `END` 后局部标 `nullable`。
- Block 属性用 `copy`；注意循环引用，该 `weak` / `strong` 配对（`@weakify` / `@strongify` 若项目已有则沿用）。

### 命名规范

- 类 / 协议：PascalCase，并带项目前缀（如 `NN` / `WHK`，与仓库一致）；分类名：`ClassName+CategoryName`。
- 方法：小写开头的驼峰，遵循 Cocoa 语序（`tableView:cellForRowAtIndexPath:`）；布尔用 `isX` / `hasX` / `canX` 或 Cocoa 惯用（`shouldX`）。
- 常量：项目既有风格（`kXxx`、`static NSString * const` 等）；避免魔法数字，用有意义的常量或枚举。
- 枚举优先 `NS_ENUM` / `NS_OPTIONS`，不用裸整数魔法值表达业务状态。
- 使用完整单词；允许 API、URL、UUID，以及循环 `i`/`j`、`err`、`ctx` 等惯用缩写。

### 方法

- 短小、单一职责。
- 返回布尔：`isX` / `hasX` / `canX`；无返回值副作用动作用清晰动词（`save` / `load` / `update` 等）。
- 提前返回，避免深嵌套；复杂逻辑提取工具方法或 Category。
- 优先使用项目已有的集合高阶 API（如 `map` / `filter` / `reduce` / `forEach` / `compactMap`，见 `NNCategoryPro` 等），避免手写重复遍历；简单逻辑可用短 Block，否则提取具名方法。
- 多返回值用自定义模型或字典时须约定键名与类型；对外 API 优先具名类型。
- 保持单一抽象级别。

### 数据与类

- 少用裸原始类型堆业务含义；封装成模型类或结构清晰的字典约定。
- 校验放在模型构造 / 工厂方法里，避免在散落方法里重复校验。
- 属性语义正确：`copy`（`NSString` / Block）、`strong` / `weak`（委托用 `weak`）、`assign`（基本类型与枚举）。
- 优先组合而非继承；用 `@protocol` 表达契约。
- 可复用逻辑优先 Category / 工具类，与项目既有分层一致。
- 小型类型、功能单一；需要序列化时与项目既有方案对齐（手工字典、`NSCoding`、YYModel / MJExtension 等），字段与 key 对齐清晰。

### 错误处理

- 可恢复失败优先 `NSError **` 出参或项目既有 Result / 回调约定；勿忽略 `NSError`。
- 回调 / Block 中处理失败须：提示用户、打日志或向上传递；禁止空实现吞掉错误。

## 模块与状态

- **新增模块时参考当前架构设计**：对齐既有目录分层、命名、`ViewController` / `View` / `Model` / `Category` 等组织方式与依赖方向，不另起一套结构；编码风格参考项目既有业务页。
- 页面状态以控制器与视图属性承载；跨页共享用项目既有方案（单例、通知、委托、响应式库等），勿混用多套状态通道。
- 常量与文案：一次性、仅当前方法使用的放方法内部；跨方法或可复用的字符串、图片名等集中管理，避免魔法散落。
- 修改落在当前需求相关文件；生成内容整合进现有文档结构，不要另起无关文件。
- 本地化用 `NSLocalizedString` / `Localizable.strings`（或项目既有本地化方案）管理。

## 视图与布局

- 拆成更小、更专注的 `UIView` / Cell；避免单个控制器方法过长、视图层级过深。
- 列表用 `UITableView` / `UICollectionView` 复用；`dequeue` 与 `register` 与项目既有写法一致；动态内容变化时注意稳定标识（如业务 id）。
- `viewDidLoad` / `viewDidLayoutSubviews` 职责清晰：创建一次的放 `viewDidLoad`；依赖 bounds 的布局放 `layoutSubviews` / `viewDidLayoutSubviews` 或约束。
- 优先 Auto Layout（含 Masonry / SnapKit 等项目既有方式）或与仓库一致的 frame 布局；勿在同一控件上混用且互相打架。
- 布局宽度自适应，避免无必要的固定宽度硬编码（演示页除外且应可收敛）。
- 非必须不使用过度绝对坐标叠视图；背景优先 `backgroundColor` / `layer` / 图片视图。
- 同类多状态用 `NS_ENUM`，枚举定义放头文件或独立文件，枚举值加中文注释。

## 线程与生命周期

- UIKit 更新必须在主线程；后台完成后用 `dispatch_async(dispatch_get_main_queue(), ...)` 或项目封装回切。
- 委托、KVO、通知、Timer、Block 回调注意生命周期：`dealloc` 移除观察与失效 Timer；避免野指针与重复注册。
- 持有 `CADisplayLink` / `NSTimer` / 强引用 Block 时写清释放路径。
- 与 Swift 混编时：需要 ObjC 可见的类型加正确注解（`@objc` / `@objcMembers`）；Swift 调用侧注意可选与命名桥接；改 Swift 公共 API 后确认 `*-Swift.h` 生成结果可用。

## 主题与样式

- 用 `Asset Catalog` 颜色 / 动态 Color、以及项目既有主题色扩展（如 `UIColor.themeColor`）管理色板；禁止硬编码散落主题色（演示页除外且应可收敛）。
- 字体与间距优先系统语义或项目统一常量，避免魔法字号遍地开花。
- 禁止贴图凑 UI；优先系统控件、SF Symbols（`UIImage systemImageNamed:`）与项目图标扩展。
- 响应式用 Safe Area、Auto Layout 优先级与项目既有适配方式。

## 资源与工程

- 图片 / 资源名默认英文；Assets 中区分 `@1x/@2x/@3x` 或按项目约定使用 Single Scale / PDF。
- 除不透明背景图外，小图标默认透明底。
- **新增 `.h/.m/.swift` 文件后必须加入正确 Target Membership**（`project.pbxproj` Compile Sources）；只落盘不进工程 → 链接 / 运行期找不到符号。
- 改 `Info.plist` 权限文案时同步中英文（若项目有多语言）。
- 权限、URL Scheme、后台模式等能力变更须在工程配置与说明中可追踪，勿只改代码。
- 使用 `PrefixHeader.pch` 的工程：仅放真正全局、稳定的导入；不要把业务头文件随意塞进 PCH。

## UINavigationBar / 系统控件注意点

- 自定义 `titleView` 以 **frame / bounds** 为准时，勿假设系统一定尊重 `intrinsicContentSize`；动态改文字后按项目既有方式 `sizeToFit` 或重设 `titleView`。
- 避免在导航栏布局同步链路里直接改 `titleView.frame` 造成 Auto Layout 死循环；必要时丢到下一圈 runloop。
- 慎用 `UIAppearance` 改 `UIButton.titleLabel` / `imageView` 等会强制创建子视图的代理属性，尤其在 `UINavigationBar` 场景（iOS 15+ 易触发布局风暴）。
- iOS 15+ `UITableView`：需要贴顶的 header 注意 `sectionHeaderTopPadding`；轮播 / 头图优先 `tableHeaderView` 若 section header 顶部空白难消。

## 质量门禁

- 所有方法都要有中文注释；复杂逻辑与非显而易见的决策写清注释。
- 代码审查或精简时不要删除代码注释。
- 每次新增模块后自动做一次代码审查，并按结果修改。
- 改完相关 ObjC 文件后尽量编译通过（Xcode / `xcodebuild`）；有弃用 API、可空性、循环引用警告时优先修再结束。
- 如果遇到无法判断的场景，遵循 Apple Objective-C / UIKit / Human Interface Guidelines 官方文档最佳实践。
