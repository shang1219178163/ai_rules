---
name: flutter-data-model-generation
description: >-
  Use when generating Flutter/Dart data models from Swagger/OpenAPI JSON
  (数据模型生成、RootModel、独立 Model、$ref、definitions、响应参数、响应示例、json_to_dart).
  $ref in definitions → independent XxxModel once (no duplicate across APIs);
  strip $ref last segment to Chinese+Latin letters only then use as Model name (keep Vo/DTO);
  Chinese in ref key → translate to English for Model class/file names;
  then response model from params (priority) or example; sibling imports for refs;
  never suffix ref models as RootModel; RootModel name/file must not contain detail.
alwaysApply: false
---

# Flutter 数据模型生成

从 Swagger / OpenAPI JSON 生成 Dart 数据模型时遵循本 skill（与 web_tool Swagger 生成、`json_to_dart` 一致）。

## 生成顺序（铁律）

生成模型时，根据 JSON 文件先将 **响应 schema 树中 `$ref` 指向、且 `definitions` 中存在的定义** 做成独立模型，然后再根据 响应参数（优先级） 或响应示例（其次）生成包络模型；需要引用这些定义时同级导入。独立模型后缀是 **Model**（不是 RootModel，也不是 DetailModel）。`$ref` 指向的键不在 `definitions` 中、或只有 `originalRef` 没有 `$ref` 的，不生成独立文件。准入只看 **`$ref`**（`#/definitions/` 后的键），不看 `originalRef` 字段。

| 步骤 | 输入 | 产物 |
|------|------|------|
| 1 | 响应树中：有 `$ref` **且** `definitions` 含该键 | 每个定义一个独立 `.dart`：**`XxxModel`** |
| 2 | 响应参数（优先）或响应示例（其次） | 接口包络：**`XxxRootModel`**（由 Api 类名推导，如 `FooApi` → `FooRootModel`） |
| 3 | RootModel / 独立 Model 字段类型若对应某已收录 `$ref` | **同级** `import 'yyy_model.dart';`，不在本文件内嵌套重复 class |

## `$ref` / definitions 去重（铁律）

- `definitions` 里同一个键（`$ref` 末段）在 **整次批量生成 / zip** 中只产出 **一份** 独立 Model 文件。
- 多个接口共用同一 `$ref` 时：第一次生成后记入已输出集合；后续接口 **不再重复生成** 该 Model，但仍按同一类名做同级 import。
- 类名按 definitions 键全局稳定（跨接口共用同一 `XxxModel` 名）。
- RootModel 仍按接口各一份（包络可不同）；去重只针对独立 Model（definitions 实体）。

## 命名

- **RootModel**：仅响应包络（Api 名推导）。例：`CustomerApplyInfoApi` → `CustomerApplyInfoRootModel` → `customer_apply_info_root_model.dart`。Api 基名仍可去掉 Vo/DTO。
- **独立 Model**：由 `$ref` → definitions 键推导。例：`MatchUpVO` → **`MatchUpVOModel`** → `match_up_vo_model.dart`（`VO` 整段为 `_vo_`，不是 `_v_o_`）。
- **禁止**：给 definitions 模型加 `RootModel` 后缀；**禁止**再用 `DetailModel` 作为独立模型后缀。
- **基名以 `Root` 结尾**：为避免与包络 `XxxRootModel` 同形，独立模型用 **`XxxRootRefModel`**（例：`BracketRoot` → `BracketRootRefModel`，不是 `BracketRootModel`）。
- **Root 与 Detail 不得共存（铁律）**：任意模型**类名 / 文件名**中不得同时出现 `Root` 与 `Detail`（禁止 `RootDetailModel`、`DetailRootModel`、`FooRootBarDetail…`）。
  - 共存时：**去掉 Detail，保留 Root**（Pascal 段匹配；勿误伤 `Room`）。
  - 仅含 `Detail`、不含 `Root`：允许（如译文「详情」→ `MatchLiveRoomDetailModel`）。
  - RootModel 路径：`stripDetailFromRootModelBase` 一律去掉 Detail（无 `…DetailRootModel` / `…_detail_root_model`）。
  - 独立 Model 路径：词库与 `$ref` 键应避免产出同时含 Root+Detail 的基名；人工/AI 审名时按本条纠正。
