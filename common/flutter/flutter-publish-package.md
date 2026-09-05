---
name: flutter-publish-package
description: >-
  将某 X 组件封装成 Flutter 包并发布到 pub.dev。Use when the user asks 发布包,
  封装为包, 发布pub, 打tag, 生成Flutter包, 或提供某个组件源码要求作为独立
  pub 包发布。完成从创建 package 目录、迁移源码、接入 workspace、建 example、
  美化精简代码、补 CHANGELOG/README 到打 tag 的完整流程。推送 tag 后须盯
  GitHub Actions 发布 workflow 结果并确认 pub.dev 上线。
alwaysApply: false
---

# 将 X 组件发布为 Flutter 包

把某个组件源码封装成独立 pub 包并发布。目标：组件即插即用，example 可跑，README/CHANGELOG 齐备，workspace 正确登记。

## 前置确认

- 以下路径均在 `/Users/shang/GitHub/flutter_packages` 仓库内操作。
- 组件源码位置（如某 Demo 里的 widget 文件）需在开始时定位确认。

## 流程

1. **命名**
   组件名若不是小写下划线（snake_case），先转成小写下划线作为**项目名称**（`${项目名称}`）。

2. **创建 package 项目**
   ```bash
   cd /Users/shang/GitHub/flutter_packages/packages
   flutter create --template=package ${项目名称}
   ```

3. **迁移组件源码**
   进入项目目录，将 X 组件源码迁移到 `lib/src`。
   在 `lib/${项目名称}.dart` 顶部声明 `library;`，随后逐一 `export 'src/${组件相关源码}.dart';`。

4. **加 workspace 声明（package 顶 pubspec）**
   在项目目录 `pubspec.yaml` 的 `dependencies` 之前添加：
   ```yaml
   resolution: workspace
   ```

5. **生成 example**
   ```bash
   # 项目目录下
   flutter create example
   ```
   进入 `example` 后，在 `example/pubspec.yaml` 的 `dev_dependencies` 之前添加路径依赖（注意缩进）：
   ```yaml
   dependencies:
     ${项目名称}:
       path: ../
   ```
   example 应用主题色统一为 **`Colors.green`**：
   ```dart
   ThemeData(
     colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
     useMaterial3: true,
   )
   ```

6. **搭建 example 页面**
   在 `example/lib` 下创建 `pages` 目录，页面文件命名为 `my_home_page.dart`，页面类名统一用 `MyHomePage`（构造带 `required this.title`）。在此实现组件效果。

   `MyHomePage` 需为 **`StatefulWidget`**，结构固定为「上方效果展示 + 下方调参」两部分：
   - **上方展示区**：组件的效果展示区域，居中展示组件（组件需包在 `Center` 里），**不包 `Card`**。
   - **下方调参区**：用 `Card` 包裹，**圆角固定 12**：
     ```dart
     Card(
       shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
       child: ...
     )
     ```
     内部用 `Slider` 等控件实时调整组件属性；`onChanged` 只写 `setState(() => prop = v)`（遵循「不在 setState 里写逻辑」规则），**预览区效果实时变化**。
   - 组件所有对外可调参数都应暴露在调参区；若无参数，可只保留上方展示区。
   - 调参区为预览区提供变量；参数变化经 `setState` 直接驱动上方组件重建。

7. **iOS 模拟器运行 + 美化精简**
   iOS 模拟器成功运行（确认效果）后，对 `MyHomePage` 代码执行：美化、精简代码、审查、修改。

8. **补 CHANGELOG**
   在项目目录下补充 `CHANGELOG.md`。每个版本的说明**不要超过 3 句话**。

9. **更新 README**
   在项目目录下更新 `README.md`，参照仓库内其它包（如 `align_overlay`）的写法：截图用绝对 `raw.githubusercontent.com` 链接 + `width="30%"`，一行最多 3 张图。

10. **登记 workspace（flutter_packages 根 pubspec）**
   在 `/Users/shang/GitHub/flutter_packages/pubspec.yaml` 的 `workspace:` 下按首字母排序添加：
    ```yaml
    - packages/${项目名称}
    - packages/${项目名称}/example
    ```

11. **更新 flutter_packages/README.md**
    在 `/Users/shang/GitHub/flutter_packages/README.md` 中登记新包：
    - 目录树：在 `packages/` 分支下按字母序加入 `├── ${项目名称}/   # 组件描述`。
    - 发布表：在「发布到 pub.dev」的表格中新增一行，含 Package / Tag 示例 / Workflow / pub.dev 链接。

## 发布要点

- 交接前 `dart analyze` 目标文件要干净，去掉警告。
- 截图宽高统一 `width="30%"`，用 `raw.githubusercontent.com` 绝对链接，且保证推送到 `main` 后能被 pub.dev 正确展示。
- CHANGELOG 版本条目控制在 3 句话内；README 覆盖 Features / Getting started / Usage / Parameters / Example。
- 发布链路：提交改动 → 合并到 main → 打 `${项目名称}-v1.0.0` tag → 推送。若有发布 workflow（参考 `.github/workflows/enhance_widget_publish.yml`）会自动触发 pub.dev 发布。

