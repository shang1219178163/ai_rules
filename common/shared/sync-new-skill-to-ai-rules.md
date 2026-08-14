---
name: sync-new-skill-to-ai-rules
description: >-
  Use when creating a new Cursor/Claude/Codex skill, writing SKILL.md, or the
  user says 生成 skill / 新增 skill / 同步到 ai_rules. Always copy the new skill into
  the ai_rules repo.
alwaysApply: false
---

# 新增 Skill 同步到 ai_rules

以后新增 skill 都同步一份到 [ai_rules](https://github.com/shang1219178163/ai_rules)。不要只写在业务仓库的 `.cursor/skills/` 或 `~/.cursor/skills/`。

## 步骤

1. 先在对话里写好 skill 正文。
2. 把**同一份正文**写入 `/Users/shang/GitHub/ai_rules/common/<领域>/<name>.md`，带 frontmatter（`name`、`description`、`alwaysApply: false`）。无 `paths` / 无 `globs` → 按需 Skill。
3. 在 ai_rules 根目录运行 `./scripts/sync_common.py`。
4. 当前 Flutter 项目需要立刻生效时，把生成的 `cursor/rules/<name>.mdc` 符号链接到项目 `.cursor/rules/`。
5. **不要自动 git commit / push**。

## 目录

| 主题 | 写入 |
|------|------|
| Flutter / Dart | `common/flutter/` |
| iOS / Swift / ObjC | `common/iOS/` |
| 后端 / API | `common/backend/` |
| Docker / 交付 | `common/ops/` |
| 其它横切 | `common/shared/` |

模块 `name` 用小写连字符（如 `do-not-overwrite-local-changes`）。标题可以用中文。
