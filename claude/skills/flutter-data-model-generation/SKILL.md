---
name: flutter-data-model-generation
description: Use when generating Flutter/Dart data models from Swagger/OpenAPI JSON (数据模型生成、RootModel、独立 Model、$ref、definitions、响应参数、响应示例、json_to_dart). $ref in definitions → independent XxxModel once (no duplicate across APIs); strip $ref last segment to Chinese+Latin letters only then use as Model name (keep Vo/DTO); Chinese in ref key → translate to English for Model class/file names; then response model from params (priority) or example; sibling imports for refs; never suffix ref models as RootModel; RootModel name/file must not contain detail.
---
@../../../common/flutter/flutter-data-model-generation.md
