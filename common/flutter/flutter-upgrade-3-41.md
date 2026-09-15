---
name: flutter-upgrade-3-41
description: >-
  把 Flutter 工程从 3.27 升到 3.41.9（Dart 3.11）。Use when 升级 Flutter SDK、
  3.27 升 3.41、Flutter 3.41、Dart 3.11、UIScene、FlutterImplicitEngineDelegate、
  Gradle Plugin DSL、enable-swift-package-manager、DKImagePickerController
  branch 4.3.9、CocoaPods 1.16.2、IconData final、FaIcon、analysis_options.yaml
  formatter.errors。覆盖完整步骤与本次升级踩坑。
alwaysApply: false
---

# Flutter 3.27 → 3.41.9 工程升级

把**已有工程配置**对齐 Flutter 3.41.9，直到 iOS 模拟器能跑起来。默认假设本机 SDK 已用 FVM 装好；用户没说「去装 SDK」就不要重装。

来源：`flutter_templet_project` 实升（2026-09）。其它工程按同一清单走，遇到表里的报错用对应解法。

## 铁律

1. **先读官方文档再改代码**（见下表）。不要凭 3.27 记忆改 Gradle / AppDelegate。
2. **只改工程配置与编译所需代码**。禁止 `dart fix --apply` 全仓库。已有文件只用 StrReplace，禁止 Write 整文件覆盖。
3. **分析器必须用 3.41.9**。`dart.flutterSdkPath` 用绝对路径 `/Users/shang/fvm/versions/3.41.9`。Cursor 若仍挂 3.44.x analysis_server，先杀进程再 Restart Analysis Server。
4. **本工程继续 CocoaPods**。3.41 默认开 SPM；`file_picker` 10.x 的 SPM 会把 `DKImagePickerController` tag `4.3.9` 写成 branch，Xcode 解析失败。不要为修 SPM 去升 `file_picker` 12/13（`FilePickerResult` API 不兼容）。
5. **跑到已 Booted 的模拟器**。不要新开一台。不要自动 git commit / push。

## 版本对照

| 项 | 3.27 侧 | 3.41.9 目标 |
|---|---|---|
| Flutter | 3.27.4 | 3.41.9 |
| Dart | ~3.6 | **3.11.5** |
| `environment.sdk` | `>=3.6.0 <4.0.0` | `>=3.11.0 <4.0.0` |
| `environment.flutter` | 无或 3.27 | `>=3.41.0` |
| iOS | 旧 lifecycle | **UIScene** + `FlutterImplicitEngineDelegate` |
| Android Gradle | `apply from: flutter.gradle` | **Plugin DSL**（`apply from` 已移除） |
| iOS 依赖 | CocoaPods | 3.41 默认 SPM；本工程 **关掉 SPM** |
| CocoaPods | 1.13.x 能编 | **≥ 1.16.2**（本机升到 1.17.0） |
| Java / Kotlin | 视工程 | Java 17，Kotlin 1.9.24，AGP 8.5.2 |

FVM 路径：`/Users/shang/fvm/versions/3.41.9`。命令一律 `fvm flutter ...`，不要用系统 `flutter`。

## 官方文档（动手前打开）

- 升级命令：https://docs.flutter.dev/install/upgrade
- Breaking changes 总表：https://docs.flutter.dev/release/breaking-changes
- UIScene：https://docs.flutter.dev/release/breaking-changes/uiscenedelegate-adoption
- SPM 开关：https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers
- Gradle Plugin DSL：https://docs.flutter.dev/release/breaking-changes/flutter-gradle-plugin-apply
- Android v1 embedding 已删：https://docs.flutter.dev/release/breaking-changes/android-v1-embedding-java-apis-removed
- Radio API（若工程用 Radio）：https://docs.flutter.dev/release/breaking-changes/radio-api-redesign

## 升级清单

复制并勾选。用户说「SDK 已装好」时跳过步骤 0 的 install，仍要核对 `fvm flutter --version`。

```
- [ ] 0. 核对 SDK / FVM / dart.flutterSdkPath
- [ ] 1. 锁项目版本（.fvmrc、pubspec environment）
- [ ] 2. pubspec 依赖与 SPM 开关
- [ ] 3. Android 迁到 Plugin DSL
- [ ] 4. iOS UIScene + MethodChannel 改注册时机
- [ ] 5. 关掉 SPM 并清掉 Xcode package 引用
- [ ] 6. Dart 破坏性 API（ThemeData / FaIcon / const builder）
- [ ] 7. analysis_options.yaml 合法化
- [ ] 8. fvm flutter pub get；重启分析器；只修 error
- [ ] 9. CocoaPods ≥ 1.16.2；iOS 模拟器跑通
```

