---
name: docker
description: Docker/K8s 规范。编写 Dockerfile、compose 或 K8s 清单时使用。
globs: "**/Dockerfile*,**/docker-compose*.{yml,yaml},**/*.{dockerfile},**/k8s/**/*.yaml"
alwaysApply: false
paths:
  - "**/Dockerfile*"
  - "**/docker-compose*.yml"
  - "**/docker-compose*.yaml"
  - "**/k8s/**"
  - "**/kubernetes/**"
---
# Docker
多阶段构建；非 root；健康检查；资源限制。
