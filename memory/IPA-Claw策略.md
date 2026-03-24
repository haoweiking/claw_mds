# IPA-Claw 策略 - 智能概率套利与情绪波动捕捉

## 核心理念
预测"Polymarket 上的玩家是否在犯错"，而非预测 BTC 会涨到哪里。

## 数据引擎层

### 维度 A：CEX 实盘监控
- Binance BTC/USDT 永续合约 1m 和 5m 线
- CVD (累计成交量增量)
- Funding Rate (资金费率) - 极高时说明多头拥挤

### 维度 B：Polymarket 盘口
- Yes/No 的 Spread
- 隐含概率 = $Price_Yes / (Price_Yes + Price_No)$

### 维度 C：极速情绪分析
- Twitter Top 5 交易员关键词监控

## 核心交易逻辑

### 第一步：偏差探测 (The Edge)
- 理论胜率：CEX 15分钟均线偏差 + CVD 方向
- 市场赔率：Polymarket 价格
- **入场条件：理论胜率 - 市场赔率 > 7%**

### 第二步：寻找价格惯性
- 最佳入场：周期开始后第 2-4 分钟
- 观察价格走势是否与 CEX 成交量一致

### 第三步：执行过滤
- 若出现大额 Liquidations，顺着清算方向下注

## 风控

### 止损规则
- 第 13 分钟若亏损 > 20%，立即止损

### 空仓过滤器
- CEX 波动率低于阈值时自动休眠

### 滑点保护
- 分批入场 (TWAP)
- Gas 暴涨时提高 Gas 费 10%

## 执行指令

### Task: BTC_15M_STRATEGY
```
Monitor: 每 10 秒读取 Binance BTC 永续 5m 线 RSI 和 CVD
Compare: Polymarket BTC-Price-Up 最新成交价

Condition 1 (Long):
- BTC > VWAP 且 CVD 持续上升
- Polymarket_Yes < 0.52
=> 执行 Buy YES

Condition 2 (Contrarian):
- RSI_5m > 80
- 出现大额 Long Liquidation 预警
=> 执行 Buy NO (做空过热)

Risk Control:
- 第 13 分钟亏损 > 20% 立即止损
- 波动率低时休眠
```
