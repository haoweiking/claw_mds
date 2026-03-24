#!/usr/bin/env python3
"""
V-MAC 策略 - 极速动量与均值回归复合策略
Polymarket BTC 15分钟预测市场交易
"""

import subprocess
import json
import time
import requests
from datetime import datetime

# ========== 配置 ==========
PRIVATE_KEY = "1e3299cac7270a4b855d594020459d44e645e161eaa5b6aed659f5781ed75ef8"
MAX_POSITION_PCT = 0.10  # 最大仓位 10%
MIN_POSITION_PCT = 0.05  # 最小仓位 5%
# 假设账户余额 5 USDT
ACCOUNT_balance = 5.0

# ========== 数据源 ==========
def get_binance_kline(symbol="BTCUSDT", interval="1m", limit=50):
    """获取K线数据"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return data
    except Exception as e:
        print(f"获取K线失败: {e}")
        return []

def get_binance_orderbook(symbol="BTCUSDT", limit=20):
    """获取订单簿"""
    try:
        url = "https://api.binance.com/api/v3/depth"
        params = {"symbol": symbol, "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return data
    except Exception as e:
        print(f"获取订单簿失败: {e}")
        return {}

def get_binance_funding(symbol="BTCUSDT"):
    """获取资金费率"""
    try:
        url = "https://fapi.binance.com/futures/data/fundingRateHistory"
        params = {"symbol": symbol, "limit": 1}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        return data[0] if data else None
    except:
        return None

# ========== 技术指标 ==========
def calc_vwap(klines):
    """计算VWAP"""
    if not klines:
        return None
    volume_sum = 0
    price_vol_sum = 0
    for k in klines:
        close = float(k[4])
        volume = float(k[5])
        price_vol_sum += close * volume
        volume_sum += volume
    return price_vol_sum / volume_sum if volume_sum > 0 else None

def calc_ema(prices, period):
    """计算EMA"""
    if len(prices) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calc_rsi(prices, period=5):
    """计算RSI"""
    if len(prices) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calc_orderbook_imbalance(orderbook):
    """计算订单簿失衡度"""
    if not orderbook:
        return 0
    bids = sum(float(b[1]) for b in orderbook.get('bids', []))
    asks = sum(float(a[1]) for a in orderbook.get('asks', []))
    if bids + asks == 0:
        return 0
    return (bids - asks) / (bids + asks) * 100

# ========== Polymarket ==========
def get_active_btc_markets():
    """获取活跃的BTC 15分钟市场"""
    # 当前热门市场 slug（需要动态获取，这里先硬编码）
    markets = [
        "btc-updown-15m-1772726400",  # 11:00-11:15 ET
    ]
    return markets

def get_market_data(slug):
    """获取市场数据"""
    result = subprocess.run(
        ["polymarket", "markets", "get", slug, "-o", "json"],
        capture_output=True, text=True, timeout=30
    )
    try:
        return json.loads(result.stdout)
    except:
        return None

def place_order(slug, outcome, amount):
    """下单"""
    # outcome: "Yes" = Up, "No" = Down
    result = subprocess.run(
        ["polymarket", "clob", "trade", slug, outcome, "--yes-price", "0.5", "--size", str(amount)],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout, result.stderr

# ========== 策略逻辑 ==========
def analyze_entry():
    """分析入场信号"""
    # 1. 获取 Binance 数据
    klines = get_binance_kline()
    if not klines:
        return None, "无法获取K线数据"
    
    # 提取价格
    closes = [float(k[4]) for k in klines]
    
    # 2. 计算指标
    vwap_15m = calc_vwap(klines[-15:])  # 15分钟VWAP
    current_price = closes[-1]
    
    # EMA
    ema9 = calc_ema(closes, 9)
    ema21 = calc_ema(closes, 21)
    
    # RSI
    rsi = calc_rsi(closes)
    
    # 订单簿
    ob = get_binance_orderbook()
    ob_imbalance = calc_orderbook_imbalance(ob)
    
    # 资金费率
    funding = get_binance_funding()
    funding_rate = float(funding['fundingRate']) * 100 if funding else 0
    
    # 3. 获取 Polymarket 数据
    markets = get_active_btc_markets()
    pm_data = {}
    for slug in markets:
        market = get_market_data(slug)
        if market and market.get('active') and not market.get('closed'):
            try:
                prices = json.loads(market.get("outcomePrices", "[]"))
                liquidity = float(market.get("liquidity", 0))
                pm_data[slug] = {
                    'up_price': float(prices[0]) if len(prices) > 0 else 0.5,
                    'down_price': float(prices[1]) if len(prices) > 1 else 0.5,
                    'liquidity': liquidity,
                    'question': market.get('question', '')
                }
            except:
                pass
    
    # 4. 信号判断
    signals = []
    
    # 多头信号
    if vwap_15m and ema9 and ema21 and ob_imbalance:
        # 趋势过滤：价格 > VWAP
        trend_up = current_price > vwap_15m
        # 动量确认：EMA金叉
        momentum_up = ema9 > ema21
        # 盘口优势：买单 > 卖单 20%
        ob优势 = ob_imbalance > 20
        
        if trend_up and momentum_up and ob优势:
            # 检查 Polymarket 赔率
            for slug, pm in pm_data.items():
                if pm['liquidity'] > 10000 and pm['up_price'] < 0.58:
                    signals.append({
                        'type': 'LONG',
                        'side': 'YES',  # Buy Up
                        'price': pm['up_price'],
                        'liquidity': pm['liquidity'],
                        'reason': f'趋势+动量+OB优势: price>{vwap_15m:.0f}, EMA9>{ema21:.0f}, OB>{ob_imbalance:.1f}%'
                    })
        
        # 空头信号
        trend_down = current_price < vwap_15m
        momentum_down = ema9 < ema21
        ob劣势 = ob_imbalance < -20
        
        if trend_down and momentum_down and ob劣势:
            for slug, pm in pm_data.items():
                if pm['liquidity'] > 10000 and pm['down_price'] < 0.58:
                    signals.append({
                        'type': 'SHORT',
                        'side': 'NO',  # Buy Down
                        'price': pm['down_price'],
                        'liquidity': pm['liquidity'],
                        'reason': f'趋势+动量+OB劣势: price<{vwap_15m:.0f}, EMA9<{ema21:.0f}, OB<{ob_imbalance:.1f}%'
                    })
    
    # 5. 费率套利
    if funding_rate > 0.03:  # 资金费率极高
        for slug, pm in pm_data.items():
            if pm['up_price'] > 0.55:  # 多头拥挤但价格还没反映
                signals.append({
                    'type': 'FUNDING_ARB',
                    'side': 'NO',
                    'price': pm['down_price'],
                    'liquidity': pm['liquidity'],
                    'reason': f'费率套利: Funding={funding_rate:.3f}%'
                })
    
    return signals, {
        'price': current_price,
        'vwap': vwap_15m,
        'ema9': ema9,
        'ema21': ema21,
        'rsi': rsi,
        'ob_imbalance': ob_imbalance,
        'funding_rate': funding_rate
    }

# ========== 主循环 ==========
def main():
    print("🚀 V-MAC 策略启动")
    print("="*60)
    
    last_signal_time = 0
    
    while True:
        try:
            signals, btc_info = analyze_entry()
            
            if btc_info:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] BTC: ${btc_info['price']:,.0f} | "
                      f"VWAP: ${btc_info['vwap']:,.0f} | "
                      f"EMA: {btc_info['ema9']:,.0f}/{btc_info['ema21']:,.0f} | "
                      f"RSI: {btc_info['rsi']:.1f} | "
                      f"OB: {btc_info['ob_imbalance']:+.1f}% | "
                      f"Funding: {btc_info['funding_rate']:.3f}%")
            
            if signals:
                print(f"   🚨 发现信号: {len(signals)}个")
                for sig in signals:
                    print(f"   - {sig['type']}: {sig['side']} @ ${sig['price']:.3f} | {sig['reason']}")
                    
                    # 执行下单
                    amount = ACCOUNT_balance * MAX_POSITION_PCT / sig['price']
                    print(f"   📝 尝试下单: {amount:.2f} USDT @ ${sig['price']}")
                    # place_order(...)
                    
                last_signal_time = time.time()
            else:
                print("   ⏳ 无信号，等待...")
            
            time.sleep(30)  # 每30秒检查
            
        except KeyboardInterrupt:
            print("\n👋 监控已停止")
            break
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
