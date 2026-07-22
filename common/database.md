---
name: database
description: 数据库规范。编写 SQL、ORM 或数据访问层时使用。
globs: "**/*.{sql,prisma}"
alwaysApply: false
paths:
  - "**/*.sql"
  - "**/*repository*"
  - "**/*dao*"
  - "**/migrations/**"
  - "**/*.prisma"
---
# Database
避免 SELECT *；合理索引；事务最小化；防 N+1；参数化 SQL；分页查询。
