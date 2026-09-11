---
name: git-tag-release
description: >-
  代码打 tag 之前检查是否存在 CHANGELOG、LICENSE、README 文档，不存在就创建；
  存在则更新 CHANGELOG 和 README。Use when the user asks 打tag、打 tag、
  git tag、release、发版、v1.x.x、准备 GitHub Release，或推送版本标签。
alwaysApply: false
---

# 打 tag 前检查 / 更新文档

**代码打 tag 之前检查是否存在 CHANGELOG、LICENSE、README 文档，不存在就创建。存在更新 CHANGELOG 和 README。**

未完成上述文档步骤，不得创建 tag。

## 文档根目录

以**本次发版目标**为准（仓库根，或 monorepo 里正在发版的子包目录）。以下文件名均可接受：

| 文档 | 可接受文件名 |
| --- | --- |
| CHANGELOG | `CHANGELOG.md`、`CHANGELOG`、`Changelog.md` |
| LICENSE | `LICENSE`、`LICENSE.md`、`LICENCE` |
| README | `README.md`、`README` |

优先使用仓库已有命名；新建时默认 `CHANGELOG.md`、`LICENSE`、`README.md`。

## 强制顺序

1. 确认目标版本（如 `1.2.0` → tag `v1.2.0`）与文档根目录。
2. **检查**三份文档是否存在：
   - **不存在 → 创建**（见下方模板）。
   - **已存在 → 更新 `CHANGELOG` 与 `README`**（`LICENSE` 一般不改；仅当版权年/持有人明显过期且用户同意时再改）。
3. 若为 Flutter / Dart 包：同时 bump `pubspec.yaml` 的 `version`，并遵循 `flutter-tag-release`（CHANGELOG 每版本 ≤ 5 句）。
4. 提交文档（及同次发版相关代码）。仅在用户明确要求时 commit。
5. 再打 annotated tag，例如：
   ```bash
   git tag -a v1.2.0 -m "v1.2.0

   <一句话摘要>"
   ```
6. 仅在用户明确要求时 `git push` 分支与 tag。

## 不存在时：创建模板

### CHANGELOG.md

```markdown
# Changelog

本文件记录重要变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [x.y.z] - YYYY-MM-DD

### Added

- <本版本要点>
```

把 `x.y.z` / 日期换成本次发版信息；要点来自 `git log` / diff，写清用户可见变更。

### LICENSE

默认 **MIT**（若仓库已有其它许可证约定，从其约定，勿擅自换成 MIT）：

```text
MIT License

Copyright (c) YYYY <Author>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- `YYYY`：当前年份。
- `<Author>`：从同仓库其它 `LICENSE`、`package`/`pubspec` authors、或 `git log` 推断；不确定则先问用户。

### README.md

至少包含：项目名与一句话说明、当前版本（与 tag 一致）、安装/使用要点、链到 `CHANGELOG.md`（及 `LICENSE` 可选）。按实际技术栈补全，勿写空壳占位段。

## 已存在时：更新规则

### CHANGELOG

- 在**文首版本区**新增本次 `## [x.y.z] - YYYY-MM-DD`（或项目既有风格）。
- 若有 `[Unreleased]`：把已交付条目移入该版本节，并清空或保留空的 Unreleased。
- 内容与即将打 tag 的提交一致；不要写未合并的计划项。
- Flutter 项目：每个版本不超过 5 句话（见 `flutter-tag-release`）。

### README

- 当前版本号与 tag / 包版本字段一致。
- 功能列表、示例、命令中的版本与本次变更对齐。
- 可链到 `CHANGELOG.md`。

### LICENSE

- 已存在则**默认不动**。
- 缺失才创建；不要在打 tag 流程里改许可证类型。

## 禁止

- 先打 tag 再补 CHANGELOG / LICENSE / README。
- Tag 指向未包含文档更新（及必要版本 bump）的旧提交。
- 在用户未要求时自动 `git push --tags`。