## 盯发布结果（每次打 tag / 推送后必做）

**推送匹配规则的 tag 后，不要立刻结束对话**：必须盯到本次 GitHub Actions 发布 workflow 出最终结论，并把结果回报给用户。

### 步骤

1. **定位本次 run**（推送 tag 后立刻执行）：
   ```bash
   gh run list --workflow=${项目名称}_publish.yml --limit 3
   ```
   取最新一条（通常 `event=push`、`headBranch=${项目名称}-vX.Y.Z`），记下 `run_id`。

2. **轮询直到完成**（约每 30–60 秒一次，直到 `status=completed`）：
   ```bash
   gh run view <run_id> --json status,conclusion,url,displayTitle,updatedAt
   gh run view <run_id> --json jobs --jq '.jobs[] | {name, status, conclusion, steps: [.steps[] | {name, status, conclusion}]}'
   ```
   也可用 `gh run watch <run_id>`（若环境支持交互）。

3. **成功时**：
   - 向用户报告：workflow 链接 + `conclusion=success`。
   - 再确认 pub.dev 已上线：
     ```bash
     curl -sL "https://pub.dev/api/packages/${项目名称}" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["latest"]["version"], d["latest"]["published"])'
     ```
   - 回报 pub.dev 包页：`https://pub.dev/packages/${项目名称}`。

4. **失败时**：
   - 拉失败步骤日志并定位原因（常见：LICENSE 仍是 TODO、`pub publish` 校验失败、凭证缺失）：
     ```bash
     gh run view <run_id> --log-failed
     ```
   - 向用户说明失败步骤与原因；**先修问题再重打/重推 tag**（或 `gh workflow run` / `workflow_dispatch`），不要只报「失败了」就结束。

### 硬性要求

- 「打 tag / 推送 / 发布」类请求的收尾 = **workflow 终态 + pub.dev 确认（成功时）**，不是「已 push tag」。
- 旧 tag 删除后重打同名 tag 也会重新触发 workflow，同样要盯。
- 若仓库尚无 `${项目名称}_publish.yml`，先补齐（对照现有 `*_publish.yml`）再发；有 workflow 却未触发时，检查 tag 名是否匹配 `on.push.tags` 规则。

## 常见问题 / 踩坑记录

发布某个包时可能遇到以下问题，先按此处排查。

### 1. workspace 解析失败：member 缺 `resolution: workspace`

运行仓库根 `flutter pub get` 时报：
```
packages/<name>/example/pubspec.yaml is included in the workspace from ./pubspec.yaml,
but does not have `resolution: workspace`.
```
或
```
Workspace members must have unique names. `apps/example/pubspec.yaml` and
packages/<name>/example/pubspec.yaml are both called "example".
```

**解决**：
- 给 `<name>/example/pubspec.yaml` 的 `environment` 之后加 `resolution: workspace`。
- example 包名不能叫 `example`（与 `apps/example` 冲突），改成 `<name>_example`（如 `animated_halo_example`）。
- workspace 里每个 member 的包名必须唯一。

### 2. 新建 example 后根 `flutter pub get` / analyze 慢

`flutter run` 前先让包处于 workspace 中：先在根 `pubspec.yaml` 的 `workspace:` 登记该包（含 `/example`），再 `flutter pub get`，否则解析失败。

### 3. iOS 构建失败：The sandbox is not in sync with the Podfile.lock

```
Failed to build iOS app
Error (Xcode): The sandbox is not in sync with the Podfile.lock.
Run 'pod install' or update your CocoaPods installation.
```

**解决**：在 `example/ios` 下运行 `pod install` 同步 Pods。若 `pod install` 因 **Ruby / CocoaPods 编码**报错（`Unicode Normalization not appropriate for ASCII-8BIT`），先设 UTF-8 locale 再跑：
```bash
export LANG=en_US.UTF-8
cd example/ios && pod install
```

### 4. 默认模板文件要清理

`flutter create --template=package` 和 `flutter create example` 生成的默认文件引用不存在的 `Calculator` / 计数器，会导致 `analyze` 报错：
- 删除包级 `test/<name>_test.dart`（引用 `Calculator`）。
- 重写 `example/test/widget_test.dart`（默认计数器测试），改为验证新页面。
- 平台残留：`example/ios/`、`macos/` 下会生成 `Podfile`、`*.xcconfig`、`GeneratedPluginRegistrant.swift` 等，保留即可。

### 5. 发布前的 LICENSE

`flutter create` 生成的 `LICENSE` 内容是 `TODO: Add your license here.`，**直接发布会被 pub.dev 拒**。发布前把它替换为标准 MIT License。

### 6. example widget 测试跑挂

`AnimatedCrossFade` 等会把 first/second child 都保留在 widget 树里（隐藏的那个仍在树中），`find.text('secondChild')` 仍能命中。断言时不要假设"未显示 = 不在树中"，改用验证标题 / 明确存在的元素；或直接断言组件本身渲染成功。
