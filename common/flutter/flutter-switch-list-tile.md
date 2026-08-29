---
name: flutter-switch-list-tile
description: >-
  Use when adding or refactoring boolean switches in Flutter UI (开关、Switch、
  SwitchListTile、配置开关、设置项). Prefer SwitchListTile over Row+Switch.
globs: "**/*.dart"
alwaysApply: false
paths:
  - "**/*.dart"
---

# 开关 UI 优先 SwitchListTile

布尔开关（配置项、设置页、面板里的开/关）优先用 `SwitchListTile`，不要手写 `Row` + `Text`/`Column` + `Switch`。

## 做法

- `title`：主文案；需要说明时用 `subtitle`
- 紧凑面板：`dense: true`，`contentPadding: EdgeInsets.zero`
- 开关颜色走主题 `switchTheme` / `colorScheme`，不要在单个 Switch 上硬编码 `activeColor`

## 例外

仅当布局明显不是「左文案右开关」的 ListTile 形态（例如工具栏内嵌、与其它控件同一行混排）时，再用裸 `Switch`。
