# ai_rules

Personal AI rules for multi-project sharing across Claude Code, Codex, and Cursor.

个人 AI 规则库，便于在 Claude Code、Codex、Cursor 多项目间共享。

[English](#english) · [中文](#中文)

---

## English

### Layout

```text
common/                 # Single source of truth (rule bodies)
  core.md               # Always-on: 中文、禁止自动 git commit
  flutter.md            # Path / skill scoped modules…
  backend.md            # Long reference → skills / agent-requested
  …

claude/
  CLAUDE.md             # Only @common/core.md
  rules/                # Path-scoped → install as .claude/rules/
  skills/backend/       # On-demand skill for long backend rules

codex/
  AGENTS.md             # Symlink → common/core.md
  skills/<topic>/       # Symlink SKILL.md → common/<topic>.md
                        # Install as .agents/skills/

cursor/rules/           # Thin .mdc wrappers with globs / alwaysApply
```

### Load strategy

| Layer | When it loads | What belongs here |
|-------|---------------|-------------------|
| Always-on | Every session | `core` only |
| Path-scoped | Matching files opened | Short domain rules (flutter, api, docker…) |
| Skills / agent-requested | Task match or manual invoke | Long refs (`backend`) |

Do **not** `@` or symlink the entire `common/` tree into `CLAUDE.md` / `AGENTS.md`.

### Per-tool wiring

#### Cursor

Copy or symlink `cursor/rules/*.mdc` into the project’s `.cursor/rules/`, keeping relative paths to `common/` (or vendor this repo as a whole).

- `core.mdc` → `alwaysApply: true`
- Modules with `globs` → activate on matching files
- `backend` / `microservice` / `performance` → no broad globs; agent picks them by `description`

#### Claude Code

In a project:

1. Point `CLAUDE.md` at this repo’s `claude/CLAUDE.md` (or copy and keep `@../common/core.md` valid).
2. Link `claude/rules/` → `.claude/rules/` (path-scoped via `paths:` + `@` import).
3. Link `claude/skills/backend/` → `.claude/skills/backend/` (body loads when the skill is used).

#### Codex

1. Link `codex/AGENTS.md` → project `AGENTS.md` (follows symlink to `common/core.md`).
2. Link `codex/skills/` → project `.agents/skills/` (each `SKILL.md` is a symlink into `common/`).

Codex does not expand `@` imports; use symlinks for always-on and skills.

### Editing rules

- Edit bodies only under `common/`.
- Keep `common/core.md` short.
- Prefer path triggers for short modules; use skills / agent-requested for large documents (avoid wide globs like `**/*.{ts,js,py}` on `backend.md`).

### Sync adapters

Body text is referenced (import / symlink), so editing `common/*.md` content does **not** require copying. After you **add / remove / rename** a module or change frontmatter (`globs` / `paths` / `description`), refresh wrappers:

```bash
./scripts/sync_common.py
# preview only:
./scripts/sync_common.py --dry-run
```

The script rebuilds `claude/`, `codex/`, and `cursor/rules/` from `common/` frontmatter:
- has `paths` → Claude path-scoped rule
- no `paths` → Claude skill
- has `globs` → Cursor file-scoped rule; otherwise agent-requested
- Codex: `AGENTS.md` → `core`; every other module → `skills/<name>/SKILL.md` symlink

---

## 中文

### 目录结构

```text
common/                 # 唯一正文（规则内容）
  core.md               # 始终加载：中文回复、禁止自动 git commit
  flutter.md            # 按路径 / Skill 按需加载的模块…
  backend.md            # 长文参考 → Skills / Agent 按需选用
  …

claude/
  CLAUDE.md             # 仅 @common/core.md
  rules/                # 路径触发 → 安装为 .claude/rules/
  skills/backend/       # 长文 backend 的按需 Skill

codex/
  AGENTS.md             # 符号链接 → common/core.md
  skills/<topic>/       # SKILL.md 符号链接 → common/<topic>.md
                        # 安装为 .agents/skills/

cursor/rules/           # 薄封装 .mdc（globs / alwaysApply）
```

### 加载策略

| 层级 | 何时加载 | 放什么 |
|------|----------|--------|
| Always-on | 每次会话 | 仅 `core` |
| Path-scoped | 打开匹配文件时 | 中短领域规范（flutter、api、docker…） |
| Skills / agent-requested | 任务匹配或手动调用 | 长文参考（`backend`） |

**不要**把整个 `common/` 用 `@` 或符号链接塞进 `CLAUDE.md` / `AGENTS.md`。

### 各端挂载

#### Cursor

将 `cursor/rules/*.mdc` 复制或符号链接到项目的 `.cursor/rules/`，并保持到 `common/` 的相对路径（或整仓引用本仓库）。

- `core.mdc` → `alwaysApply: true`
- 带 `globs` 的模块 → 打开匹配文件时激活
- `backend` / `microservice` / `performance` → 不用宽泛 globs；由 Agent 按 `description` 选用

#### Claude Code

在业务项目中：

1. 让项目 `CLAUDE.md` 指向本仓库的 `claude/CLAUDE.md`（或复制并保证 `@../common/core.md` 路径有效）。
2. 将 `claude/rules/` 链接为 `.claude/rules/`（`paths:` + `@` 按路径触发）。
3. 将 `claude/skills/backend/` 链接为 `.claude/skills/backend/`（调用 Skill 时才加载正文）。

#### Codex

1. 将 `codex/AGENTS.md` 链接为项目 `AGENTS.md`（跟随符号链接到 `common/core.md`）。
2. 将 `codex/skills/` 链接为项目 `.agents/skills/`（每个 `SKILL.md` 指向 `common/`）。

Codex **不支持** `@` 展开；always-on 与 skills 请用符号链接。

### 编辑约定

- 正文只改 `common/`。
- `common/core.md` 保持极短。
- 短规范优先路径触发；长文档用 Skills / agent-requested（避免给 `backend.md` 配 `**/*.{ts,js,py}` 这类宽泛 globs）。

### 一键同步挂载层

正文通过引用 / 符号链接读取，**只改 `common` 正文内容时不必拷贝**。在**新增 / 删除 / 重命名**模块，或改 frontmatter（`globs` / `paths` / `description`）之后，运行：

```bash
./scripts/sync_common.py
# 仅预览：
./scripts/sync_common.py --dry-run
```

脚本会按 `common/` 的 frontmatter 重建 `claude/`、`codex/`、`cursor/rules/`：
- 有 `paths` → Claude 路径规则
- 无 `paths` → Claude Skill
- 有 `globs` → Cursor 按文件触发；否则 Agent 按需选用
- Codex：`AGENTS.md` → `core`；其余模块 → `skills/<name>/SKILL.md` 符号链接