### 0. 核对 SDK

```bash
ls /Users/shang/fvm/versions/3.41.9
fvm flutter --version   # Flutter 3.41.9 / Dart 3.11.5
```

`.vscode/settings.json`：

```json
"dart.flutterSdkPath": "/Users/shang/fvm/versions/3.41.9"
```

不要用相对路径 `.fvm/flutter_sdk`。不要指到另一套已装 SDK（例如 3.44.1），否则 `package_config` 会混版本，IDE 报一堆假 error。

`fix-flutter-sdk-path` 习惯写 `/Users/shang/fvm/default`。仅当 `default` **已经**指向 3.41.9 时才能用；升级进行中一律钉死 `versions/3.41.9`。

### 1. 锁项目版本

- `.fvmrc`：`{ "flutter": "3.41.9" }`
- `.fvm/fvm_config.json`：`{ "flutterSdkVersion": "3.41.9" }`
- `pubspec.yaml`：`version` 可改为 `3.41.0+N`；`environment` 如上表。
- 删掉只为 3.27 打的 `dependency_overrides`（如过期的 `screen_brightness_ios` / `url_launcher_ios` / `image_cropper` pin）。与 3.41 无关的 override（`html`、`webview_flutter_android` 等）留下。

### 2. pubspec 依赖

必面对齐：

| 包 | 原因 |
|---|---|
| `intl: ^0.20.2` | 3.41 的 `flutter_localizations` 需要 intl 0.20 |
| `flutter_form_builder: ^10.0.0` | 9.5.0 卡旧 intl，`pub get` 失败 |
| `font_awesome_flutter: ^11.0.0` | 10.x 继承 `IconData`；3.41 里 `IconData` 是 **final** |
| 不要升 `file_picker` 到 12/13 | 能修 SPM，但 `FilePickerResult` / `pickFiles` 不兼容现有调用 |

在 `flutter:` 下关 SPM：

```yaml
flutter:
  uses-material-design: true
  # file_picker 10.x SPM 把 DKImagePickerController tag 4.3.9 写成 branch
  config:
    enable-swift-package-manager: false
```

然后 `fvm flutter pub get`。

### 3. Android → Plugin DSL

3.41 的 Flutter Gradle 插件**不再提供** `flutter.gradle` / `app_plugin_loader.gradle`。继续 `apply from:` 会直接编不过。

`android/settings.gradle` 改为 `pluginManagement` + `plugins`，保留原有 `flutter.sdk` 从 `local.properties` 读取：

```gradle
pluginManagement {
    def flutterSdkPath = {
        def properties = new Properties()
        file("local.properties").withInputStream { properties.load(it) }
        def flutterSdkPath = properties.getProperty("flutter.sdk")
        assert flutterSdkPath != null, "flutter.sdk not set in local.properties"
        return flutterSdkPath
    }()
    includeBuild("$flutterSdkPath/packages/flutter_tools/gradle")
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
plugins {
    id "dev.flutter.flutter-plugin-loader" version "1.0.0"
    id "com.android.application" version "8.5.2" apply false
    id "org.jetbrains.kotlin.android" version "1.9.24" apply false
}
include ":app"
```

删掉旧的 `apply from: "$flutterSdkPath/packages/flutter_tools/gradle/app_plugin_loader.gradle"`。

`android/app/build.gradle` 顶部改为：

```gradle
plugins {
    id "com.android.application"
    id "kotlin-android"
    id "dev.flutter.flutter-gradle-plugin"
}
```

删掉 `apply plugin: 'com.android.application'`、`apply from: flutter.gradle`。`compileSdk` / `minSdk` / `ndkVersion` 用 `flutter.*`。Java/Kotlin **17**。

`android/build.gradle`：AGP/Kotlin classpath 已迁到 `settings.gradle` 的 `plugins`，根文件不要再留一份 `buildscript` 冲突。

Kotlin `MainActivity` 已是 v2 embedding 则不必改。

### 4. iOS UIScene

3.41 默认 UIScene。还在 `didFinishLaunching` 里拿 `window?.rootViewController` 注册插件 / MethodChannel，引擎可能还没就绪。

**AppDelegate** 实现 `FlutterImplicitEngineDelegate`，插件和自建 Channel 改到 `didInitializeImplicitFlutterEngine`：