- **RootModel 不能包含 detail 关键字**（类名 / 文件名均不可）。路径段如 `/detail` 进入 Api 名（`MatchLivesRoomDetailApi`）时 → `MatchLivesRoomRootModel`。

### 独立模型保留 Vo / DTO（铁律）

独立 Model 的**类名与文件名不得**去掉 `Vo` / `VO` / `Dto` / `DTO`（不要对独立 Model 调用 `stripModelTypeSuffix`）。

文件名反驼峰时，`VO`/`DTO` 等连续大写缩写视为一段：`AliFaceInitVOModel` → `ali_face_init_vo_model.dart`（**禁止** `ali_face_init_v_o_model`）。实现依赖 `String.toUncamlCase` 的缩写感知拆分。

| 输入（definitions / 内层纯名） | 正确 | 错误 |
|--------------------------------|------|------|
| `MatchUpVO` | `MatchUpVOModel` / `match_up_vo_model.dart` | `MatchUpModel` / `MatchUpVODetailModel` / `match_up_v_o_model` |
| `AliFaceInitVO` | `AliFaceInitVOModel` / `ali_face_init_vo_model.dart` | `ali_face_init_v_o_model.dart` |
| `LiveSearchRoomItemVO` | `LiveSearchRoomItemVOModel` | `LiveSearchRoomItemModel` / `…DetailModel` |
| `QueryDTO` | `QueryDTOModel` / `query_dto_model.dart` | `QueryModel` / `QueryDTODetailModel` |

对比：RootModel（由 Api 名推导）以及 json_to_dart **嵌套类**路径仍可剥 Vo/DTO；**仅独立 Model 文件/类名除外**。

### `$ref` 含中文时的独立模型名（铁律）

`$ref` 末段（definitions 键）若含汉字：**将中文译为英文**后再拼独立模型名（保留原有拉丁 / Vo/DTO 段）。

| `$ref` / definitions 键 | 译文基名 | 类名 / 文件名 |
|-------------------------|----------|----------------|
| `比赛直播间详情` | `MatchLiveRoomDetail` | `MatchLiveRoomDetailModel` / `match_live_room_detail_model.dart` |
| `#/definitions/比赛直播间详情` | 同上 | 同上 |
| `R«比赛直播间详情»` | `RMatchLiveRoomDetail` | `RMatchLiveRoomDetailModel` |
| `关注列表VO` | `FollowListVO` | `FollowListVOModel` |
| `AnchorTopVO对象` | `AnchorTopVOObject` | `AnchorTopVOObjectModel` |

实现：`SwaggerChineseRefTranslator.translateHanRuns`（离线词库最长匹配）→ `resolveRefClassName`。  
definitions **查找 / 去重**仍用完整中文键；仅 **类名 / 文件名** 用译文。

### `$ref` 含特殊符号时的独立模型名（铁律）

`$ref` **末段**经 `extractPlainRefToken` 后**只含中文与英文字母**（去掉 `«»`/`<>`、数字、下划线、逗号等一切非中英文字符）；剩余整段作为基名（可再经中文翻译；**保留** Vo/DTO，再加 `Model`）。不要只取括号内层。

| `$ref` / definitions 键 | 纯中英末段 | 类名 / 文件名 |
|-------------------------|------------|----------------|
| `CursorPageVO«LiveSearchRoomItemVO»` | `CursorPageVOLiveSearchRoomItemVO` | `CursorPageVOLiveSearchRoomItemVOModel` / `cursor_page_vo_live_search_room_item_vo_model.dart` |
| `R«CursorPageVO«LiveCardVO»»` | `RCursorPageVOLiveCardVO` | `RCursorPageVOLiveCardVOModel` |
| `R«Map«string,Item»»` | `RMapstringItem` | `RMapstringItemModel` |
| `MatchUpVO`（已是纯英文） | `MatchUpVO` | `MatchUpVOModel` |

实现：`extractPlainRefToken`（取 `/` 后末段 + `[^A-Za-z\u4e00-\u9fff]` 剔除）→ 中文翻译 → `resolveRefClassName`（**不**调用 `stripModelTypeSuffix`；后缀固定 `Model`）。  
注意：definitions **查找 / 去重**仍用完整键；仅 **类名 / 文件名** 用规范化串。同名冲突时仍走既有 `_uniqueRefClassName`。

