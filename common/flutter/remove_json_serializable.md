---
name: remove_json_serializable
description: >-
  Migrates Dart/Flutter models off json_annotation JsonSerializable to hand-written
  fromJson/toJson. Use when removing @JsonSerializable, deleting *.g.dart, or converting
  code-generated models to manual serialization.
alwaysApply: false
---

# Remove JsonSerializable

Convert `@JsonSerializable` models to plain Dart classes with hand-written `fromJson` / `toJson`. Do **not** keep `json_annotation`, `part '*.g.dart'`, or generated serializers.

## When to use

- User asks to remove `JsonSerializable` / `*.g.dart`
- Migrating an `*_entity.dart` (+ `.g.dart`) to a hand-written model
- Replacing generated `static Foo fromJson` / `_$FooFromJson` with manual mapping

## Workflow

Copy and track:

```
Task Progress:
- [ ] 1. Inventory source + generated mapping
- [ ] 2. Write plain models (no JsonSerializable)
- [ ] 3. Add hand-written fromJson / toJson
- [ ] 4. Swap files / keep import paths stable
- [ ] 5. Update dependents + analyze
```

### 1. Inventory source + generated mapping

Read both:

- Source: `@JsonSerializable`, `@JsonKey(name: ...)`, nested types, mixins
- Generated: `*.g.dart` — **authoritative for JSON key names** (e.g. field `attetionItems` ↔ key `'items'`)

Also find importers:

```bash
rg -n "path/to/foo_entity\.dart|FooEntity\.fromJson" lib --glob '*.dart'
```

### 2. Write plain models (no JsonSerializable)

For every class in the file:

**Remove**

- `import 'package:json_annotation/...'`
- `part '...g.dart';`
- `@JsonSerializable(...)`
- `@JsonKey(...)`
- Generated `static X fromJson(...) => _$XFromJson(...)` / `toJson() => _$XToJson(this)`

**Keep**

- Fields, named constructors, getters, mixins/`@override` members
- Nested type imports that are still needed

Prefer the project's existing hand-written style (named constructor that assigns fields), e.g.:

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

### 3. Add hand-written fromJson / toJson

Rules:

- Mirror **`.g.dart` key names**, not Dart field names when they differ
- Nested objects: `json['x'] == null ? null : Child.fromJson(json['x'] as Map<String, dynamic>)`
- Lists:

```dart
if (json['items'] != null) {
  final array = List<Map<String, dynamic>>.from(json['items'] ?? []);
  items = array.map((e) => Child.fromJson(e)).toList();
}
```

- Numbers: `(json['n'] as num?)?.toInt()` when the field is `int?`
- `toJson` for lists/objects: `?.map((e) => e.toJson()).toList()` / `?.toJson()`
- Do **not** reintroduce `JsonSerializable`

### 4. Swap files / keep import paths stable

Preferred in-place replace (avoids mass import edits):

1. Write the new hand-written content to the **same path** as the old entity (or rename temp → final name the user asked for)
2. Delete `*.g.dart`
3. Delete any temporary `*_model.dart` if it was only a staging file

If the user asks to rename (e.g. `attention_model` → `attetion_entity`):

```bash
rm path/foo_entity.dart path/foo_entity.g.dart
mv path/foo_model.dart path/foo_entity.dart
```

Keep **public class names** stable unless the user explicitly wants renames, so existing `import` / `Foo.fromJson` call sites keep working.

### 5. Update dependents + analyze

```bash
dart analyze path/to/new_or_replaced.dart path/to/importers...
```

Fix only breakages caused by the migration (e.g. `static fromJson` → named constructor is usually call-site compatible as `Foo.fromJson(map)`).

If the project uses graphify, run `graphify update .` after code changes.

## Checklist before done

- [ ] No `json_annotation` / `part '*.g.dart'` / `@JsonSerializable` / `@JsonKey` left on migrated types
- [ ] Every migrated class has hand-written `fromJson` + `toJson`
- [ ] JSON keys match former `.g.dart` (including renamed keys)
- [ ] Old `.g.dart` (and staging files) deleted
- [ ] Importers still resolve; `dart analyze` clean for touched files

## Example (this repo)

Migrating `lib/models/attetion_entity.dart` (+ `.g.dart`):

1. Stage hand-written copy without annotations
2. Port mapping from `attetion_entity.g.dart` (notably `items` ↔ `attetionItems`)
3. Replace entity file with hand-written version; delete `.g.dart`
4. Leave imports as `package:social_fe_app/models/attetion_entity.dart`
