---
name: ios-pod-spm-dual-support
description: 把已有的 iOS CocoaPods 库改造成同时支持 CocoaPods 与 SPM，两种包管理器共用同一份源码目录、模块名保持一致。覆盖 Package.swift 模板与字段取舍、Swift 6 并发陷阱、libarclite/Xcode 15+ 部署目标报错、SPM tag 解析与安全指纹、发版脚本陷阱及端到端验证。触发：给 pod 库增加 SPM 支持、pod install 报 libarclite、SPM 解析带 tag 的 iOS 库失败、维护双包管理器发版。
alwaysApply: false
---

# 让 iOS CocoaPods 库同时支持 CocoaPods 与 SPM

把一个已有的 CocoaPods-only 的 iOS 库改造成同时支持 SPM，两种包管理器**共用同一份源码目录**，模块名保持一致，下游 `import <ModuleName>` 无需改动。

## 适用场景

- 已有 podspec-only 的 iOS 库，要加 SPM 支持
- `pod install` 报 `libarclite` 错误
- SPM 消费方解析带 tag 的 iOS 库失败
- 维护双包管理器发版

## 前置勘察（决定改造难度）

开工前先确认这四项，它们决定了工作量：

```bash
# 1. 库源码是否只依赖系统框架（决定 SPM 是否需要 dependencies）
grep -rn '^import' <LibDir>/Classes/

# 2. 是否有资源文件（决定 SPM 是否需要 resources）
find <LibDir> -name '*.xcassets' -o -name '*.bundle' -o -name '*.strings'
grep -rn 'Bundle(\|UIImage(named:' <LibDir>/Classes/

# 3. 部署目标 / Swift 版本（要与 Package.swift 对齐）
grep -E 'deployment_target|swift_version' *.podspec

# 4. 是否已有悬空符号链接（会阻断 SPM，见「错误 4」）
git ls-files -s | awk '$1=="120000"{print $4}'
```

**零第三方依赖 + 零资源** 是最理想的情况：`Package.swift` 可以极简，SPM 不需要 `dependencies:` 和 `resources:`。

## 实施步骤

### 1. 清理阻断性文件

先删掉会阻断 SPM 的遗留物（详见「错误 4」）：

```bash
# 悬空符号链接（如 CocoaPods 模板遗留的 _Pods.xcodeproj -> Example/Pods/）
git rm <悬空链接>
```

### 2. 新建 `Package.swift`（仓库根）

```swift
// swift-tools-version:5.3
import PackageDescription

let package = Package(
    name: "YourLib",
    platforms: [
        .iOS(.v12)          // 与 podspec 的 deployment_target 对齐
    ],
    products: [
        .library(
            name: "YourLib",
            targets: ["YourLib"]
        )
    ],
    targets: [
        .target(
            name: "YourLib",
            path: "YourLib/Classes",      // 必须显式指定，与 podspec 的 source_files 指向同一目录
            exclude: [".gitkeep"]
        )
    ],
    swiftLanguageVersions: [.v5]          // 防 Swift 6 并发报错，见错误 2
)
```

字段选择的理由：

| 字段 | 要点 |
| --- | --- |
| `swift-tools-version:5.3` | **不要用 6.x**。tools-version < 6.0 时 SwiftPM 默认 Swift 5 语言模式；≥ 6.0 默认 Swift 6 模式，会让 `@objcMembers open class X: UIViewController` 这类代码大面积报 MainActor 隔离错误。5.3 同时支持 `platforms:` / `exclude:` / `swiftLanguageVersions:` |
| `swiftLanguageVersions: [.v5]` | 与 5.3 当前冗余，但是**未来有人升级 tools-version 时的保险丝**。注意 tools-version 6.0+ 已更名 `swiftLanguageModes`，勿混用 |
| `path:` | **必须显式写具体目录，不要用 `"."`**。根路径会让 SwiftPM 扫描整个仓库（`Example/Pods/`、`.build/`、`.git/`），结果不可预测 |
| `platforms:` | 声明 iOS floor。SPM 只在消费方自己的 manifest 里设 deployment target，**没有 CocoaPods 那种 `post_install` 兜底手段**，消费方低于此版本会在他们那边报错 |

**manifest 首行必须是 `// swift-tools-version:X.Y`**，前面不能有空行或横幅注释，否则解析失败（最常见的首次尝试错误）。

### 3. 更新 `.gitignore`

```
.swiftpm/
Package.resolved
```

无依赖的根包不产生 `Package.resolved`，但 Xcode 把仓库根当包打开时可能生成 `.swiftpm/`。

### 4. 解除 `libarclite` 阻塞（Xcode 15+）

Xcode 15 起工具链物理移除了 `libarclite_iphonesimulator.a`，**任何部署目标 < 12.0 的 target 在链接阶段都会失败**。官方错误如下：

```
clang: error: SDK does not contain 'libarclite' at the path
'/Applications/Xcode.app/.../usr/lib/arc/libarclite_iphonesimulator.a';
try increasing the minimum deployment target
```