```swift
@main
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
    override func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        // 通知等非 Flutter 引擎初始化可留在这里
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }

    func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
        GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)
        MethodChannelRegistrar.register(with: engineBridge.applicationRegistrar.messenger())
    }
}
```

`didFinishLaunching` **不要**再 `GeneratedPluginRegistrant.register(with: self)`。

需要 `UIWindow` 的 Channel（如音量）：`window` 改为可选；未传入时从 `connectedScenes` 取 key window。

**Info.plist** 增加 `UIApplicationSceneManifest`，`UISceneDelegateClassName` = `FlutterSceneDelegate`，`UISceneStoryboardFile` = `Main`，`UIApplicationSupportsMultipleScenes` = false。

其它 iOS：

- `Podfile`：`platform :ios, '15.5'`（本工程 MLKit 需要；至少满足 3.41 最低版本）。
- 删掉模拟器 `EXCLUDED_ARCHS[sdk=iphonesimulator*] = arm64`（Apple Silicon 模拟器要 arm64）。
- `ios/Flutter/AppFrameworkInfo.plist` **删掉** `MinimumOSVersion`（3.41 不再从这里读，留着会警告/冲突）。

### 5. 关掉 SPM 并清 Xcode 引用

仅改 `pubspec` 不够：`xcodebuild` 仍会解析 `project.pbxproj` 里的 `FlutterGeneratedPluginSwiftPackage`。

在 `ios/Runner.xcodeproj/project.pbxproj` 搜并删掉：

- `FlutterGeneratedPluginSwiftPackage`
- `packageReferences` / `packageProductDependencies` / `XCRemoteSwiftPackageReference` / `XCSwiftPackageProductDependency` 中与 Flutter 生成 SPM 相关的条目

然后 `fvm flutter pub get`。`ios/Flutter/ephemeral/Packages/` 可能还会生成文件，只要 pbxproj 不再引用即可。

### 6. Dart 破坏性 API

按编译 error 局部改，不要全仓库格式化。

**ThemeData 子主题类型**（`ThemeData(...)` 参数已是 `*ThemeData`）：

```
TabBarTheme        → TabBarThemeData
AppBarTheme        → AppBarThemeData
DialogTheme        → DialogThemeData
BottomAppBarTheme  → BottomAppBarThemeData
InputDecorationTheme → InputDecorationThemeData
```

字段类型 `TabBarTheme?` 同样改。grep：`appBarTheme:` / `tabBarTheme:` / `dialogTheme:` / `bottomAppBarTheme:` / `inputDecorationTheme:`。

**font_awesome_flutter 11**：`IconData` 不能再被继承。

```
The class 'IconData' can't be extended, implemented, or mixed in
```

依赖改 `^11.0.0` 后，把 `Icon(FontAwesomeIcons.xxx)` 换成 `FaIcon(FontAwesomeIcons.xxx)`。

**Cupertino 转场**：

```
const CupertinoPageTransitionsBuilder()  // 不再是 const 构造
```

去掉 `const`。

其它官方项（本仓库未必踩到，但要搜）：`Radio` 新 API；Android Java v1 embedding 调用。

### 7. analysis_options.yaml

Dart 3.11 的 YAML schema 更严。按下面改，改完用 IDE 诊断确认 **0 warning**：

- **禁止** `formatter.errors`。严重级别只写在 `analyzer.errors`。
- `formatter` 只留 `page_width`、`trailing_commas`（3.7+ 合法键）。
- `linter.rules` 必须是 **字符串列表**。不要写成 `always_use_package_imports: true` 这种 map（和 list 混用会废掉整段）。
- `analyzer.errors` **键不能重复**（重复会 `Duplicate mapping key`）。
- 删除已移除/弃用规则：`unsafe_html`、`always_require_non_null_named_parameters`、`prefer_equal_for_default_values`、`avoid_null_checks_in_equality_operators`；视 SDK 还可能有 `iterable_contains_unrelated_type`、`list_remove_unrelated_type`。
- 拼写：`unnecessary_brace_in_string_interns` → `unnecessary_brace_in_string_interps`。

### 8. 分析器对齐（只修 error）

```bash
fvm flutter pub get
fvm flutter analyze
```

若 IDE 仍报大量 error 而 CLI 没有：

1. 确认 `package_config.json` 是 3.41.9 生成的，不是 3.44.x。
2. 杀掉旧 `analysis_server`（3.44.1）进程。
3. 命令面板：**Dart: Restart Analysis Server**。

只修 **error**。`deprecated_member_use` 本工程在 `analyzer.errors` 里已 ignore，不要借升级去清全仓库 deprecated。

