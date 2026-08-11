---
name: mq
description: 消息队列规范。编写生产者、消费者或 MQ 配置时使用。
globs: "**/*{mq,queue,consumer,producer,kafka,rabbit}*"
alwaysApply: false
paths:
  - "**/*mq*"
  - "**/*queue*"
  - "**/*consumer*"
  - "**/*producer*"
  - "**/*kafka*"
  - "**/*rabbit*"
---
# MQ
保证幂等；重试；死信队列；顺序性；消息可追踪。
