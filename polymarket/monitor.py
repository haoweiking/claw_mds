#!/usr/bin/env python3
"""
BTC 15分钟预测市场监控 + 策略系统
"""

import subprocess
import json
import time
from datetime import datetime

MARKET_SLUG = "btc-updown-15m-1772628300"

def get_market_data():
    """获取市场数据"""
    result = subprocess.run(
        ["polymarket", "markets", "get", MARKET_SLUG, "-o", "json"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        return data
    except:
        return None

def parse_prices(data):
    """解析价格"""
    prices_str = data.get("Prices", "")
    outcomes_str = data.get("Outcomes", "")
    
    prices = [float(p) for p in prices_str.split(",")]
    outcomes = outcomes_str.split(", ")
    
    return dict(zip(outcomes, prices))

def get_strategy(prices, liquidity):
    """基于当前市场数据给出策略"""
    up_price = prices.get("Up", 0)
    down_price = prices.get("Down", 0)
    
    # 计算隐含概率
    total = up_price + down_price
    up_prob = up_price / total * 100 if total > 0 else 0
    down_prob = down_price / total * 100 if total > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"📊 BTC 15分钟市场分析")
    print(f"{'='*50}")
    print(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    print(f"📈 Up 概率: {up_prob:.1f}% (价格: {up_price})")
    print(f"📉 Down 概率: {down_prob:.1f}% (价格: {down_price})")
    print(f"💧 流动性: ${liquidity}")
    print()
    
    # 策略逻辑
    recommendation = None
    reason = ""
    
    if up_price >= 0.95:
        recommendation = "SELL_UP"  # 卖出手中持仓
        reason = f"Up价格过高({up_price})，建议止盈"
    elif up_price > 0.70:
        recommendation = "WAIT"
        reason = f"Up价格{up_price}，胜率高但盈亏比差(只赚~{((1-up_price)/up_price)*100:.0f}%)，建议等待"
    elif up_price < 0.40:
        recommendation = "BUY_UP"
        reason = f"Up价格{up_price}合理，盈亏比好，值得买入"
    elif up_price < 0.30:
        recommendation = "STRONG_BUY_UP"
        reason = f"价格严重被低估！盈亏比极佳"
    else:
        recommendation = "WAIT"
        reason = "价格区间不明朗，建议观望"
    
    print(f"🎯 策略建议: {recommendation}")
    print(f"💡 理由: {reason}")
    print(f"{'='*50}\n")
    
    return {
        "recommendation": recommendation,
        "reason": reason,
        "up_price": up_price,
        "down_price": down_price,
        "up_prob": up_prob,
        "down_prob": down_prob
    }

def main():
    print("🚀 BTC 15分钟预测市场监控启动")
    print("按 Ctrl+C 退出\n")
    
    while True:
        data = get_market_data()
        if data:
            prices = parse_prices(data)
            liquidity = data.get("Liquidity", "$0")
            result = get_strategy(prices, liquidity)
        else:
            print("❌ 获取数据失败，等待重试...")
        
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
