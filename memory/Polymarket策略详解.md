# Polymarket 15分钟交易策略 - 详细版

## 策略核心

### 1. IPA-Claw 策略 (智能概率套利)

**核心理念**: 寻找"市场定价错误"的机会

**入场条件**:
```
理论胜率 - Polymarket价格 > 7%
```

**理论胜率计算**:
1. 获取 Binance 5m K线
2. 计算 RSI(5): 超买>70 超卖<30
3. 计算 VWAP: 价格 > VWAP 偏多
4. 计算 CVD (成交量变化): 上升偏多
5. 综合判断理论概率

### 2. V-MAC 策略 (动量策略)

**核心理念**: 技术面多指标共振

**入场条件**:
- 多头: 价格 > VWAP + EMA9上穿EMA21 + 订单簿失衡>20%
- 空头: 价格 < VWAP + EMA9下穿EMA21 + 订单簿失衡<-20%

---

## 执行流程

### Step 1: 获取数据
```python
# Binance 5m K线
klines = get_binance_kline("BTCUSDT", "5m", 50)

# Polymarket BTC 15m 市场
markets = get_btc_15m_markets()
```

### Step 2: 计算指标
```python
# RSI
rsi = calc_rsi(closes, 5)

# VWAP
vwap = calc_vwap(closes[-15:], volumes[-15:])

# EMA
ema9 = calc_ema(closes, 9)
ema21 = calc_ema(closes, 21)

# 订单簿失衡
ob_imbalance = calc_orderbook_imbalance(orderbook)
```

### Step 3: 判断信号
```python
# Long 信号
if price > vwap and ema9 > ema21 and ob_imbalance > 20 and up_price < 0.58:
    entry("YES")  # 买涨

# Short 信号  
if price < vwap and ema9 < ema21 and ob_imbalance < -20 and down_price < 0.58:
    entry("NO")  # 买跌
```

### Step 4: 执行交易
```python
# 下单
polymarket trade <slug> <outcome> --yes-price <price> --size <amount>
```

### Step 5: 监控与平仓
- 每分钟检查
- 第13分钟若亏损>20%止损
- 结算前平仓

---

## 风险管理

### 仓位
- 单笔: 0.5-1 USDT (账户5U的10-20%)
- 总仓位: 不超过50%

### 止损
- 亏损20%必须平仓
- 不扛单

### 止盈
- 目标收益: 20-50%
- 达到目标可部分平仓

### 过滤器
- 波动率低时停止
- 无明确信号时等待

---

## 当前状态

- 余额: 需要充值
- 监控: 已设置每分钟检查
- 市场: 等待15分钟BTC市场
