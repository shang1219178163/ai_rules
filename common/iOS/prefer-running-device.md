---
name: prefer-running-device
description: iOS 应用构建运行时，优先选择当前运行中的真机或模拟器，而不是固定指定设备或先启动新设备。触发：构建/运行 iOS App、xcodebuild 指定 destination、用户要求"优先使用当前运行中的真机或者模拟器"。
alwaysApply: false
---

# iOS 优先使用当前运行中的真机 / 模拟器

构建并运行 iOS App 时，优先复用**当前正在运行的设备**（真机或模拟器），避免固定写死某个设备、也避免重复启动新模拟器实例。

## 步骤

1. 列出当前设备状态：
   - 真机：`xcrun devicectl list devices`
   - 模拟器：`xcrun simctl list devices booted`（只看 `Booted` 状态的）
2. 选择优先级：
   - 优先已 `Booted` 的模拟器；其次已连接且 `available` 的真机。
   - 真机显示 `unavailable`（未解锁 / 未信任电脑）时，改用运行中的模拟器。
3. 用选中的设备作为 `xcodebuild` destination：
   - 模拟器：`-destination 'id=<模拟器UDID>'`
   - 真机：`-destination 'id=<真机UDID>'`
4. 构建成功后再安装运行：
   - `xcrun simctl install booted <App.app>` + `xcrun simctl launch booted <BundleID>`

## 注意

- **优先用 CocoaPods workspace**：`xcodebuild -workspace <项目>.xcworkspace`。直接编 `.xcodeproj` 会缺 Pods 的 header 搜索路径，报 `#import <xxx.h> file not found`。
- 构建命令放后台（`run_in_background`），用 `xcodebuild ... | grep -E "BUILD|error:"` 过滤输出。
- 真机全部 `unavailable` 时，明确告知用户改用模拟器，而不是卡在真机。
- 若必须切换 tab / 输入文字才能到达目标页，优先用 `simctl`（如 `defaults write` 跳过引导页），避免依赖需要辅助功能权限的 GUI 点击工具。
