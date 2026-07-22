---
name: security
description: 安全规范。处理认证授权、敏感数据或安全相关改动时使用。
globs: "**/*{auth,security,crypto}*"
alwaysApply: false
paths:
  - "**/*auth*"
  - "**/*security*"
  - "**/*crypto*"
---
# Security
遵循 OWASP；HTTPS；JWT/OAuth2；输入校验；敏感信息脱敏；密码 BCrypt/Argon2。
