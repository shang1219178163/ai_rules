---
name: flutter-ios-debug
description: >-
  在 iOS 模拟器上构建、安装、启动 Flutter 应用并通过设备日志复现/定位运行期问题（视频切换、纹理、
  播放器生命周期等）。触发：需要在 iOS 模拟器上跑 Flutter app、复现某个运行期 bug、看设备日志、
  确认某次修改在真实运行时有效。适合需要"改代码→跑起来→看日志→截屏确认"闭环的调试。
---

# Flutter iOS 模拟器调试

将 Flutter 工程跑在 iOS 模拟器上，用命令行完成"构建 → 安装 → 启动 → 抓日志 → 截屏确认"的调试闭环，避免依赖需要辅助功能权限的 GUI 点击工具。

所有命令都要写成可在当前工程目录直接执行的、可复用的形式，设备 UDID / bundle id 用自动探测或占位符，**不要硬编码具体设备**。

## 先决条件

- 已安装 Xcode + CocoaPods，`flutter` 在 PATH。
- 模拟器已启动：`xcrun simctl list devices booted` 能看到 `Booted` 状态（无则 `xcrun simctl boot <UDID>`）。

## 步骤

### 1. 探测设备与参数

```bash
# 已启动的模拟器
xcrun simctl list devices booted | grep Booted

# 自动取第一个 Booted 的 UDID
UDID=$(xcrun simctl list devices booted | grep -oE '[0-9A-F-]{36}' | head -1)

# bundle id（从 pbxproj 探测，识别 com.xxx.yyy）
BUNDLE_ID=$(grep -rhoE 'PRODUCT_BUNDLE_IDENTIFIER = com\.[a-z.]+' ios/Runner.xcodeproj/project.pbxproj | head -1 | grep -oE 'com\.[a-z.]+')
```

### 2. 构建（后台运行，避免阻塞）

在工程根目录（含 `pubspec.yaml` 的那一层）执行。多个 `flutter` 子工程时注意 cwd——每个包在各自目录构建。

```bash
flutter build ios --simulator --debug 2>&1 | tail -5
```

构建成功标志：结尾 `✓ Built build/ios/iphonesimulator/Runner.app`。
若慢或需继续干别的，用 `run_in_background` 放后台。

### 3. 安装 + 启动

```bash
xcrun simctl install "$UDID" build/ios/iphonesimulator/Runner.app
xcrun simctl launch "$UDID" "$BUNDLE_ID"
```

启动会打印进程 PID，如 `com.example.chewie: 12345`。

### 4. 抓设备日志

`log show` 按进程过滤，只留 Flutter `debugPrint` 输出和错误：

```bash
xcrun simctl spawn "$UDID" log show --last 60s \
  --predicate 'process == "Runner"' --style compact \
  2>&1 | grep -iE "flutter: |error|Exception|Null check|Unhandled" | head -40
```

- `debugPrint(...)` 在日志里以 `(Flutter) flutter: ...` 形式出现。
- 用 `grep` 过滤关键字（如 `switchToVideo|acquire|dispose|activeCount|Null check`）聚焦兴趣点。
- **先启动 app 再 `log show`**，否则拿不到本次运行的日志。日志是追加式的，`--last Ns` 取最近窗口。

### 5. 截屏确认画面

```bash
xcrun simctl io "$UDID" screenshot /tmp/current.png
```

用 Read 工具打开截屏，确认画面确实是预期状态（如已切到目标视频、非黑屏、非停滞旧画面）。**截屏是验证"画面真的变了"的唯一可靠手段**——日志只证明日志，不证明渲染。

## 关键坑（今天验证过的）

- **CocoaPods / Pods 依赖**：flutter 托管的 iOS 工程用 `.xcworkspace` 而非裸 `.xcodeproj`。用 `flutter build ios` 走默认 workspace，别手动编 `.xcodeproj`。
- **模拟器 app 不在前台时截屏看到的是主屏幕**：`simctl launch` 启动后 app 通常在前台，但如果退回桌面，`screenshot` 会拍到 SpringBoard。确认 `launch` 返回的 PID 存在且未崩溃。
- **AppleScript / `osascript ... click at` 点到模拟器不可靠**：返回的是 System Events 的 UI 元素 ID 而非真实落点，且需要辅助功能权限。**不要用它来点击模拟器内部**。要驱动交互，改用临时在 `initState` 注入自动触发的测试代码（如 `Future.delayed` 后调用目标逻辑 + `debugPrint` 标记），跑完再删。注入代码要含唯一关键词（如 `TEMP REPRO` / `AUTO-VERIFY`），最后用 `grep -rn "关键词" lib/` 确认清理干净。
- **无效视频源会污染复现结论**：`PlatformException(VideoError, ..., -12660)` 多因视频源在该网络环境返回 403/不可达（如 `commondatastorage.googleapis.com`）。先用 `curl -s -o /dev/null -w "%{http_code}" <url>` 探测源是否可达（`200` 可达、`000`/`403` 不可达），再用**可达源**做切换测试，避免把"源挂了"误判成"代码 bug"。
- **CoreAudio / CFNetwork 噪音日志**：`SessionAPIUtilities -50`、`Task finished with error [-999]`、`coremedia` 的 KVO 日志多为系统噪音，**不是应用错误**。判断时看 `(Flutter) flutter:` 前缀和 `Unhandled/Null check/Exception` 关键字。
- **模拟器纹理时序与真机可能不同**：iOS 视频纹理 detach 是异步的。切源时若不等表面彻底 detach 就 dispose 旧播放器，新播放器可能无法绑定纹理，画面停留在旧视频。复现"仍播旧视频"要专门测这类竞态（快速连切、全屏切源），并在真机上二次确认。

## 清理临时注入

调试用的临时注入代码结束时务必删除：

```bash
grep -rn "TEMP REPRO\|AUTO-VERIFY\|REPRO" lib/
# 无输出 = 已清理干净
```