要升到 iOS 12.0（而非 11.0）—— 12.0 是 `libarclite` 的分水岭。三处都要改：

```
podspec:      s.ios.deployment_target = '12.0'
Package.swift: .iOS(.v12)
Podfile:      platform :ios, '12.0'
```

**只改 Podfile 的 platform 是不够的**：`pod install` 后第三方 pod 的 target 仍是各自 podspec 声明值（如 SnapKit 8.0、SwiftExpand 9.0），照样链接失败。需要 `post_install` 兜底：

```ruby
post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
    end
  end
end
```

验证所有 target 已统一：

```bash
grep -o 'IPHONEOS_DEPLOYMENT_TARGET = [0-9.]*' Example/Pods/Pods.xcodeproj/project.pbxproj | sort | uniq -c
```

### 5. 更新 README

补 SPM 安装段，并**显著标注 iOS 版本下限**：

```swift
dependencies: [
    .package(url: "https://github.com/<owner>/<repo>.git", from: "1.5.0")
]
```

### 6. 发版（tag 是 SPM 的解析目标）

**SPM 按 git tag 解析版本，因此 `Package.swift` 必须存在于 tag 指向的那棵树里**。加在分支上但不发新版，SPM 消费方依然拿不到。

发版前在流程里加一道 manifest 校验（放在**打 tag 之前**，因为 tag 不可变）：

```bash
if [ -f "Package.swift" ]; then
    swift package dump-package > /dev/null || exit 1
fi
```

## 错误与解决办法

### 错误 1：`pod install` 报 `libarclite` 不存在

见「实施步骤 4」。根因是 Xcode 15+ 移除该静态库，**必须把部署目标抬到 12.0**，且要覆盖所有 Pods target（第三方 pod 的声明值也要用 `post_install` 抬高）。

降级 CocoaPods **无法解决** —— 库是被 Xcode 工具链物理删除的，不是 Podfile 解析问题。

### 错误 2：Swift 6 模式下大面积 MainActor 隔离报错

`@objcMembers open class X: UIViewController` 继承的 UIKit 类型在 iOS 18 SDK 上带 `@MainActor` 标注，而类体没有 actor 隔离。tools-version ≥ 6.0 时 SwiftPM 默认 Swift 6 语言模式，会产生大量并发错误。

**已实测**：同一个库在 tools-version 5.3 下编译通过，切到 6.0 后报 4 个错误，典型形态：

```
error: main actor-isolated static property 'notiNameDismissKey'
       can not be referenced from a nonisolated context

error: call to main actor-isolated instance method 'updatePresentedView'
       in a synchronous nonisolated context
```

注意源文件本身**一行没改**，仅语言模式变化就会产生这些错误。

**解决**：tools-version 锁 `5.3`，并显式写 `swiftLanguageVersions: [.v5]`。

### 错误 3：SPM 解析报 `Revision ... does not match previously recorded value`

```
error: 'libname': Revision <new-sha> for libname remoteSourceControl <url>
version 1.5.0 does not match previously recorded value <old-sha>
```

**这是 SPM 的安全指纹机制**：它记录了「版本号 → 内容指纹」的映射。**一旦某个 tag 被移动过，任何在移动前解析过该版本的机器都会硬失败。**

指纹文件位置：

```
~/Library/org.swift.swiftpm/security/fingerprints/<libname>-<hash>.json
```

清缓存（`~/Library/Caches/org.swift.swiftpm/`、`.build/`、`Package.resolved`）**都无法绕过** —— 必须删掉该 fingerprint 文件。

**根本对策：已发布的 tag 永远不要移动。** 需要修正时发新版本号。仅在「从未发布到 trunk」的前提下才可移动 tag。

### 错误 4：仓库根有悬空符号链接导致 SPM / xcodebuild 直接报错

CocoaPods 模板会在仓库根留下 `_Pods.xcodeproj` 符号链接，指向已 gitignore 的 `Example/Pods/Pods.xcodeproj`。任何全新 clone 里它都是**悬空**的：

```
xcodebuild: error: '_Pods.xcodeproj' does not exist.
```

这会**完全阻断** SPM 构建与 `xcodebuild`。确认无人引用后删除：

```bash
git ls-files _Pods.xcodeproj        # 确认被跟踪
grep -rn '_Pods' --include='*.xcworkspacedata' --include='*.pbxproj' .   # 确认无引用
git rm _Pods.xcodeproj
```

### 错误 5：`pod trunk push` 报 `Net::OpenTimeout`

```
[!] There was an error pushing a new version to trunk: Net::OpenTimeout
```

**这不代表发布失败。** 常见情况是客户端等待响应超时、而服务端已完成上传。

**重试前务必先确认**，否则可能重复发布：

```bash
pod trunk info YourLib | grep '<version> ('
```

对照时间戳判断是否为本次上传。确认未发布再重试。

### 错误 6：发版脚本把无关文件卷进提交，tag 消息串版本

