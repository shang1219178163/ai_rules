---
name: flutter-tag-release
description: >-
  Flutter / Dart 应用或包在打 git tag（如 v1.2.0）发布前，必须先更新
  README.md 与 CHANGELOG.md；CHANGELOG 每个版本不超过 5 句话。Use when
  the user asks 打tag、打 tag、release、发版、v1.x.x、更新 CHANGELOG、
  更新 README 后打 tag，或准备 GitHub Release / 推送版本标签。
alwaysApply: false
---

# Flutter 打 tag 前更新文档

打 `v*` tag（或用户指定的版本 tag）**之前**，必须先更新并提交 `README.md` 与 `CHANGELOG.md`（通常一并 bump `pubspec.yaml` 的 `version`）。未更新文档不得打 tag。

## 强制顺序

1. 确认目标版本号（如 `1.2.0` → tag `v1.2.0`）。
2. 更新 `pubspec.yaml`：`version: x.y.z+build`。
3. 更新 `CHANGELOG.md`：在文首新增该版本节（见下方格式）。
4. 更新 `README.md`：当前版本号、功能列表、示例命令/产物名中的版本与本次变更一致。
5. 提交上述文件（及同次发版相关代码）。
6. 再创建 annotated tag，例如：
   ```bash
   git tag -a v1.2.0 -m "v1.2.0

   <一句话摘要>"
   ```
7. 仅在用户明确要求时 `git push` 分支与 tag。

## CHANGELOG 规则

- **每个版本不超过 5 句话**（一句一行，完整句号结尾）。
- 不要用冗长的 Added/Changed/Fixed 分节堆砌；直接写该版本的要点句子。
- 可不写文件头说明与空的 `[Unreleased]` 段；版本链接脚注可保留。
- 示例：

```markdown
## [1.2.0] - 2026-09-06

新增前景抠图：无文字时可自动分割，也可点击图片轻点分割对象。
工作台支持「识字 / 抠图」切换，抠图结果可预览并下载为透明 PNG。
```

## README 规则

- 写明**当前版本**（与 `pubspec.yaml` / tag 一致）。
- 功能列表、架构说明覆盖本版本已交付能力（新增功能要写进列表）。
- 打包产物示例、tag 示例中的版本号与本次发版一致。
- 可链到 `CHANGELOG.md`。

## 禁止

- 先打 tag 再补 README / CHANGELOG。
- 单个版本 CHANGELOG 超过 5 句话。
- Tag 指向未包含文档与版本号 bump 的旧提交。
