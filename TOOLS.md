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

## Cron Jobs (2026-03-27 状态)
- **GitHub Trending** — 每天8:30 ✅ (last run ok)
- **Daily workspace sync** — 每天0:00 CST ✅ (last run ok)
- **Clever Compact** — 每1小时 ✅
- **Poly 周期总结** — 已禁用 (b062c544)
- **Poly交易监控 / Elon监控** — 已移除（不在 cron 列表中）❌

## 模型选择
- Hunter-Alpha 在 isolated session 中容易超时（>150秒）
- 简单任务用 default 模型即可
- 能用脚本完成的不要让 AI 做

## 投递配置
Telegram 投递必须包含：
```json
{"mode": "announce", "channel": "telegram", "to": "5445067794"}
```
