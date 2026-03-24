# Proactivity Memory

## Status
status: ongoing
version: 1.0.1
last: 2026-03-16
integration: complete

## Activation Preferences
- 自动激活：心跳检查、任务跟进、上下文恢复
- 安静时段：23:00-08:00（GMT+8）
- 消息风格：简洁，有变化才通知

## Action Boundaries
- 自动执行：文件读取、搜索、内部代码整理
- 先建议：发送消息、定时任务变更
- 必须确认：发邮件、发帖、删除数据、外部操作

## State Rules
- session-state.md：当前任务、上次决策、阻塞项、下一步
- working-buffer.md：长时间或脆弱任务中的临时记录
- 任务完成后刷新状态

## Heartbeat Behavior
- 重新检查：进行中的阻塞、承诺的跟进、过期任务
- 有变化才通知用户
- 无事保持安静

## Notes
- 用户主要用中文交流
- 关注 Polymarket BTC 15min 预测市场
- 机器：haoserver (Linux arm64)

---
*Updated: 2026-03-16*
