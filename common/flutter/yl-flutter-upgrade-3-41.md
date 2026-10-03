---
name: yl-flutter-upgrade-3-41
description: >-
  医链 Flutter 工程升到 3.41.9 的差异与踩坑。Use when 升级 yl_health_app、医链、
  git.yljt.cn、相对路径包、没有则走 pub、yl_design、yl_foundation、yl_media、recognition_qrcode、
  GoogleMLKit 非模块头、Unexpected duplicate tasks、pod 走代理、华为 agconnect、
  sticky_az_list、carousel_slider 5、win32 UnmodifiableUint8ListView。
  通用步骤用 flutter-upgrade-3-41，本文覆盖医链差异。
alwaysApply: false
---

# 医链 Flutter 升到 3.41.9

先按 skill `flutter-upgrade-3-41` 做通用清单（FVM、Plugin DSL、UIScene、关 SPM、只修 error）。本文只写医链和那份清单不一样，或那份没踩到的问题。来源：`yl_health_app` 从 FVM 3.10.6 / `local.properties` 3.19.6 实升（2026-10）。

命令一律 `fvm flutter`。SDK：`/Users/shang/fvm/versions/3.41.9`。不要改营销版本（`versionName` / `versionCode` / `pubspec` version）。不要 commit / push。不要 `dart fix --apply`。已有文件只用 StrReplace。

## 覆盖通用 skill 的默认值

| 项 | 通用 skill | 医链 |
|---|---|---|
| iOS 最低版本 | 15.5（模板为 MLKit） | **13.0**。Podfile、pbxproj 全部 `IPHONEOS_DEPLOYMENT_TARGET`、post_install 都是 13.0 |
| 私有依赖 | 无 | **不要 clone** `git.yljt.cn`。本机有源码用相对路径，没有则走 pub 包 |
| `file_picker` | 不升 12/13 | 同样，继续 CocoaPods |
| SPM | 关掉 | 同样 |

## 网络

```bash
export PUB_HOSTED_URL=https://pub.flutter-io.cn
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
export http_proxy=http://127.0.0.1:7892 https_proxy=http://127.0.0.1:7892
export HTTP_PROXY=http://127.0.0.1:7892 HTTPS_PROXY=http://127.0.0.1:7892
export no_proxy=localhost,127.0.0.1,git.yljt.cn
export NO_PROXY=localhost,127.0.0.1,git.yljt.cn
```

- 公网 pod / pub 下载走 `127.0.0.1:7892`。`pod install` 不带代理会卡在 Google / GitHub。
- `git.yljt.cn` **必须**在 `no_proxy` 里。该主机没有公网 DNS；走代理时 HTTPS 是 `SSL_ERROR_SYSCALL`，HTTP 是 502。不要改全局 git config。
- `LANG` 不设，CocoaPods 会因编码直接失败。

## 相对路径包

凡是 `git.yljt.cn` 上的库都不要 clone。本机源码只有这两处：

- `/Users/shang/yl/packages`
- `/Users/shang/yl/modules`

工程在 `/Users/shang/yl/projects/<app>` 时，override 写成 `../../packages/<dir>` 或 `../../modules/<dir>`。依赖声明用 `any`，在 `dependency_overrides` 里给 `path`。直接依赖和会传递拉取 git 的包都要 override，否则 `pub get` 仍会 clone。

查找顺序：

1. 目录名与 pub 包名相同：先看 `packages/<name>/pubspec.yaml`，再看 `modules/<name>/pubspec.yaml`。没有 `pubspec.yaml` 不算有。
2. 目录名和 pub 名不一致时，用下面的已知映射。
3. 两处都没有：去掉 git url，改用 pub.dev 上的同名包（走 `PUB_HOSTED_URL`）。不要留 `git.yljt.cn`。

