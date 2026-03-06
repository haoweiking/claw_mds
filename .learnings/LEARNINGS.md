# Learnings Log

Captured learnings, corrections, and discoveries. Review before major tasks.

---

## 2026-03-05

### Polymarket CLI Bug
- **Problem**: `polymarket markets list --active true` doesn't show btc-updown markets
- **Solution**: Generate slug manually using timestamp formula `btc-updown-15m-{timestamp}`
- **Pattern**: btc-updown-15m-{unix_timestamp_aligned_to_15min}
- **See Also**: ERRORS.md

### Session Memory
- **Learning**: Must read memory/YYYY-MM-DD.md at session start, otherwise lose context
- **Correction**: User reminded me 3 times before I checked memory
- **Pattern**: Always read today's and yesterday's memory files on session start

### Trading Tools Integration
- **Best Practice**: Built unified trading_tools package with PriceData, KLineData, DeFiData, PolymarketData
- **APIs Working**: CoinGecko, Binance, OKX, Bybit, CryptoCompare, DefiLlama
- **APIs Need Key**: DappRadar, LunarCrush, Arkham

## 2026-03-05

### Trading Knowledge System

**核心策略**:
1. IPA-Claw: 预测市场犯错，偏差>7%入场
2. V-MAC: 趋势+动量+盘口共振

**技术指标**:
- RSI: 超买>70, 超卖<30
- VWAP: 机构成本线  
- EMA: 趋势跟踪
- 订单簿失衡: 订单流信号

**风险管理**:
- 单笔不超2-5%仓位
- 亏损20%必须止损
- 波动率低时停止交易

**数据源已接入**:
- Binance (价格、K线、资金费率)
- DefiLlama (TVL)
- Polymarket (预测市场)

**交易执行**:
- 私钥已配置 (EOA 签名)
- 已实现首次盈利 +$3.01
- 学会了限价单和市价单的区别
