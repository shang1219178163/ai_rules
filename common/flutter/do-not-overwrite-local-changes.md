---
name: do-not-overwrite-local-changes
description: >-
  Use when editing existing files, using Write on a file that already exists,
  fixing compile errors in files the user did not name, or when the user is also
  editing (手动修改、本地改动、不要覆盖、整文件覆盖、Write 覆盖). Prevents the agent from clobbering
  unsaved or in-progress user edits.
alwaysApply: false
---

# 不覆盖本地改动

用户会同时改代码。磁盘、编辑器未保存缓冲、Read 结果可能不一致。禁止用整文件覆盖去“修好”用户正在改的文件。

## 铁律

**用户没点名要改的文件，不要写。点名要改的文件，只用局部替换。**

## 必做

1. 先读磁盘上的当前文件，再改。
2. 已有文件一律用 StrReplace / 局部补丁，禁止 Write 整文件覆盖。
3. 只改用户本轮明确提到的路径。封装 API、修编译、对齐模型，都不构成改其它文件的许可。
4. Read 与磁盘/行数对不上、或文件刚被用户改过：停下来问，不要自行重写。
5. 用户说「不要改 xxx」：该路径整轮只读。

## 禁止

- 用 Write 覆盖已存在的源文件（新建文件除外）
- 为修重复类名、JsonToModel 质量、相邻编译错误而重写用户刚生成/正在改的模型
- 把「Read 到的旧内容」当成权威，覆盖用户未保存或刚保存的新内容
- 顺手改调用方、主题色、其它 mixin「保持一致」

## 借口对照

| 借口 | 实际 |
|------|------|
| 生成模型编不过，只能整文件重写 | 只改冲突那几处，或问用户要不要动模型 |
| Write 比补丁更干净 | 干净会盖掉本地改动；补丁才安全 |
| 用户说用这个模型，所以我重写模型 | 用 = 按现有类型解析，不是改模型文件 |
| 磁盘和 Read 不一致，以我写的为准 | 以用户文件为准；不一致就问 |
| 相关文件也要一起改才能跑 | 先完成点名的文件；其它改动先问 |

## 红旗 — 停下

- 准备对已有 `.dart` / 模型文件调用 Write
- 准备改用户没点名的路径
- 「先把模型整理干净再写 mixin」
- 「生成稿太乱，我重写一版」

出现以上任一：不要写。问一句该不该动那个文件。
