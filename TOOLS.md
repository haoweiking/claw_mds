# TOOLS.md - Local Notes

## Polymarket CLI
- `polymarket events get <slug> -o json` — 获取事件详情
- outcomePrices 是**字符串格式** `'["0.0015","0.9985"]'`，需要 `json.loads()` 再 `float()`
- 价格单位是美元：0.0015 = 0.15¢
- 钱包未配置，只能查询不能实际交易
- 模拟交易在 `memory/poly-portfolio.json` 跟踪

## 监控脚本
- **Elon 监控:** `scripts/elon-monitor.sh` — 纯脚本，不依赖 AI
- **Poly 交易:** `scripts/poly-monitor.py` — 自动执行交易信号，更新 portfolio JSON

## Cron Jobs (2026-03-16 状态)
- **Poly交易监控** — 每30分钟，模型默认，有 delivery.to ✅
- **Elon Tweets监控** — 每30分钟，运行稳定 ✅
- **EigenFlux** — 已禁用（连续27次超时）❌
- **GitHub Trending** — 每天8:30，已修复 delivery.to ✅
- **Poly清仓** — 3/22 20:00 一次性任务 ✅

## 模型选择
- Hunter-Alpha 在 isolated session 中容易超时（>150秒）
- 简单任务用 default 模型即可
- 能用脚本完成的不要让 AI 做

## 投递配置
Telegram 投递必须包含：
```json
{"mode": "announce", "channel": "telegram", "to": "5445067794"}
```