| pub 名 | 本机目录 |
|---|---|
| `yl_design` | `packages/yl_design` |
| `yl_foundation` | `packages/yl_foundation` |
| `yl_app_upgrader` | `packages/yl_app_upgrader` |
| `yl_fast_login` | `packages/yl_fast_login` |
| `yl_media` | `packages/yl_media` |
| `image_editor_plus` | `packages/image_editor_plus` |
| `wechat_assets_picker` | `packages/flutter_wechat_assets_picker` |
| `emoji_picker_flutter` | `packages/emoji_picker_flutter` |
| `yl_form_biz_mod` | `modules/yl_form_biz_mod` |
| `yl_cross_care_biz_mod` | `modules/yl_cross_care_biz_mod` |

`sticky_az_list` 本机没有，用 pub `^0.0.7`，不要用私有 git。

`yl_fast_login` 目录可能是 bare repo，没有工作区文件。检出 master，**不要**改 `core.bare`：

```bash
git --git-dir=/Users/shang/yl/packages/yl_fast_login \
  --work-tree=/Users/shang/yl/packages/yl_fast_login checkout -f master
```

override 能压过其它包的版本约束，压不过 path 包自己的 SDK 约束。`image_editor_plus` 的 `sdk: <3.0.0` 这次没有挡住 `pub get`，编译仍会编这个包，不要因此删掉它。

## 依赖钉死（只为编过）

`flutter_localizations` 要 `intl ^0.20.2`。path 包还要旧约束，用 override，不要降 intl。

```yaml
dependency_overrides:
  intl: ^0.20.2                 # yl_foundation 写的是 ^0.18.0
  image_cropper: ^7.1.0         # image_editor_plus 写的是 ^4.0.1
  win32: 5.15.0                 # 5.5.0 使用已删除的 UnmodifiableUint8ListView；调用方允许 <6
  screenshot: 3.0.0             # 2.5.0 的 ViewConfiguration(size:) 已删除；capture / Screenshot 控件仍兼容
  flutter_sticky_header: 0.8.0  # 0.6.5 的 hashValues 已删除；会带上 value_layout_builder 0.5.0
  wechat_picker_library: 1.0.7  # 1.0.5 还在构造 BottomAppBarTheme
```

直接依赖也要抬，否则 lock 不会自己动：

- `flutter_slidable: ^3.1.2`（3.1.1 的 `hashValues`；`^3.1.1` 仍允许锁在 3.1.1）
- `carousel_slider: ^5.1.2`（4.2.1 与 Material 的 `CarouselController` 重名，包自身编不过）

`sticky_az_list ^0.6.5` 的 caret 不到 0.7，所以 `flutter_sticky_header: 0.8.0` 必须放在 override。`image_editor_plus` 的 `screenshot: ^2` 同理。

## Android 华为

AGP 8 不能再使用 `buildscript` classpath `com.huawei.agconnect:agcp:1.6.0.300`。根 `build.gradle` 去掉这份 `buildscript`。`settings.gradle` 的 `plugins` 增加：

```gradle
id "com.huawei.agconnect" version "1.9.1.301" apply false
```

`pluginManagement.repositories` 和 `allprojects.repositories` 保留华为 maven。app 模块里已有的 `com.huawei.agconnect` 插件 id 不用改。Gradle 8.14，AGP 8.5.2，Kotlin 1.9.24，Java 17。`compileSdk` / `minSdk` / `targetSdk` / `ndkVersion` 用 `flutter.*`。

## iOS：recognition_qrcode

`pod install` 成功后还有两个 Xcode 错误，都在这个插件。

**重复拷贝**。podspec 同时有 `s.source_files = 'Classes/**/*'` 和 `s.resources = ['Classes/*.png']`。Xcode：`Unexpected duplicate tasks`，文件是 `bx-right-arrow@3x.png`。在 post_install 里从该 target 的 sources 删掉 png：

```ruby
if target.name == 'recognition_qrcode'
  target.source_build_phase.files.delete_if do |build_file|
    build_file.file_ref&.path&.end_with?('.png')
  end
end
```

