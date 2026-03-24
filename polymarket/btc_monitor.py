#!/usr/bin/env python3
"""
BTC 15分钟预测市场 - 实时监控 + 策略系统
"""

import subprocess
import json
import time
from datetime import datetime

# 跟踪的市场
MARKETS = [
    "btc-updown-15m-1772629200",  # 8:00-8:15
    "btc-updown-15m-1772630100",  # 8:15-8:30  
    "btc-updown-15m-1772631000",  # 8:30-8:45
]

def get_market(slug):
    """获取市场数据"""
    result = subprocess.run(
        ["polymarket", "markets", "get", slug, "-o", "json"],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except:
        return None

def analyze_market(market):
    """分析市场并给出策略"""
    if not market:
        return None
    
    question = market.get("question", "")
    active = market.get("active", False)
    closed = market.get("closed", True)
    
    if not active or closed:
        return None
    
    try:
        prices = json.loads(market.get("outcomePrices", "[]"))
        outcomes = json.loads(market.get("outcomes", "[]"))
    except:
        return None
    
    if len(prices) < 2:
        return None
    
    up_price = float(prices[0])
    down_price = float(prices[1])
    volume = float(market.get("volume", 0))
    
    # 解析时间
    end_date = market.get("endDate", "")
    
    # 计算隐含概率
    total = up_price + down_price
    up_prob = up_price / total * 100
    down_prob = down_price / total * 100
    
    # 盈亏比计算
    if up_price > 0:
        up_payout = (1 - up_price) / up_price * 100  # 买入1能赢多少
    else:
        up_payout = 0
    
    if down_price > 0:
        down_payout = (1 - down_price) / down_price * 100
    else:
        down_payout = 0
    
    # 策略逻辑
    recommendation = "WAIT"
    action = ""
    size = 0
    
    # 策略1：价格接近50%，且有足够流动性
    if volume > 1000:
        if up_prob > 40 and up_prob < 60:
            if up_payout > 50:  # 盈亏比 > 1:1
                recommendation = "BUY_UP"
                action = f"买入 Up，最多可买 ~${volume*0.1:.0f}"
                size = min(5, volume * 0.02)  # 最多用5U或2%流动性
        elif down_prob > 40 and down_prob < 60:
            if down_payout > 50:
                recommendation = "BUY_DOWN"
                action = f"买入 Down，最多可买 ~${volume*0.1:.0f}"
                size = min(5, volume * 0.02)
    
    # 策略2：价格极端但流动性高（需要更谨慎）
    elif volume > 10000:
        if up_prob > 80:
            recommendation = "SELL_UP"  # 卖高估的
            action = "价格过高，建议不追高"
        elif down_prob > 80:
            recommendation = "SELL_DOWN"
            action = "价格过低，建议不追空"
    
    return {
        "question": question,
        "end_time": end_date,
        "up_price": up_price,
        "down_price": down_price,
        "up_prob": up_prob,
        "down_prob": down_prob,
        "up_payout": up_payout,
        "down_payout": down_payout,
        "volume": volume,
        "recommendation": recommendation,
        "action": action,
        "size": size
    }

def format_recommendation(analysis):
    """格式化推荐信息"""
    if not analysis:
        return ""
    
    r = analysis
    emoji = {
        "WAIT": "⏳",
        "BUY_UP": "🟢",
        "BUY_DOWN": "🔴",
        "SELL_UP": "🔴",
        "SELL_DOWN": "🟢",
    }
    
    msg = f"""
{'='*60}
🎯 市场分析: {r['question'][:40]}...
{'='*60}

📊 当前概率:
   🟢 Up: {r['up_prob']:.1f}% (价格: ${r['up_price']:.3f})
   🔴 Down: {r['down_prob']:.1f}% (价格: ${r['down_price']:.3f})

💰 盈亏比:
   🟢 Up: 1:{r['up_payout']:.0f} (买${r['up_price']:.2f}赢${1-r['up_price']:.2f})
   🔴 Down: 1:{r['down_payout']:.0f} (买${r['down_price']:.2f}赢${1-r['down_price']:.2f})

💵 成交量: ${r['volume']:,.0f}
⏰ 结束时间: {r['end_time'][:16]} UTC

{emoji.get(r['recommendation'], '❓')} 建议: {r['recommendation']}
📝 {r['action']}
{'='*60}
"""
    return msg

def main():
    print("🚀 BTC 15分钟市场监控启动")
    print("="*60)
    
    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检查市场...")
        
        has_opportunity = False
        
        for slug in MARKETS:
            market = get_market(slug)
            analysis = analyze_market(market)
            
            if analysis:
                msg = format_recommendation(analysis)
                print(msg)
                
                # 有建议时标记
                if analysis['recommendation'] != 'WAIT':
                    has_opportunity = True
            else:
                # 检查市场是否关闭
                if market and market.get('closed'):
                    print(f"   {slug}: 已关闭")
        
        if not has_opportunity:
            print("   当前没有好的交易机会...")
        
        time.sleep(30)  # 每30秒检查一次

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
