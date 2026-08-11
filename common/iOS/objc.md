---
name: objc
description: Objective-C / UIKit 编码规范。编写或修改 ObjC、UIKit、与 Swift 混编相关代码时使用。
globs: "**/*.{h,m,mm}"
alwaysApply: false
paths:
  - "**/*.h"
  - "**/*.m"
  - "**/*.mm"
  - "**/*.pch"
  - "**/Podfile"
  - "**/Podfile.lock"
---

您是一名 Objective-C / UIKit 专家级程序员，具有 iOS App 架构设计经验，并偏好干净的编程和设计模式。

生成符合 Cocoa / Cocoa Touch 与 Apple 最佳实践的代码。通用原则（中文回复、禁止自动 git commit、少改少抽象、外科手术式修改）见 `common/core.md`，此处不重复。横切安全 / 日志 / 性能 / 测试见 `common/shared/`，此处只写 ObjC 特有约束。

目标：可编译无警告、ARC + Nullability、可维护、可测；优先官方 API 与项目既有代码，不随意改公共 API，不引入无必要第三方依赖。

## 运行与工具

- Xcode 用当前 Scheme / Destination；优先当前已选择的设备，若未选择则优先 iOS 模拟器。
- 有 CocoaPods 时用 `.xcworkspace` 编译，不要只用 `.xcodeproj`（除非项目无 Pod）。
- 改完相关 `.h` / `.m` 后尽量编译验证；改资源 / `Info.plist` / `PrefixHeader.pch` / 工程配置后提醒完整 Rebuild。
- 依赖变更后提醒 `pod install`（或项目既有命令）并重新编译。
- 格式与静态检查优先项目既有流程；可用 `clang-format`、`clang-tidy`、Xcode Static Analyzer、`XCTest`。

## Objective-C 语言

### 基本原则

- 注释与文档用中文；实现精简，删除纯转发方法。
- 业务日志禁止 `NSLog` / `printf`；用项目既有日志（如 `DDLog`）。生产日志禁止 Token / 密码 / 敏感用户信息（详见 `shared/logging.md`）。

### 文件与头文件

- 不要在方法内部留空行（与项目既有风格冲突时服从项目）。
- 文件名 PascalCase，与类型名一致（`UserManager.h/.m`）；Category：`Class+Role.h/.m`（如 `NSString+NXExtension`），避免 `NSObject+Common` 这类大杂烩。
- 一个 `.h/.m` 对优先一个主要公共类型；对外 API 在 `.h`，私有属性 / 方法在 `.m` 的 class extension。
- **头文件最小暴露**：`.h` 能 `@class` / `@protocol` 前向声明就不要 `#import` 实现头；`#import` 放 `.m`，减少编译依赖与循环引用。
- 系统 / 第三方用项目既有 `#import` 风格；PCH 仅放真正全局稳定的导入，勿塞业务头文件。

### 命名

- 类 / 协议：PascalCase + 项目前缀（与仓库一致，如 `NN` / `NX`）；忌用无意义的裸名 `Manager` / `Helper` / `Tool` / `Common`。
- 方法：Cocoa 语序驼峰（`loadUserWithIdentifier:`），勿写成 `getUser:` 这类含糊命名。
- 布尔：`is` / `has` / `should` / `can` / `enable`（如 `isLoading`）；忌 `loading`。
- 常量用项目既有风格（`kXxx`、`static NSString * const`）；状态用 `NS_ENUM` / `NS_OPTIONS`，忌魔法整数。
- 完整单词优先；允许 API、URL、UUID 及 `i`/`j`/`err`/`ctx` 等惯用缩写。

### 属性与 Nullability

- 语义：`copy`（`NSString` / 不可变集合 / Block）、`weak`（delegate）、`strong`（一般对象）、`assign`（标量 / 枚举）。
- Block 属性必须 `copy`；delegate / 协议回调对象禁止 `strong`（须 `weak`）。
- 新代码用 `NS_ASSUME_NONNULL_BEGIN/END`，可为 nil 处标 `nullable`；集合尽量写泛型（`NSArray<NSString *> *`），避免无必要 `id`。

### 方法与初始化

- 短小、单一职责、单一抽象级别；提前返回；复杂逻辑提取方法或 Category。
- 优先项目既有集合高阶 API（`map` / `filter` / `reduce` / `forEach` / `compactMap` 等），避免重复手写遍历；简单用短 Block，否则具名方法。
- 重复 Block 签名用 `typedef`（如 `typedef void (^NXCompletionBlock)(BOOL success);`）；`typedef` 放文件顶部或公共头。
- 多返回值 / 多参数对外 API 优先具名类型，少用散落字典约定。
- 指定初始化：`init` / `initWith…` 返回 `instancetype`；`self = [super init…]` 后再配置；禁止 `- (void)init`。
- UIView 统一 `setupUI`（或项目既有命名）完成子视图搭建。

### ARC 与循环引用

- 默认 ARC；禁止 `retain` / `release` / `autorelease` 与手动内存管理。
- Block 捕获 `self`：`__weak typeof(self) weakSelf = self;`，执行时 `__strong typeof(weakSelf) strongSelf = weakSelf;`（或项目 `@weakify` / `@strongify`）。
- 单例用 `dispatch_once` + `sharedInstance`（或项目既有写法）；勿滥用单例塞业务状态。

