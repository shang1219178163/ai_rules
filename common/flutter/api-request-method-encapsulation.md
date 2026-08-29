---
name: api-request-method-encapsulation
description: >-
  Use when writing or generating API request methods that fetch and parse models
  (api请求方法封装、网络请求、模型解析、fromJson、Provider request、BaseRequestAPI、
  rootModel). Api 方法名 request()；类顶注释声明解析模型；Provider 去前缀命名；
  参数必传跟随 Api；生成一律返回 RootModel；no map_ext；return via result；
  follow debugPrint null template.
alwaysApply: false
---

# api请求方法封装

单接口的「发请求 + 成功判断 + 模型解析」应封装成可复用方法（Api 内为 `request()`，同前缀 Provider 为去前缀后的 `requestXxx`）。Provider / 页面只做状态与编排，不散落 `Map` 脱壳。

## 职责边界

| 放这里 | 不放这里 |
|--------|----------|
| `fetch()`、判断 `code`/`data`、`fromJson` | Toast、路由、分页合并、跨接口编排 |
| 失败时 `debugPrint` 后 `return null` | `map_ext` 的 `fetchResult` / `fetchModels` 等 |
| 成功时整包 `rootModel` | 手拆 `map['data']` / `items` 再 map |

## 与「创建数据模型」的关系

请求方法 / Provider **仅在打开「创建数据模型」时生成**。关闭时只产出 Api 壳，不注入 `request()`、不生成 Provider。

配置开关「在 API 中解析模型」（依赖已打开创建数据模型）：

| 开关 | 策略 | 产物 |
|------|------|------|
| 打开 | `SwaggerApiRequestParseStrategy` | Api 实现 `request()`；Provider 委托 `await api.request()` |
| 关闭 | `SwaggerProviderRequestParseStrategy` | Api 不变；Provider 内完整 fetch+解析 |

生成的请求方法**一律返回整包 RootModel**（`Future<XxxRootModel?>`）。列表 / 分页由调用方取 `root?.data` 或 `root?.data?.items`。

## 命名

- **Api**：固定 `request()`（无方法参数）。
- **Provider**：`request` + Api 基名去掉与文件去 `Provider` 后相同的前缀。  
  - `CustomerProvider` + `CustomerApplyInfoApi` → `requestApplyInfo`  
  - 去前缀后为空 → `request`  
  - 组内撞名：优先保留 `V*`（`requestApply` / `requestV2Apply`），仍冲突则数字后缀。

## Provider 参数（跟随 Api 属性）

带上 Api 全部构造参数（跳过 header；消歧；按名排序），必传跟随 `isRequired`，并传入 `XxxApi(...)`。

```dart
Future<CustomerApplyInfoRootModel?> requestApplyInfo({
  required int? id,
  int? type,
}) async {
  final api = CustomerApplyInfoApi(
    id: id,
    type: type,
  );
  final result = await api.request();
  return result;
}
```

## Import

- Provider：`package:flutter/foundation.dart`（ChangeNotifier / debugPrint）+ `../api/…` + `../model/…`
- Api 宿主 `request()`：`package:flutter/foundation.dart` + `../model/xxx_root_model.dart`

## Api 类顶部注释（铁律）

**创建 Api（无论是否打开「创建数据模型」）**：`class` 与 constructor 上方均须写接口 `summary`（`/// $summary`；空则省略）。

打开「创建数据模型」后，类顶在 summary 之外另加 **解析模型 / 关联模型**（`ensureApiClassModelDoc` 会整段替换类顶 `///`，仍含 summary）：

```dart
/// 查询申请信息
///
/// 解析模型：BracketRootModel
/// 关联模型：BracketRootRefModel
class BracketApi extends BaseRequestAPI {
  /// 查询申请信息
  BracketApi({ ... });
```

（仅 Api 时类顶与 constructor 各一行 summary；打开创建数据模型后类顶扩展为上例。）
| 行 | 规则 |
|----|------|
| 类顶 `/// summary` | **凡创建 Api 必有**（`mergeApiContent`；空则省略） |
| constructor 上 `/// summary` | **凡创建 Api 必有**（`mergeApiContent`；空则省略） |
| `解析模型：` / `关联模型：` | 仅打开「创建数据模型」时由 `ensureApiClassModelDoc` 写入 |

实现：`SwaggerApiGenerator.mergeApiContent`（class + constructor summary）；`SwaggerRequestMethodBuilder.ensureApiClassModelDoc` + `resolveFirstLevelRelatedModelClassNames`（模型注释）。

## 铁律

1. Api 方法名 `request()` 且无参数。
2. Provider 方法名去掉与文件去 Provider 后相同的前缀；组内消歧。
3. Provider 参数必传跟随 Api 属性必传。
4. 禁止 map_ext 脱壳。
5. `final rootModel = XxxRootModel.fromJson(map);`
6. 生成代码：`final result = rootModel; return result;`（委托：`final result = await api.request(); return result;`）。
7. 手写若返回内部字段：`final result = rootModel.属性; return result;`。
8. 失败：`debugPrint(["❌" "$this", requestUrl, map].join(","));` 后 `return null`（Provider 用 `api.requestUrl`）。
9. Api 类顶部注释声明 `解析模型：XxxRootModel`；`关联模型` 仅一级独立 Model（不列嵌套）。
10. `requestType` **必须**与接口 HTTP 方法一致：`HttpMethod get requestType => HttpMethod.GET|POST|PUT|…`（取自 paths 的 method 键，**禁止**一律写成 `POST`）。实现：`mergeApiContent` / `applyRequestUriAndMethod`（`endpoint.method.label`）。

## 禁止：map_ext

不用 `fetchResult` / `fetchBool` / `fetchList` / `fetchModels`。

## Api 模板

```dart
Future<CustomerApplyInfoRootModel?> request() async {
  final map = await fetch();
  if (map['code'] != 0 || map["data"] == null) {
    debugPrint(["❌" "$this", requestUrl, map].join(","));
    return null;
  }
  final rootModel = CustomerApplyInfoRootModel.fromJson(map);
  final result = rootModel;
  return result;
}
```

## 打包目录

| 类型 | zip 内路径 |
|------|------------|
| Api | `api/*.dart` |
| RootModel | `model/*.dart` |
| Provider | `provider/*.dart` |

- zip 一律按 kind 分目录，并写显式目录项。
- 打开「创建数据模型」→ api+model+provider → 强制 zip；仅 api → 按批量阈值。
- 同前缀 Api 合并到同一 Provider 文件。

## 其它

- 模型类名标准 PascalCase（粘连词如 `customerbalance` → `CustomerBalance`）。
- **模型类名不要包含 Vo / DTO**：生成时去掉末尾 `Vo`/`VO`/`Dto`/`DTO`（可叠加，如 `UserVoDTO` → `User`）；`UserVoApi` → `UserRootModel`。
- **数据模型生成顺序与独立 Model**：见 `flutter-data-model-generation`（先 `$ref`→`XxxModel` 去重，再响应参数/示例→RootModel，同级 import）。
- **Api 顶部模型注释**：见上文「Api 类顶部注释」；与 `ensureApiClassModelDoc` 一致。
