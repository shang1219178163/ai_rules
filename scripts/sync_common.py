#!/usr/bin/env python3
"""从 common/ 一键同步 Claude / Codex / Cursor 挂载层。

正文只维护在 common/（可分子目录：flutter/、backend/、shared/、ops/）。
本脚本递归扫描 common/**/*.md，按 frontmatter 重建：
  - claude/CLAUDE.md、claude/rules/、claude/skills/
  - codex/AGENTS.md、codex/skills/
  - cursor/rules/*.mdc

模块名取 frontmatter name（或文件 stem），与所在子目录无关。
用法（仓库根目录）:
  ./scripts/sync_common.py
  python3 scripts/sync_common.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "common"
CLAUDE = ROOT / "claude"
CODEX = ROOT / "codex"
CURSOR_RULES = ROOT / "cursor" / "rules"

CORE_NAME = "core"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse leading YAML-like frontmatter. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    meta: dict = {}
    current_list_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        list_item = re.match(r"^\s*-\s+(.*)$", line)
        if list_item and current_list_key:
            val = list_item.group(1).strip().strip('"').strip("'")
            meta.setdefault(current_list_key, []).append(val)
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            current_list_key = key
            meta[key] = []
            continue
        current_list_key = None
        if val.lower() in ("true", "false"):
            meta[key] = val.lower() == "true"
        else:
            meta[key] = val.strip('"').strip("'")
    return meta, body


def load_modules() -> dict[str, dict]:
    if not COMMON.is_dir():
        raise SystemExit(f"missing {COMMON}")
    modules: dict[str, dict] = {}
    for path in sorted(COMMON.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(COMMON).parts):
            continue
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        name = meta.get("name") or path.stem
        rel = path.relative_to(COMMON).as_posix()
        is_core = path == COMMON / f"{CORE_NAME}.md"
        if name in modules:
            prev = modules[name]["rel"]
            raise SystemExit(f"duplicate module name {name!r}: {prev} and {rel}")
        modules[name] = {
            "path": path,
            "stem": path.stem,
            "rel": rel,
            "meta": meta,
            "is_core": is_core,
        }
    if CORE_NAME not in modules and (COMMON / f"{CORE_NAME}.md").exists():
        modules[CORE_NAME] = {
            "path": COMMON / f"{CORE_NAME}.md",
            "stem": CORE_NAME,
            "rel": f"{CORE_NAME}.md",
            "meta": {},
            "is_core": True,
        }
    return modules


def write_file(path: Path, content: str, dry_run: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        action = "update"
    elif path.exists():
        if path.read_text(encoding="utf-8") == content:
            return
        action = "update"
    else:
        action = "create"
    if dry_run:
        print(f"  [{action}] {path.relative_to(ROOT)}")
        return
    if path.is_symlink() or path.exists():
        path.unlink()
    path.write_text(content, encoding="utf-8")
    print(f"  [{action}] {path.relative_to(ROOT)}")


def ensure_symlink(link: Path, target: Path, dry_run: bool) -> None:
    rel = Path(os_relpath(target, link.parent))
    desired = rel.as_posix()
    if link.is_symlink() and link.readlink().as_posix() == desired:
        return
    action = "relink" if link.exists() or link.is_symlink() else "link"
    if dry_run:
        print(f"  [{action}] {link.relative_to(ROOT)} -> {desired}")
        return
    if link.exists() or link.is_symlink():
        link.unlink()
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(desired)
    print(f"  [{action}] {link.relative_to(ROOT)} -> {desired}")


def os_relpath(target: Path, start: Path) -> str:
    import os

    return os.path.relpath(target, start)


def prune_dir(directory: Path, keep_names: set[str], pattern: str, dry_run: bool) -> None:
    if not directory.is_dir():
        return
    for path in directory.glob(pattern):
        if path.is_dir():
            name = path.name
            if name not in keep_names:
                if dry_run:
                    print(f"  [prune] {path.relative_to(ROOT)}/")
                else:
                    # remove skill dir contents
                    for child in path.rglob("*"):
                        if child.is_file() or child.is_symlink():
                            child.unlink()
                    for child in sorted(path.rglob("*"), reverse=True):
                        if child.is_dir():
                            child.rmdir()
                    path.rmdir()
                    print(f"  [prune] {path.relative_to(ROOT)}/")
        else:
            name = path.stem
            if name not in keep_names:
                if dry_run:
                    print(f"  [prune] {path.relative_to(ROOT)}")
                else:
                    path.unlink()
                    print(f"  [prune] {path.relative_to(ROOT)}")


def yaml_paths_block(paths: list[str]) -> str:
    if not paths:
        return ""
    lines = "\n".join(f'  - "{p}"' for p in paths)
    return f"paths:\n{lines}\n"


def sync_claude(modules: dict[str, dict], dry_run: bool) -> None:
    print("Claude")
    write_file(CLAUDE / "CLAUDE.md", "@../common/core.md\n", dry_run)

    rule_names: set[str] = set()
    skill_names: set[str] = set()

    for name, mod in modules.items():
        if mod["is_core"]:
            continue
        meta = mod["meta"]
        paths = meta.get("paths") or []
        if isinstance(paths, str):
            paths = [paths]

        if paths:
            rule_names.add(name)
            content = (
                "---\n"
                f"{yaml_paths_block(paths)}"
                "---\n"
                f"@../../common/{mod['rel']}\n"
            )
            write_file(CLAUDE / "rules" / f"{name}.md", content, dry_run)
        else:
            skill_names.add(name)
            desc = meta.get("description") or name
            content = (
                "---\n"
                f"name: {name}\n"
                f"description: {desc}\n"
                "---\n"
                f"@../../../common/{mod['rel']}\n"
            )
            write_file(CLAUDE / "skills" / name / "SKILL.md", content, dry_run)

    prune_dir(CLAUDE / "rules", rule_names, "*.md", dry_run)
    # prune skill dirs
    skills_root = CLAUDE / "skills"
    if skills_root.is_dir():
        for d in skills_root.iterdir():
            if d.is_dir() and d.name not in skill_names:
                if dry_run:
                    print(f"  [prune] {d.relative_to(ROOT)}/")
                else:
                    for child in d.iterdir():
                        child.unlink()
                    d.rmdir()
                    print(f"  [prune] {d.relative_to(ROOT)}/")


def sync_codex(modules: dict[str, dict], dry_run: bool) -> None:
    print("Codex")
    ensure_symlink(CODEX / "AGENTS.md", COMMON / "core.md", dry_run)

    keep: set[str] = set()
    for name, mod in modules.items():
        if mod["is_core"]:
            continue
        keep.add(name)
        ensure_symlink(
            CODEX / "skills" / name / "SKILL.md",
            mod["path"],
            dry_run,
        )

    skills_root = CODEX / "skills"
    if skills_root.is_dir():
        for d in skills_root.iterdir():
            if d.is_dir() and d.name not in keep:
                if dry_run:
                    print(f"  [prune] {d.relative_to(ROOT)}/")
                else:
                    for child in d.iterdir():
                        child.unlink()
                    d.rmdir()
                    print(f"  [prune] {d.relative_to(ROOT)}/")


def sync_cursor(modules: dict[str, dict], dry_run: bool) -> None:
    print("Cursor")
    keep: set[str] = set()

    for name, mod in modules.items():
        keep.add(name)
        meta = mod["meta"]
        desc = meta.get("description") or name
        always = bool(meta.get("alwaysApply")) if "alwaysApply" in meta else mod["is_core"]
        globs = meta.get("globs")

        if mod["is_core"]:
            content = (
                "---\n"
                f"description: {desc if desc != name else '全局约定：中文回复、禁止自动提交'}\n"
                "alwaysApply: true\n"
                "---\n\n"
                f"[core](mdc:../../common/{mod['rel']})\n"
            )
        elif globs:
            # globs may be string or leftover list — normalize to string for Cursor
            if isinstance(globs, list):
                globs_str = ",".join(globs)
            else:
                globs_str = str(globs)
            content = (
                "---\n"
                f"description: {desc}\n"
                f'globs: "{globs_str}"\n'
                "alwaysApply: false\n"
                "---\n\n"
                f"[{name}](mdc:../../common/{mod['rel']})\n"
            )
        else:
            # agent-requested
            content = (
                "---\n"
                f"description: {desc}\n"
                "alwaysApply: false\n"
                "---\n\n"
                f"[{name}](mdc:../../common/{mod['rel']})\n"
            )

        # core description override when no frontmatter description
        if mod["is_core"] and not meta.get("description"):
            content = (
                "---\n"
                "description: 全局约定：中文回复、禁止自动提交\n"
                "alwaysApply: true\n"
                "---\n\n"
                "[core](mdc:../../common/core.md)\n"
            )

        write_file(CURSOR_RULES / f"{name}.mdc", content, dry_run)

    prune_dir(CURSOR_RULES, keep, "*.mdc", dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Claude/Codex/Cursor adapters from common/")
    parser.add_argument("--dry-run", action="store_true", help="只打印将要执行的操作")
    args = parser.parse_args()

    modules = load_modules()
    if CORE_NAME not in modules:
        print("error: common/core.md is required", file=sys.stderr)
        return 1

    print(f"Found {len(modules)} module(s) in common/")
    if args.dry_run:
        print("(dry-run)\n")

    sync_claude(modules, args.dry_run)
    sync_codex(modules, args.dry_run)
    sync_cursor(modules, args.dry_run)
    print("\nDone. Body edits in common/ need no copy; this refreshes wrappers/symlinks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
