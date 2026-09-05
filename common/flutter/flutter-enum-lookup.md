---
name: flutter-enum-lookup
description: >-
  Use when resolving a Dart/Flutter enum member from one of its properties
  (枚举根据属性取值反查枚举成员、nameOf、valueOf、label、byName、firstOrNull、
  字符串映射到枚举). Given an enum with extra fields, look up the member by value
  using `values.where(...).firstOrNull`.
alwaysApply: false
globs: "**/*.dart"
paths:
  - "**/*.dart"
---

# Dart 枚举：通过成员属性反查枚举类型

外部来的字符串 / 值（如 CLI 参数、接口返回的 `name`、配置项）需要映射回某个枚举成员时，优先用 **`values.where(...).firstOrNull`**，而不是手写 `switch`/`for` 匹配或维护一份并列清单。

## 推荐范式（以 `deploy.dart` 为例）

给枚举成员附加自定义字段，然后用静态方法按字段值反查：

```dart
enum DeployArch {
  x86_64(value: '1', label: 'Intel'),
  arm64(value: '2', label: 'Apple Silicon');

  const DeployArch({required this.value, required this.label});
  final String value;
  final String label;

  /// 按 value 字段反查
  static DeployArch? valueOf(String? v) =>
      values.where((e) => e.value == v).firstOrNull;

  /// 按枚举名（name）反查
  static DeployArch? nameOf(String? v) =>
      values.where((e) => e.name == v).firstOrNull;
}
```

要点：
- `values` 就是所有枚举成员，**不要**再单独维护 `const all = [...]` 清单（易漏增、重复）。
- 用 `.firstOrNull` 返回可空结果，调用方能表达「未匹配」。
- 反查方法收 `String? v`，方法内自行判空/判空串，返回 `null` 兜底。

## 命名约定

- 查询哪个属性，方法就叫 **`<属性名>Of`**：按 `name` 查 → `nameOf`，按 `value` 查 → `valueOf`，按 `label` 查 → `labelOf`。
- 参数名固定用 **`v`**（`String? v`），不要用 `value`、`input` 等，保持统一。

## 反查维度

| 想按什么查 | 方法名（`<属性名>Of`） | 写法 |
|-----------|------------------------|------|
| 枚举名（`name`） | `nameOf(String? v)` | `values.where((e) => e.name == v).firstOrNull` |
| 自定义字段（`value`/`label`…） | `valueOf` / `labelOf` | `values.where((e) => e.<field> == v).firstOrNull` |
| 解析为「未匹配默认值」 | — | 改为返回 `unknown`，或用 `?? .someDefault` |

## 其它方式与坑

- `EnumByName.name`（`values.byName(...)`）：只按 **`name`** 匹配，未匹配会**抛异常**，不满足「可空反查」。
- `values.asNameMap()[v]`：同样仅按 `name`，返回可空，等价 `nameOf` 但不如 `where(...).firstOrNull` 直观 / 可控。
- 手写 `for`/`switch` 匹配：多成员时冗长，且新增成员容易漏改，不推荐。
- 无需 import `package:collection`：`firstOrNull` 是 Dart 3.0 起 `dart:core` 的 `IterableExtensions`，直接可用。
