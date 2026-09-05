---
name: macos-appicon
description: >-
  Generate and refresh Flutter macOS AppIcon with flutter_launcher_icons,
  Info.plist CFBundleIconName, clean Debug rebuild, lsregister, and Dock
  refresh. Use when setting macOS app icon, flutter_launcher_icons, AppIcon,
  Dock still shows Flutter logo, or CFBundleIconName.
alwaysApply: false
---

# macOS AppIcon 生成

Flutter **仅 macOS** 目标时，按下列步骤生成并刷新 AppIcon。调试模式下 Dock 仍显示 Flutter logo，多半是缓存或 Info.plist 未声明 `CFBundleIconName`。

## 前置

- 源图为正方形 PNG（建议 ≥ 1024×1024），路径存在（常见：`assets/images/icon_new.png`）。
- **不要**把仅用于 launcher 的目录写进 `pubspec.yaml` 的 `flutter.assets`（目录不存在会报 `unable to find directory entry`）。
- `ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon`（Xcode 工程默认即可）。

## 工作流（必须按序执行）

1. 安装 flutter_launcher_icons。
2. 运行 dart run flutter_launcher_icons。
3. Info.plist：改为声明 CFBundleIconName = AppIcon（去掉空的 CFBundleIconFile）。
4. 重新生成图标 + flutter clean + Debug 构建，并用 lsregister 注册新 .app。
5. 执行 killall Dock 刷新 Dock。

### 步骤 1 — 安装 flutter_launcher_icons

`pubspec.yaml` 的 `dev_dependencies`：

```yaml
dev_dependencies:
  flutter_launcher_icons: ^0.14.4
```

项目根配置 `flutter_launcher_icons.yaml`（按实际源图改 `image_path`）：

```yaml
# 生成图标：dart run flutter_launcher_icons
flutter_launcher_icons:
  image_path: "assets/images/icon_new.png"
  android: false
  ios: false
  macos:
    generate: true
    image_path: "assets/images/icon_new.png"
```

然后：

```bash
flutter pub get
```

### 步骤 2 — 生成图标

```bash
dart run flutter_launcher_icons
```

确认输出 `Creating Icons for MacOS...` / `Successfully generated launcher icons`，且 `macos/Runner/Assets.xcassets/AppIcon.appiconset/` 下 PNG 已更新。

### 步骤 3 — Info.plist

编辑 `macos/Runner/Info.plist`：

- 去掉空的 `CFBundleIconFile`（或不要留空字符串）。
- 改为声明：

```xml
<key>CFBundleIconName</key>
<string>AppIcon</string>
```

### 步骤 4 — clean、Debug 构建、lsregister

在项目根执行（将 `image2text.app` 换成实际产物名）：

```bash
dart run flutter_launcher_icons
flutter clean
flutter build macos --debug

APP="build/macos/Build/Products/Debug/<app_name>.app"
touch "$APP"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP"
```

校验：

```bash
plutil -p "$APP/Contents/Info.plist" | grep -i icon
# 期望含 CFBundleIconName => AppIcon
ls -la "$APP/Contents/Resources/AppIcon.icns"
```

### 步骤 5 — 刷新 Dock

```bash
killall Dock
```

然后重新 `flutter run -d macos`。若仍显示旧图标：Cmd+Q 完全退出应用；或从 Dock 移除旧图标后，再从上述 Debug `.app` 启动。

## 清单

```
- [ ] flutter_launcher_icons 已安装且 yaml 指向有效源图
- [ ] dart run flutter_launcher_icons 成功
- [ ] Info.plist 有 CFBundleIconName=AppIcon，无空 CFBundleIconFile
- [ ] flutter clean + flutter build macos --debug
- [ ] lsregister 已注册新 .app
- [ ] killall Dock
```