### 错误与模型

- 可恢复失败用 `NSError **` 或项目既有回调约定；勿静默 `return nil` / 空实现吞错。
- 业务层用模型对象承载数据（映射 / 默认值 / 校验在模型或工厂）；勿让裸 `NSDictionary` 贯穿各层。
- 序列化与项目既有方案对齐（手工字典、`NSCoding`、YYModel / MJExtension 等），字段与 key 清晰。
- 优先组合而非继承；用 `@protocol` 表达契约；可复用逻辑放 Category / 工具类。

## 架构与模块

- **对齐项目现有分层**：`Models` / `Views` / `Controllers` / `Services`（或仓库既有目录），不另起架构；编码风格参考既有业务页。
- ViewController 不堆：网络、复杂数据转换、厚重业务；下沉到 Service / 模型 / 既有中间层。
- 网络：`ViewController → Service → API Client`；禁止在 Controller 里直接铺 `NSURLSession` 业务请求（演示页除外）。
- 常量与文案：一次性用完的放方法内；跨方法复用的集中管理，避免魔法散落。
- 本地化：`NSLocalizedString` / 项目既有方案。
- 修改只落需求相关文件；不删公共接口与既有注释；不引入无必要第三方依赖。

## UIKit 与布局

- 拆小 `UIView` / Cell；Cell 只做展示（如 `configureWithModel:` / `cellWithModel:`），不做业务。
- 列表必须复用（`registerClass:` / `registerNib:` + `dequeue`）；禁止每次 `alloc` 新 Cell。
- 生命周期职责：`viewDidLoad` 一次性创建；依赖 bounds 的布局放 `layoutSubviews` / `viewDidLayoutSubviews` 或约束；`viewWillAppear` / `viewDidAppear` 等勿堆重逻辑。
- **禁止在 `init` 里访问 `self.view`**（触发过早加载）。
- 优先 Auto Layout（`NSLayoutAnchor` / Masonry 等项目既有方式）；与 frame 混用时勿互相打架。
- 宽度自适应；尊重 Safe Area；非必须不用绝对坐标堆叠；背景优先 `backgroundColor` / 图片视图；禁止贴图凑 UI。
- 多状态用 `NS_ENUM`，值加中文注释。

### 导航栏与系统控件（易踩坑）

- 自定义 `titleView` 以 frame / bounds 为准时，勿假设一定尊重 `intrinsicContentSize`；改文字后按项目方式 `sizeToFit` 或重设 `titleView`。
- 勿在导航栏布局同步链路里直接改 `titleView.frame`（易 AL 死循环）；必要时下一圈 runloop。
- 慎用 `UIAppearance` 碰 `UIButton.titleLabel` / `imageView`（iOS 15+ 导航栏易布局风暴）。
- iOS 15+ TableView：贴顶 header 注意 `sectionHeaderTopPadding`；头图 / 轮播可用 `tableHeaderView` 规避 section 顶空白。

## 并发与生命周期

- UIKit 必须在主线程更新；后台完成后主队列回切。
- 后台任务用自建队列（串行 / 并行按需）或项目封装；避免无节制地 `dispatch_get_global_queue` 轰炸。
- 委托、KVO、通知、`NSTimer` / `CADisplayLink`、强引用 Block：在 `dealloc`（或对等时机）移除 / invalidate；防止野指针与重复注册。
- 避免主线程重计算与无节制频繁 layout；大图勿一次性整包 `NSData` 塞内存，走 `UIImage` + 缓存（详见 `shared/performance.md`）。

## 与 Swift 混编

- ObjC 可见 API 正确暴露（`@objc` / 头文件可见性按项目约定）；改 Swift 公共接口后确认 `*-Swift.h` 可用。
- 注意可空性、命名桥接与模块导入；混编边界保持薄、依赖单向清晰。

## 主题、资源与工程

- 颜色 / 字体走 Asset Catalog 或项目主题扩展；禁止散落硬编码主题色（演示页可收敛除外）。
- 优先系统控件与 SF Symbols；小图标默认透明底；资源名英文；Assets 区分 `@1x/@2x/@3x` 或按项目 Single Scale / PDF 约定。
- **新增 `.h/.m/.swift` 必须加入 Target Membership（Compile Sources）**；只落盘不进工程会链接失败。
- 改 `Info.plist` 权限文案时同步中英文（若项目有多语言）；权限、URL Scheme、后台模式等变更须同步工程配置与说明，勿只改代码。
- 密钥 / Token / 密码禁止硬编码；用 Keychain 或环境配置（详见 `shared/security.md`）。

## 质量门禁

- 所有方法都要有中文注释；复杂决策写清原因；审查或精简时不删既有注释。
- 新增较大模块或架构相关改动时，交付前做一次自审并按结果修改；小改动以编译 / 分析通过为准。
- 交付前核对：ARC 与循环引用、主线程 UI、Cocoa 命名、Nullability、可测性、无重复代码、无编译 / 分析警告。
- 无法判断时遵循 Apple Objective-C / UIKit / HIG 官方文档。