## 响应 JSON 来源优先级

1. **响应参数**展开拼装的 JSON（schema 字段树）。
2. 否则用 **响应示例**（literal example → schema 占位示例）。

有多份候选时按上述顺序尝试，直到 `json_to_dart` 生成成功。

## 同级导入改写

1. 解析时记录：`$ref` → definitions 键 → 示例 JSON，以及 JSON 路径 → 该键（如 `/data` → `BracketRoot`）。
2. 生成 RootModel / 某独立 Model 后：将 json_to_dart 按字段名生成的嵌套类名，改写成对应的 `*Model`。
3. 从本文件删除已改为外部类型的 class 定义，并添加同级 import。
4. **只 import 当前模型实际用到的文件**：
   - **RootModel**：仅改写/导入**一级**路径上的 `$ref`（路径深度 1，如 `/data`）；不把 `/data/brackets` 等嵌套模型写进 RootModel import。
   - **独立 Model**：仅改写**直接子** `$ref` 字段；更深嵌套由子 Model 自行导入。
5. Api 顶部「关联模型」与 RootModel 一级规则一致，不罗列深层独立 Model。

实现：`_buildGeneratorToRefRenames`（仅 depth==1）、`_buildDirectChildRefRenames`、`_wireSiblingRefImports`（按改写结果收集 `usedImports`）。

## 与请求封装的关系

- 打开「创建数据模型」才生成 model（及 request / Provider）；见 `api-request-method-encapsulation`。
- 请求方法返回整包 **RootModel**；业务字段 / 列表项类型可为 **独立 Model**。
- zip：`model/` 下同时可有 `*_root_model.dart` 与多个 `*_model.dart`（同一 definitions 键不会出现 `_1`/`_2` 重复）。

## 实现锚点（web_tool）

- 收集 refs：`Swagger2DocumentParseStrategy` → `responseRefExamples` / `responseRefPaths`（仅 `$ref` ∈ definitions）
- 命名：`SwaggerDartIdentifier.resolveRefClassName`（独立 Model；含中文翻译）、`resolveRootModelClassName`（RootModel）
- 中文：`SwaggerChineseRefTranslator`（definitions 键汉字 → 英文标识符）
- 生成：`SwaggerApiGenerator.generateModels`（先独立 Model 后 Root + 同级 import；`sharedRefNameToClass` / `emittedDetailRefs` 跨接口去重）
- 批量：`SwaggerApiBatchDownload.generateFiles` 传入共享集合，避免重复落盘

## 检查清单

- [ ] `$ref` 含汉字时独立 Model 名用英文译文（如 `比赛直播间详情` → `MatchLiveRoomDetailModel`）
- [ ] `$ref` 含 `«»` 时独立 Model 名为**移除特殊符号后的整段**且保留 VO/DTO（如 `CursorPageVO«LiveSearchRoomItemVO»` → `CursorPageVOLiveSearchRoomItemVOModel`）
- [ ] 仅 `$ref` 指向且 `definitions` 有键的定义已先生成独立 Model（不依赖 `originalRef` 字段）
- [ ] 同一 definitions 键在批量输出中只出现一次独立 Model（无 `xxx_model_1` 重复）
- [ ] RootModel 来源：响应参数优先，其次响应示例
- [ ] definitions 模型类名以 `Model` 结尾（**不是** `DetailModel` / `RootModel`）；独立模型**不**剥 Vo/DTO
- [ ] RootModel 类名 / 文件名不含 `detail`（无 `…DetailRootModel` / `…_detail_root_model`）
- [ ] 任意模型名无 `Root`+`Detail` 共存（无 `RootDetailModel` 等）；RootModel 已去 Detail；独立名按 skill 审
- [ ] RootModel / 独立 Model 只 import 直接需要的独立 Model（Root 仅一级路径；独立 Model 仅直接子）
- [ ] Api「关联模型」仅一级独立 Model，不含嵌套
- [ ] RootModel / 嵌套生成路径可去 Vo/DTO；**独立 Model 文件名/类名除外**
- [ ] 文件名中 `VO`/`DTO` 整段为 `_vo_`/`_dto_`（非 `_v_o_`）
