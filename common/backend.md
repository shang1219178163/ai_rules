---
description: 后端接口开发规范（最佳实践）
globs:
  - "**/*.java"
  - "**/*.kt"
  - "**/*.go"
  - "**/*.cs"
  - "**/*.js"
  - "**/*.ts"
  - "**/*.py"
alwaysApply: false
---

# 后端接口开发规范

## 角色定位

你是一名资深后端开发工程师。
所有代码必须符合企业级生产环境要求，优先保证：

- 正确性（Correctness）
- 可维护性（Maintainability）
- 可读性（Readability）
- 安全性（Security）
- 可测试性（Testability）
- 可扩展性（Scalability）
- 高性能（Performance）
- 高可观测性（Observability）

不得为了减少代码量而降低代码质量。

---

# 开发原则

必须遵循：

- SOLID 原则
- DRY（Don't Repeat Yourself）
- KISS（Keep It Simple）
- YAGNI（You Aren't Gonna Need It）
- Clean Architecture（整洁架构）
- 分层架构
- 高内聚、低耦合

避免：

- 巨型 Controller
- 巨型 Service
- 巨型工具类
- 循环依赖
- 深层继承
- 重复代码

---

# 项目结构

推荐采用：

Controller
↓
Service
↓
Repository（DAO）
↓
Database

职责明确：

## Controller

仅负责：

- 参数接收
- 参数校验
- 权限校验
- 调用 Service
- 返回统一响应

禁止：

- 编写业务逻辑
- SQL 操作
- 大量 if/else

---

## Service

负责：

- 业务逻辑
- 事务管理
- 聚合多个 Repository
- 调用外部服务

禁止：

- HTTP 请求解析
- 数据库存取细节

---

## Repository

仅负责：

- 数据读写
- SQL
- ORM 操作

禁止：

- 业务逻辑

---

# RESTful API 规范

接口使用 RESTful 风格。

推荐：

GET /users

GET /users/{id}

POST /users

PUT /users/{id}

PATCH /users/{id}

DELETE /users/{id}

禁止：

/getUser

/deleteUser

/queryUser

/doSomething

资源使用名词，不使用动词。

---

# HTTP 状态码

正确使用 HTTP 状态码：

200 OK

201 Created

202 Accepted

204 No Content

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Unprocessable Entity

429 Too Many Requests

500 Internal Server Error

禁止所有请求统一返回 HTTP 200。

---

# 返回格式

统一返回结构：

成功：

{
    "code":0,
    "message":"success",
    "data":{}
}

失败：

{
    "code":1001,
    "message":"参数错误",
    "data":null
}

要求：

- code 为业务状态码
- HTTP 状态码表示请求结果
- message 用户可读
- data 保持固定字段

禁止：

返回格式混乱。

---

# 参数校验

所有外部输入必须校验。

包括：

- 必填项
- 字符串长度
- 数值范围
- 枚举
- 日期格式
- UUID
- Email
- 手机号
- JSON 格式
- 文件类型

任何非法参数立即返回错误。

禁止相信客户端数据。

---

# 异常处理

统一异常处理。

使用全局异常处理器。

禁止：

每个 Controller 写：

try {
}
catch(Exception e){
}

要求：

记录完整日志。

返回统一错误信息。

禁止把异常堆栈返回客户端。

---

# 权限认证

认证(Authentication)与业务逻辑分离。

支持：

- JWT
- OAuth2
- Session
- API Key

禁止：

Service 中解析 Token。

---

# 权限授权

所有接口必须进行权限校验。

禁止仅依赖前端权限。

支持：

RBAC

ABAC

资源拥有者校验

遵循最小权限原则。

---

# 数据库规范

推荐使用 ORM。

复杂 SQL 可使用原生 SQL。

禁止：

SELECT *

必须指定字段。

避免：

- N+1 查询
- 全表扫描
- 重复查询
- 长事务

事务尽量短。

---

# 分页

所有列表接口必须分页。

推荐：

page

pageSize

或：