### 9. 模拟器跑通

```bash
pod --version   # >= 1.16.2
xcrun simctl list devices booted
fvm flutter run -d <已启动的模拟器 UDID>
```

优先已 Booted 设备。iOS 用 `.xcworkspace`，不要直接编 `.xcodeproj`。

PrivacyInfo / 插件 privacy manifest 多为 **warning**，不要当成 BUILD FAILED 去改无关插件。

## 问题与解法（本次全部踩过）

### A. `pub get`：intl vs flutter_form_builder

**现象**：`intl ^0.20.2` 与 `flutter_form_builder 9.5.0` 冲突。

**解法**：`flutter_form_builder: ^10.0.0`。不要把 intl 降回 0.19。

### B. Xcode：`could not find a branch named '4.3.9'`（DKImagePickerController）

**现象**：Flutter 3.41 默认 SPM。`file_picker` 10.x 的 `Package.swift` 写了 `branch: "4.3.9"`，该值其实是 **git tag**。

**解法**：

1. `pubspec.yaml` → `flutter.config.enable-swift-package-manager: false`
2. 从 `project.pbxproj` 删除 `FlutterGeneratedPluginSwiftPackage`
3. **不要**升到 `file_picker` 12/13 来「根治」（API 破坏）

CocoaPods 解析同一个 4.3.9 tag 是正常的。

### C. `CocoaPods recommended version 1.16.2 or greater not installed`

**现象**：锁文件还是 `COCOAPODS: 1.13.0`。

**解法**：按**现有安装方式**升级，不要 brew/gem 混装。本机是 gem：`gem install cocoapods` → 1.17.0。再 `pod --version` 确认。不必为这条去改 Dart 代码。

### D. `IconData` can't be extended / mixed in

**现象**：`font_awesome_flutter` 10.9.x 在 3.41 编不过。

**解法**：`font_awesome_flutter: ^11.0.0`，UI 改用 `FaIcon(...)`。

### E. `CupertinoPageTransitionsBuilder` isn't a constant expression

**解法**：去掉 `const`。

### F. Gradle：找不到 `flutter.gradle` / `app_plugin_loader.gradle`

**解法**：步骤 3 的 Plugin DSL。3.41 **没有**旧 apply 脚本可回退。

### G. 启动后插件 / MethodChannel 无效，或 `window` 为 nil

**解法**：步骤 4。注册必须在 `didInitializeImplicitFlutterEngine`。从 `UIWindowScene` 取 key window，不要假设 `AppDelegate.window` 仍可用。

### H. Apple Silicon 模拟器架构

**现象**：排除了 `arm64` iphonesimulator。

**解法**：去掉 `EXCLUDED_ARCHS` 这条。不要为「老 Intel 模拟器」在 3.41 工程里加回来。

### I. 分析器 error 海 / 混用 3.44.1

**现象**：Cursor 用另一套 Flutter（3.44.1）分析 3.41 工程；`package_config` 与 SDK 不一致。

**解法**：`dart.flutterSdkPath` 钉死 3.41.9 绝对路径 → `fvm flutter pub get` 重生配置 → 杀 3.44 analysis_server → Restart Analysis Server。以 `fvm flutter analyze` 为准。

### J. `analysis_options.yaml` 警告

| 诊断 | 解法 |
|---|---|
| `formatter.errors` unsupported | 整块 `errors` 移到 `analyzer.errors` |
| `unsafe_html` / `always_require_non_null_named_parameters` / `prefer_equal_for_default_values` isn't a recognized lint | 删除 |
| `avoid_null_checks_in_equality_operators` deprecated | 删除 |
| `unnecessary_brace_in_string_interns` | 改为 `..._interps` |
| `Duplicate mapping key` | `analyzer.errors` 去重 |
| rules 写成 map | 改回 `- rule_name` 列表 |

### K. Theme 参数类型不匹配

**现象**：`TabBarTheme` / `AppBarTheme` / `DialogTheme` 等不能赋给 `ThemeData` 对应字段。

**解法**：改用 `*ThemeData` 类型（步骤 6）。自定义 Widget 上的 `TabBarTheme?` 字段一并改。

## 禁止

- 全仓库 `dart fix --apply` / 全文件重排
- 为关 SPM 而升级 `file_picker` 12+
- 把 `dart.flutterSdkPath` 指到非 3.41.9 的 SDK
- 自动 commit / push
- 把 PrivacyInfo warning 当 error 去改第三方插件
- 用 Write 覆盖用户正在改的已有文件
