---
name: timestamp-shadow-property
description: >-
  Adds a string shadow property for int timestamp fields (name + Str / nameStr).
  10-digit = seconds, 13-digit = milliseconds; nil/null/0 → nil/null display string.
  Use when implementing timestamp shadow props, isTimestamp, createdAtStr, or
  Swift/Dart model date string helpers from unix timestamps.
alwaysApply: false
---

# 时间戳影子属性（Swift / Dart）

为 **整型时间戳** 属性生成只读 **字符串影子属性**。规则跨语言一致；下方按语言给完整代码示例。

## 何时应用

- 时间戳影子属性、`isTimestamp`、`xxxStr`、`createdAtStr`、int → 日期字符串
- JsonCodable / Freezed / json_serializable / 手写 model

## 共用规则

| 规则 | 约定 |
| --- | --- |
| 影子名 | 属性名 + `Str`（`createdAt` → `createdAtStr`） |
| 影子类型 | 可空字符串（`String?`） |
| 空值 | 源为 `nil`/`null` 或 `0` → 返回 `nil`/`null` |
| 10 位 | **秒** |
| 13 位 | **毫秒** |
| 其它位数 | 按 **秒** |
| 展示串 | 日期默认描述的 **前 19 字符**（`yyyy-MM-dd HH:mm:ss`） |
| JSON | 影子不参与编解码 |

位数 = `abs(ts)` 的十进制位数。

---

## Swift 示例

### JsonCodable 标注

```swift
import Foundation
import JsonCodable

@Codable
struct Event {
    @CodingKey("created_at", isTimestamp: true)
    let createdAt: Int

    @CodingKey("updated_at", isTimestamp: true)
    let updatedAt: Int?
}
// 宏生成：
// var createdAtStr: String?  // 0 → nil
// var updatedAtStr: String?  // nil 或 0 → nil
```

宏展开宜 **内联** 转换逻辑，避免展开处找不到辅助类型。

### 手写：非可选 Int

```swift
import Foundation

struct Event {
    let createdAt: Int

    var createdAtStr: String? {
        let ts = createdAt
        guard ts != 0 else { return nil }
        let v = Int64(ts)
        let seconds: TimeInterval = String(Swift.abs(v)).count == 13
            ? TimeInterval(v) / 1000
            : TimeInterval(v)
        return String(String(describing: Date(timeIntervalSince1970: seconds)).prefix(19))
    }
}
```

### 手写：可选 Int?

```swift
var updatedAtStr: String? {
    guard let ts = updatedAt, ts != 0 else { return nil }
    let v = Int64(ts)
    let seconds: TimeInterval = String(Swift.abs(v)).count == 13
        ? TimeInterval(v) / 1000
        : TimeInterval(v)
    return String(String(describing: Date(timeIntervalSince1970: seconds)).prefix(19))
}
```

### 可复用辅助（可选）

```swift
enum TimestampShadow {
    static func string(from ts: Int?) -> String? {
        guard let ts, ts != 0 else { return nil }
        let v = Int64(ts)
        let seconds: TimeInterval = String(Swift.abs(v)).count == 13
            ? TimeInterval(v) / 1000
            : TimeInterval(v)
        return String(String(describing: Date(timeIntervalSince1970: seconds)).prefix(19))
    }
}

// var createdAtStr: String? { TimestampShadow.string(from: createdAt) }
```

---

## Dart 示例

### 手写 model（非空 int）

```dart
class Event {
  Event({required this.createdAt});

  final int createdAt;

  String? get createdAtStr {
    final ts = createdAt;
    if (ts == 0) return null;
    final digits = ts.abs().toString().length;
    final dt = digits == 13
        ? DateTime.fromMillisecondsSinceEpoch(ts)
        : DateTime.fromMillisecondsSinceEpoch(ts * 1000);
    final text = dt.toString();
    return text.length <= 19 ? text : text.substring(0, 19);
  }
}
```

### 手写 model（可空 int?）

```dart
class Event {
  Event({this.updatedAt});

  final int? updatedAt;

  String? get updatedAtStr {
    final ts = updatedAt;
    if (ts == null || ts == 0) return null;
    final digits = ts.abs().toString().length;
    final dt = digits == 13
        ? DateTime.fromMillisecondsSinceEpoch(ts)
        : DateTime.fromMillisecondsSinceEpoch(ts * 1000);
    final text = dt.toString();
    return text.length <= 19 ? text : text.substring(0, 19);
  }
}
```

### 可复用辅助（可选）

```dart
String? timestampShadowString(int? ts) {
  if (ts == null || ts == 0) return null;
  final digits = ts.abs().toString().length;
  final dt = digits == 13
      ? DateTime.fromMillisecondsSinceEpoch(ts)
      : DateTime.fromMillisecondsSinceEpoch(ts * 1000);
  final text = dt.toString();
  return text.length <= 19 ? text : text.substring(0, 19);
}

// String? get createdAtStr => timestampShadowString(createdAt);
```

### Freezed / json_serializable

```dart
@freezed
class Event with _$Event {
  const Event._();
  const factory Event({
    @JsonKey(name: 'created_at') required int createdAt,
    @JsonKey(name: 'updated_at') int? updatedAt,
  }) = _Event;

  /// 不写 @JsonKey；不参与序列化
  String? get createdAtStr => timestampShadowString(createdAt);
  String? get updatedAtStr => timestampShadowString(updatedAt);

  factory Event.fromJson(Map<String, dynamic> json) => _$EventFromJson(json);
}
```

命名与 Swift 对齐：`foo` → `fooStr`。仅当用户明确要求时再用 `foo_str`。

---

## 检查清单

- [ ] 影子名 = 源名 + `Str`
- [ ] 类型 `String?`
- [ ] `nil`/`null`/`0` → `nil`/`null`
- [ ] 10 位秒、13 位毫秒
- [ ] 展示串前 19 字
- [ ] 不写入 JSON
- [ ] Swift 需 Foundation；Dart 用 `DateTime`

## 反例

- 勿把所有 `Int`/`int` 当时间戳（如 `age`、`id`）
- 勿对影子字段 encode
- 勿擅自换成固定 `DateFormat`/`intl`，除非用户指定
