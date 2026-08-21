---
name: fix-flutter-sdk-path
description: >-
  Use when Cursor / VS Code 打开 Flutter 项目提示 Flutter SDK 路径不对、dart.flutterSdkPath
  配置错误、.fvm/flutter_sdk 软链接失效、fvm SDK 版本不存在. 统一修复为 /Users/shang/fvm/default.
alwaysApply: false
---

# 修复 Flutter SDK 路径

Cursor / VS Code 的 Dart 插件通过 `.vscode/settings.json` 的 `dart.flutterSdkPath` 定位 Flutter SDK。路径失效时（软链接指向不存在的 fvm 版本、相对路径解析错误），编辑器无法识别 SDK。

## 铁律

1. **统一目标**：`dart.flutterSdkPath` 一律使用绝对路径 `/Users/shang/fvm/default`。
2. **不用相对路径**：禁止 `../../fvm/default`、`.fvm/flutter_sdk` 这类相对配置（会随打开目录解析出错）。
3. **不自动提交**：只改配置文件，不 git commit / push。

## 排查步骤

1. 搜索全部目标仓库的配置：
   `rg -l --hidden --no-ignore -g '!**/.git/**' 'dart\.flutterSdkPath' /Users/shang/GitHub/`
2. 逐个检查 `.vscode/settings.json` 中 `dart.flutterSdkPath` 的值。
3. 确认 fvm 默认版本有效：
   - `ls -la /Users/shang/fvm/default`（软链接存在）
   - `ls /Users/shang/fvm/versions/`（实际安装版本）
4. 若值为相对路径或指向不存在的版本，改为 `/Users/shang/fvm/default`。

## 必做

- 用 apply_patch 局部修改，只改 `dart.flutterSdkPath` 一行，不动其它配置。
- 修改后让用户在 Cursor 中执行 `Developer: Reload Window` 使 Dart 插件重新解析 SDK。

## 禁止

- 改 `.fvmrc`、`android/settings.gradle` 里的 `flutterSdkPath`（Gradle 混合工程配置，语义不同）。
- 修改文档中的示例占位符（如 `/Users/xxx/flutter_3.16.9`）。
