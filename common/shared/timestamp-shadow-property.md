---
name: timestamp-shadow-property
description: >-
  Adds a string shadow property for int timestamp fields (name + Str / nameStr).
  10-digit = seconds, 13-digit = milliseconds; nil/null/0 → nil/null display string.
  Use when implementing timestamp shadow props, isTimestamp, createdAtStr, or
  Swift/Dart model date string helpers from unix timestamps.
alwaysApply: false
---

# 时间戳影子属性（Swift / Dart 通用）

为 **整型时间戳** 属性生成只读 **字符串影子属性**，便于 UI / 日志展示。Swift 与 Dart 规则一致；实现形态随语言（宏 / 手写 getter / codegen）。

## 何时应用

- 用户提到：时间戳影子属性、`isTimestamp`、`xxxStr`、`createdAtStr`、int → 日期字符串
- 在 JsonCodable / json_model / Freezed / 手写 model 里为时间戳加展示字段

## 铁律（两语言共用）

| 规则 | 约定 |
| --- | --- |
| 源类型 | 有符号/无符号整数族（`Int` / `int` 等）；可选时允许 `null` |
| 影子名 | **属性名 + `Str`**（例：`createdAt` → `createdAtStr`） |
| 影子类型 | **可空字符串**（Swift `String?` / Dart `String?`） |
| 空值 | 源为 `nil`/`null` **或** `0` → 影子返回 `nil`/`null` |
| 10 位整数 | **秒** → `Date(timeIntervalSince1970:)` / `DateTime.fromMillisecondsSinceEpoch(ts * 1000)` |
| 13 位整数 | **毫秒** → 秒 = `ts / 1000`（整数除）后再转日期 |
| 其它位数 | 按 **秒** 处理（与当前 JsonCodable 一致） |
| 展示串 | `Date`/`DateTime` 的默认描述字符串的 **前 19 个字符**（形如 `yyyy-MM-dd HH:mm:ss`） |
| 编解码 | 影子为计算属性，**不参与** JSON encode/decode |

位数用绝对值的十进制位数判断（例：`1725772800` → 10；`1725772800000` → 13）。

## 算法（伪代码）

```text
fn timestampShadow(ts: Int?) -> String? {
  if ts == null || ts == 0 { return null }
  v = abs(ts) as 64-bit
  seconds = (digitCount(v) == 13) ? (ts / 1000.0) : ts   // 秒为 TimeInterval / 再 *1000 给 Dart ms API
  dateText = String(describing: Date from unix seconds)     // Dart: DateTime.toString() 同类描述
  return dateText.prefix(19)
}
```

Dart 注意：`DateTime.fromMillisecondsSinceEpoch` 要毫秒：

- 10 位：`fromMillisecondsSinceEpoch(ts * 1000)`
- 13 位：`fromMillisecondsSinceEpoch(ts)`
- 再 `toString()`（或等价描述）取前 19 字

## Swift

### 标注（JsonCodable）

```swift
@CodingKey("created_at", isTimestamp: true)
let createdAt: Int
// → var createdAtStr: String?
```

- 宏展开宜 **内联** 转换逻辑，避免展开处找不到辅助类型。
- 可选 `Int?`：`guard let ts = createdAt, ts != 0 else { return nil }`
- 非可选：`guard createdAt != 0 else { return nil }`

### 手写等价

```swift
var createdAtStr: String? {
    let ts = createdAt
    guard ts != 0 else { return nil }
    let v = Int64(ts)
    let seconds: TimeInterval = String(Swift.abs(v)).count == 13
        ? TimeInterval(v) / 1000
        : TimeInterval(v)
    return String(String(describing: Date(timeIntervalSince1970: seconds)).prefix(19))
}
```

可选源字段时先 `guard let ts = createdAt, ts != 0`。

## Dart

### 手写 / codegen 等价

```dart
String? get createdAtStr {
  final ts = createdAt;
  if (ts == null || ts == 0) return null;
  final abs = ts.abs();
  final digits = abs.toString().length;
  final DateTime dt = digits == 13
      ? DateTime.fromMillisecondsSinceEpoch(ts)
      : DateTime.fromMillisecondsSinceEpoch(ts * 1000);
  final text = dt.toString(); // 通常含 "yyyy-MM-dd HH:mm:ss.sss"
  return text.length <= 19 ? text : text.substring(0, 19);
}
```

命名与 Swift 对齐：`foo` → `fooStr`。若项目惯用 `foo_str`，仅在用户明确要求时改用 snake_case。

### Freezed / json_serializable

- JSON 只映射整型字段；影子用 **getter**，勿加 `@JsonKey`。
- 代码生成插件若支持注解（如 `@TimestampShadow`），语义须与上表一致。

## 实现检查清单

- [ ] 影子名 = 源属性名 + `Str`
- [ ] 类型为可空 `String` / `String?`
- [ ] `null`/`nil`/`0` → `null`/`nil`
- [ ] 10 位秒、13 位毫秒
- [ ] 展示串长度 19（或源串更短则全长）
- [ ] 不写入 JSON
- [ ] 需要 `Foundation`（Swift）或 `dart:core` `DateTime`（Dart）

## 反例

- 不要把所有 `Int`/`int` 都当时间戳（如 `age`、`id`）——须标注或约定字段
- 不要对影子字段做 encode
- 不要用固定时区格式化替代「描述串前 19 字」，除非用户另行指定 `DateFormat` / `intl`