cursor

大数据推荐 Cursor 分页。

禁止一次返回全部数据。

---

# 查询接口

支持：

过滤(Filter)

排序(Sort)

搜索(Search)

例如：

GET /users?page=1&pageSize=20&name=Tom&status=ACTIVE

---

# 幂等性

以下接口必须支持幂等：

- 支付
- 下单
- 退款
- 创建订单

推荐：

Idempotency-Key

避免重复请求造成重复业务。

---

# 日志规范

必须使用结构化日志。

日志包含：

- requestId
- traceId
- userId
- URI
- Method
- IP
- Status
- Duration

禁止记录：

- 密码
- Token
- Cookie
- Secret
- 身份证
- 银行卡

敏感信息必须脱敏。

---

# 可观测性

系统必须支持：

- Metrics
- Trace
- Health Check
- Readiness
- Liveness

方便监控和排障。

---

# 缓存

合理使用缓存。

支持：

- Redis
- 本地缓存
- CDN

缓存必须设置过期时间。

避免：

- 缓存穿透
- 缓存击穿
- 缓存雪崩

---

# 安全规范

所有接口必须：

使用 HTTPS。

防止：

- SQL 注入
- XSS
- CSRF
- SSRF
- 命令注入
- 路径遍历
- 文件上传漏洞
- 开放重定向

所有 SQL 使用参数化查询。

密码必须加密存储。

推荐：

BCrypt

Argon2

禁止：

MD5

SHA1

---

# 配置管理

配置必须来自：

- 环境变量
- 配置文件
- Secret Manager

禁止：

代码中写死：

数据库密码

Token

Secret

API Key

---

# 文件上传

上传文件必须校验：

- MIME
- 后缀
- 文件大小
- 文件内容

文件名使用随机 UUID。

禁止相信客户端文件名。

---

# 并发处理

避免共享可变状态。

必要时：

- 分布式锁
- 乐观锁
- 悲观锁

避免重复提交。

---

# 异步任务

耗时任务必须异步。

例如：

发送邮件

短信

消息通知

视频转码

图片处理

推荐：

消息队列

后台任务

Job

禁止阻塞 HTTP 请求。

---

# 性能优化

避免：

- N+1 查询
- 重复序列化
- 重复 SQL
- 重复远程调用

合理：

- 批量查询
- 批量写入
- 批量更新

避免过早优化。

---

# API 版本

推荐：

/api/v1/

/api/v2/

重大修改必须升级版本。

禁止破坏兼容性。

---

# DTO 规范

禁止直接返回数据库 Entity。

使用：

Request DTO

Response DTO

View Object（VO）

Domain Model

各层职责分离。

---

# 命名规范

命名必须语义清晰。

推荐：

UserController

UserService

UserRepository

CreateUserRequest

UpdateUserRequest

UserResponse

禁止：

Data

Info

Temp

Test

Util1

Manager2

缩写不明确的名称。

---

# 时间规范

数据库统一使用 UTC 时间存储。

展示时再转换时区。

禁止存储本地时间。

---

# 金额规范

禁止使用：

float

double

金额统一使用：

Decimal

或

最小货币单位（分）。

---

# UUID

分布式系统推荐：

UUID

Snowflake

避免数据库自增 ID 暴露业务规模。

---

# 文档规范

所有接口必须提供：

- 功能说明
- 请求参数
- 返回结果
- 错误码
- 调用示例
- 权限要求

推荐使用 OpenAPI / Swagger 自动生成文档。

---

# 测试规范

必须覆盖：

- 单元测试
- 集成测试
- 接口测试

核心业务逻辑必须有测试。

---

# AI 代码生成要求

AI 生成代码时必须：

- 符合生产环境规范
- 提供完整实现
- 不省略关键逻辑
- 包含必要异常处理
- 包含参数校验
- 考虑边界情况
- 保持代码简洁、可维护、可扩展
- 优先采用行业最佳实践

禁止生成仅用于演示或不可直接运行的代码，除非用户明确要求示例。