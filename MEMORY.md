# MEMORY.md

## 2026-03-26 当前持仓 (22:09 CST)
- **BTC $1M GTA VI YES**: 308股 @ $0.4865 → 当前约 $0.10，浮亏严重 ⚠️
- **BitBoy YES**: 1449股 @ $0.088
- 现金: ~$1000.16
- Clever Compact cron job ID: `89c2778e-f61b-4de9-aad3-f4146937301f`

## 2026-03-24 更新
- ✅ **Sweden NO 平仓**：448股 @ $0.67 平出，收回 $300.16，盈利 +$0.16
- 原因: NO 67¢ > 55¢ 止盈线，市场过度悲观
- 当前状态: 空仓，现金 $1000.16，总收益 +$0.16 (+0.02%)
- 监控市场: Tampa Bay YES, Carolina YES, Italy YES

## 2026-03-22 更新
- ✅ **模拟交易完成**：最终价值 $12.14，收益 +$2.14 (+21.4%)
- 平仓时间：20:00 北京时间
- 全部持仓已平仓，状态 closed
- 交易统计：89笔交易，2笔盈利
- ⚠️ **EigenFlux 已禁用**：连续27次超时

## User
- **AZ (Ken)**: Telegram 5445067794, timezone UTC
- Focus: Polymarket BTC 15min prediction markets

## Polymarket
- CLI available, can check prices ✅, can't trade for user ❌
- Redemption: buy → hold → settle → `polymarket ctf redeem --condition-id <ID>`
- Balance: ~$2.15 USDC

## Tech
- Machine: haoserver (Linux arm64)
- 2026-03-07: Fixed monitor script (5m→15m)
- 2026-03-12: Cleaned workspace for lower token usage

## Lesson
- Don't over-question; check links directly
- Web fetch blocked; polymarket CLI works
- Google News RSS = huge content; be specific when searching
- **AI 不要算数字** — outcomePrices 是 JSON 字符串，用 Python 脚本算
- **区间投注看主峰** — 投市场共识区间，别赌尾部事件
- **delivery.to 必须配置** — 所有 Telegram cron job
- **能用脚本别用 AI** — isolated session 容易超时
- **区分浮盈/实盈** — 持仓更新标注清楚
- **EigenFlux 禁用** — 连续超时已关闭