**非模块头**。公开头 `ImageViewController.h` 的 `#import <GoogleMLKit/MLKit.h>` 报：`Include of non-modular header inside framework module 'recognition_qrcode.ImageViewController'`。`CLANG_ALLOW_NON_MODULAR_INCLUDES_IN_FRAMEWORK_MODULES = YES` **不能**消掉公开头里的这条。头文件改成 `@class MLKBarcode;`，`.m` 再 `#import <GoogleMLKit/MLKit.h>`。post_install 写回 `ios/.symlinks/plugins/recognition_qrcode/ios/Classes/` 下的这两个文件，避免 pub-cache 重装后丢补丁。所有 pod 仍设置该 CLANG 开关，给 `.m` 里的 umbrella import 用。

保留已有的 `TUICore` `GENERATE_INFOPLIST_FILE=NO` 和 permission_handler 宏。

UIScene：医链旧 AppDelegate 只有 `GeneratedPluginRegistrant.register(with: self)`，没有自定义 MethodChannel。注册挪到 `didInitializeImplicitFlutterEngine`，`didFinishLaunching` 只调 super。

删掉模拟器 `EXCLUDED_ARCHS[sdk=iphonesimulator*] = arm64`，以及 `ios/Flutter/AppFrameworkInfo.plist` 的 `MinimumOSVersion`。

## 编译 error（只改这些）

| 现象 | 解法 |
|---|---|
| `package:flutter/foundation.dart` 不存在 | `.dart_tool/package_config.json` 还指向已删除的 3.19.6。`dart.flutterSdkPath` 钉 `/Users/shang/fvm/versions/3.41.9`，再 `fvm flutter pub get` |
| `hashValues` / `UnmodifiableUint8ListView` / `rebuildIfNecessary` | 用上面的 override，不要手改 pub-cache |
| `BottomAppBarTheme` / `TabBarTheme` / `CardTheme` 不能赋给 `ThemeData` | 改成 `*ThemeData`。`theme.appBarTheme` 的类型是 `AppBarThemeData` |
| 本地 `flutter_wechat_assets_picker` 仍构造 `BottomAppBarTheme` | 改 `BottomAppBarThemeData`；读 `theme.appBarTheme` 的变量改成 `AppBarThemeData`。库本身靠 override 到 1.0.7 |
| `yl_design` 的 `TextTheme.subtitle1` | `titleMedium` |
| `CarouselController` 两边都有 | 升到 carousel_slider 5，调用处改 `CarouselSliderController`。不要用 `hide CarouselController` 掩盖包内部冲突 |
| Dart 3 把 `_` 当变量读 | `_` 是 wildcard。改成具名参数 |
| `sticky_az_list` 没有 `activeBackground` | `symbolBuilder` + `DefaultScrollBarSymbol.styleActive` |
| `YlFastLoginMixin` 没有 `isInPhoneAuthPage` | 删掉用这个字段的 `IgnorePointer` |
| `yl_media` 没有 `onRecognitionQrCode` | 在 `onJumpToPage` 里处理 `route == '/qrcodeWebViewPage'`，URL 取 `arguments['result']` |

分析器剩下的 warning / info 不修。`font_awesome_flutter` 10.x 这次没有报 `IconData` final；一旦出现，再按通用 skill 升到 11 并改 `FaIcon`。`image_editor_plus` 锁着 `^10`，不要为了预防去升。

## 跑模拟器

用**已经 Booted** 的模拟器，不要新开一台。iOS 编 workspace，不编 xcodeproj。

```bash
# 上面的代理与 LANG 环境
xcrun simctl list devices booted
fvm flutter run -d <UDID>
```

成功标志：日志出现 `Flutter run key commands`，并且有 `AppLifecycleState.resumed`。模拟器不在前台时进程会 `paused`，切回去即可，不是崩溃。

`file_picker` 的 `default_package` 提示、PrivacyInfo warning、未登录时的 `token: null`，都不是编译失败。

## 禁止

- 改营销版本，或自动 commit / push
- clone `git.yljt.cn`，本机没有时改回 git url，或修改全局 git proxy
- 把 `git.yljt.cn` 放进代理
- 把 iOS 最低版本升到 15.5
- 升级 `file_picker` 到 12/13
- 只加 `CLANG_ALLOW_NON_MODULAR_INCLUDES_IN_FRAMEWORK_MODULES` 就认为 MLKit 头文件问题已解决
- `dart fix --apply`，或顺手清 deprecated
