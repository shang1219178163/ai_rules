---
name: remove_json_serializable
description: >-
  将 Dart/Flutter 模型从 json_annotation JsonSerializable 迁移为手写 fromJson/toJson。
  在移除 @JsonSerializable、删除 *.g.dart，或把代码生成模型改为手动序列化时使用。
alwaysApply: false
---

# 移除 JsonSerializable

把 `@JsonSerializable` 模型改成带手写 `fromJson` / `toJson` 的普通 Dart 类。**不要**保留 `json_annotation`、`part '*.g.dart'` 或生成序列化器。

## 何时使用

- 用户要求移除 `JsonSerializable` / `*.g.dart`
- 将 `*_entity.dart`（+ `.g.dart`）迁到手写模型
- 用手动映射替换生成的 `static Foo fromJson` / `_$FooFromJson`

## 工作流

复制并勾选进度：

```
Task Progress:
- [ ] 1. 盘点源文件与生成映射
- [ ] 2. 写普通模型（无 JsonSerializable）
- [ ] 3. 补全手写 fromJson / toJson
- [ ] 4. 替换文件 / 保持 import 路径稳定
- [ ] 5. 更新引用方 + analyze
```

### 1. 盘点源文件与生成映射

同时阅读：

- 源文件：`@JsonSerializable`、`@JsonKey(name: ...)`、嵌套类型、mixin
- 生成文件：`*.g.dart` — **JSON key 名称以它为准**（例如字段 `attetionItems` ↔ key `'items'`）

并查找引用方：

```bash
rg -n "path/to/foo_entity\.dart|FooEntity\.fromJson" lib --glob '*.dart'
```

### 2. 写普通模型（无 JsonSerializable）

对文件中每个类：

**删除**

- `import 'package:json_annotation/...'`
- `part '...g.dart';`
- `@JsonSerializable(...)`
- `@JsonKey(...)`
- 生成式 `static X fromJson(...) => _$XFromJson(...)` / `toJson() => _$XToJson(this)`

**保留**

- 字段、命名构造、getter、mixin / `@override` 成员
- 仍需要的嵌套类型 import

优先贴合项目既有手写风格（命名构造里赋值字段），例如：

```dart
class Foo {
  int? code;
  String? msg;

  Foo({this.code, this.msg});

  Foo.fromJson(Map<String, dynamic> json) {
    code = (json['code'] as num?)?.toInt();
    msg = json['msg'] as String?;
  }

  Map<String, dynamic> toJson() {
    return {
      'code': code,
      'msg': msg,
    };
  }
}
```

### 3. 补全手写 fromJson / toJson

规则：

- 对齐 **`.g.dart` 的 key 名**；字段名与 key 不一致时以 key 为准
- 嵌套对象：`json['x'] == null ? null : Child.fromJson(json['x'] as Map<String, dynamic>)`
- 列表：

```dart
if (json['items'] != null) {
  final array = List<Map<String, dynamic>>.from(json['items'] ?? []);
  items = array.map((e) => Child.fromJson(e)).toList();
}
```

- 数字：字段为 `int?` 时用 `(json['n'] as num?)?.toInt()`
- `toJson` 中列表/对象：`?.map((e) => e.toJson()).toList()` / `?.toJson()`
- **不要**重新引入 `JsonSerializable`

### 4. 替换文件 / 保持 import 路径稳定

优先原地替换（减少大面积改 import）：

1. 把手写内容写到与旧 entity **相同路径**（或按用户要求 rename temp → 最终名）
2. 删除 `*.g.dart`
3. 若临时 `*_model.dart` 仅作中转，一并删除

若用户要求改名（如 `attention_model` → `attetion_entity`）：

```bash
rm path/foo_entity.dart path/foo_entity.g.dart
mv path/foo_model.dart path/foo_entity.dart
```

除非用户明确要求改名，否则保持 **公共类名** 稳定，使既有 `import` / `Foo.fromJson` 调用点继续可用。

### 5. 更新引用方 + analyze

```bash
dart analyze path/to/new_or_replaced.dart path/to/importers...
```

只修迁移引入的破坏（例如 `static fromJson` → 命名构造，调用点通常仍可写 `Foo.fromJson(map)`）。

若项目使用 graphify，改码后执行 `graphify update .`。

## 完成前检查

- [ ] 已迁移类型上无 `json_annotation` / `part '*.g.dart'` / `@JsonSerializable` / `@JsonKey`
- [ ] 每个已迁移类都有手写 `fromJson` + `toJson`
- [ ] JSON key 与原 `.g.dart` 一致（含重命名 key）
- [ ] 旧 `.g.dart`（及中转文件）已删除
- [ ] 引用方可解析；触及文件 `dart analyze` 干净

## 示例（本仓库）

迁移 `lib/models/attetion_entity.dart`（+ `.g.dart`）：

1. 先写无注解的手写副本
2. 从 `attetion_entity.g.dart` 移植映射（注意 `items` ↔ `attetionItems`）
3. 用手写版本替换 entity；删除 `.g.dart`
4. import 仍保持 `package:social_fe_app/models/attetion_entity.dart`