`git add .` 会把工作区所有改动一并提交，包括构建脚本刷新的 `Info.plist` 的 `CFBundleVersion` 时间戳。若同时用 `git log -1 --pretty=format:'%s'` 生成提交信息和 tag 消息，会造成：

- 出现两条同名但内容不同的提交
- 版本 N 的 tag 挂着版本 N-1 的说明

**解决**：tag 消息明确带上版本号，不要复用上一条提交主题：

```bash
git tag -a "${version}" -m "Release ${version}"
```

并在发版前 `git status` 确认工作区。

### 错误 7：四段式版本号对 SPM 消费者完全不可见

仓库里存在 `1.0.5.1`、`1.4.2.1` 这类四段式 tag 时：

| 场景 | 实测结果 |
| --- | --- |
| 消费者用 `from: "1.0.0"` | 解析到 `1.0.4`，四段式 tag 被**静默忽略**，不报错 |
| 消费者用 `exact: "1.0.5.1"` | manifest 报错 `Invalid semantic version string '1.0.5.1'` |

**不会破坏解析，但四段式版本永远无法被选中。** 如果某个版本只用四段式 tag 发布，SPM 消费方就完全拿不到它 —— 而且没有任何报错提示。

**解决**：发版一律用三段式 `X.Y.Z`。已在仓库中的四段式 tag 可以保留（不影响解析），但不要再新增。

### 错误 8：`swift build` 无法编译 UIKit 代码

```
error: no such module 'UIKit'
```

`swift build` 默认 macOS 三元组，iOS 库无法编译。这是**预期行为**，不是配置错误。

- 只想校验 manifest：`swift package dump-package`
- 真正编译：用 iOS destination（见下）

## 验证

### SPM 侧

```bash
# manifest 解析（不编译，必定可用）
swift package dump-package
swift package describe          # 核对 target 源文件数与模块名

# 按 podspec 的 source_files 目录用 iOS SDK 编译
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
xcrun -sdk iphonesimulator swiftc -swift-version 5 \
  -target x86_64-apple-ios12.0-simulator -sdk "$SDK" \
  -emit-module -module-name YourLib \
  -emit-module-path /tmp/lib/YourLib.swiftmodule \
  -emit-library -static -o /tmp/lib/libYourLib.a \
  -parse-as-library YourLib/Classes/*.swift

# 端到端：消费方编译+链接
xcrun -sdk iphonesimulator swiftc -swift-version 5 \
  -target x86_64-apple-ios12.0-simulator -sdk "$SDK" \
  -I /tmp/lib -L /tmp/lib -lYourLib main.swift -o /tmp/app
```

`main.swift` 要覆盖主要公开 API，确认模块接口可用。

**按版本解析（最关键的一项）** —— 必须针对**已推送的 tag**验证：

```bash
# 消费方 Package.swift 用 .package(url: "...", from: "<tag>")
swift package resolve
cat Package.resolved        # 应解析到目标版本
```

### CocoaPods 侧（回归）

```bash
pod lib lint YourLib.podspec --allow-warnings     # 本地源码
pod spec lint YourLib.podspec --allow-warnings    # 按 tag 拉真实源码
```

真实消费者验证（可选但最可靠）：搭一个最小 `.xcodeproj` + Podfile，`pod install` 后 `xcodebuild` 构建。

> `pod install` 若找不到新版本，需要 `pod install --repo-update` —— 本地 spec 仓库可能未同步。

### 环境限制

`xcodebuild -scheme <包名>` 直接打开包构建在部分 Xcode 版本上会崩：

```
INTERNAL ERROR: Unable to load workspace
Uncaught Exception: -[Swift.__SwiftDeferredNSArray intersectsSet:]: unrecognized selector
```

**这是 Xcode 环境 bug，与库本身无关** —— 用一个三行极简 iOS 包对照即可确认。绕过方式就是上面的 `swiftc` + iOS SDK 方案。

## 检查清单

- [ ] 库源码只 `import UIKit` 等系统框架（否则 Package.swift 需补 `dependencies:`）
- [ ] 无资源文件（否则需补 `resources:`）
- [ ] `Package.swift` 首行是 tools-version，`path:` 指向与 podspec `source_files` 相同目录
- [ ] `platforms:` 与 podspec `deployment_target` 一致，且 ≥ 12.0
- [ ] `swiftLanguageVersions: [.v5]` 已显式声明
- [ ] 仓库根无悬空符号链接
- [ ] `.gitignore` 含 `.swiftpm/` 与 `Package.resolved`
- [ ] 模块名与 CocoaPods 一致（`import X` 两边通用）
- [ ] 新 tag 的树里**包含** `Package.swift`
- [ ] 已发布 tag 未被移动
- [ ] 版本号为三段式（四段式对 SPM 消费者不可见，见错误 7）
- [ ] SPM 按版本解析 + 消费方链接通过
- [ ] `pod spec lint` 通过
- [ ] README 标注 iOS 版本下限
