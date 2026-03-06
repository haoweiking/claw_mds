# 交易工具集

## 已接入 ✅

### 价格数据
| 数据源 | 状态 | 用途 |
|--------|------|------|
| CoinGecko | ✅ OK | 币种价格、市值、图表 |
| Binance | ✅ OK | 现货/合约价格、K线 |
| OKX | ✅ OK | 合约价格、深度 |
| Bybit | ✅ OK | 合约价格、持仓 |
| CryptoCompare | ✅ OK | 多交易所价格聚合 |

### DeFi 数据
| 数据源 | 状态 | 用途 |
|--------|------|------|
| DefiLlama | ✅ OK | TVL、链上数据 |

### 预测市场
| 数据源 | 状态 | 用途 |
|--------|------|------|
| Polymarket | ✅ OK | BTC 15分钟预测 |

## 待接入 (需要 API Key) 🔶

### 需要申请
- DappRadar - DApp 排名数据
- LunarCrush - 社交情绪分析
- Arkham - 链上巨鲸追踪
- CoinMarketCap - 行情数据

### 需要配置
- Binance/OKX/Bybit 交易 API - 自动下单

## 使用示例

```python
# 价格查询
from trading_tools import price

btc = price.get('bitcoin')
eth = price.get('ethereum')

# DefiLlama
from trading_tools import defi

tvl = defi.get_chain_tvl('ethereum')

# Polymarket
from trading_tools import polymarket

markets = polymarket.get_btc_markets()
```

## 学习笔记

- 多交易所价格对比可以发现套利机会
- DefiLlama TVL 反映真实资金流入
- 社交情绪是领先指标
- 链上巨鲸仓位是趋势信号
