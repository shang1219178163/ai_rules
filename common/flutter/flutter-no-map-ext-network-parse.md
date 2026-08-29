---
name: flutter-no-map-ext-network-parse
description: >-
  Use when writing or generating network request / response model parsing
  (网络请求、模型解析、fromJson、fetchResult、fetchModels、map_ext). Do not use
  MapExt helpers from map_ext.dart for request result unwrapping.
globs: "**/*.dart"
alwaysApply: false
paths:
  - "**/*.dart"
---

# 网络请求模型解析禁止使用 map_ext

网络请求拿到响应后，做成功判断与模型解析时，**不要**使用 `lib/extension/map_ext.dart`（`MapExt`）里的脱壳方法：

- `fetchResult`
- `fetchBool`
- `fetchList`
- `fetchModels`

这些是历史 Map 扩展，不作为网络层 / 代码生成的解析约定。

## 正确做法

1. 用 API 的 `fetch()`（或项目既有请求入口）拿到 `Map`。
2. 判断 `code` / `data`；失败时 `debugPrint` 后 `return null`。
3. 成功则用模型的 `fromJson` 解析，例如：

```dart
final map = await api.fetch();
if (map['code'] != 0 || map["data"] == null) {
  debugPrint(["❌" "$this", api.requestUrl, map].join(","));
  return null;
}
return XxxRootModel.fromJson(map);
```

列表在校验 `code`/`data` 后，再从 `data`（或 `data['items']`）取 `List` 并 `fromJson`；失败同样 `debugPrint` 后 `return null`。

## 禁止

- `response.fetchModels(...)` / `response.fetchResult(...)`（Map 扩展）
- 生成代码里依赖 `map_ext.dart` 做模型解析
- 把 MapExt 脱壳当成新业务接口的默认解析路径
