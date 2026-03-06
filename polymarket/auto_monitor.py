#!/usr/bin/env python3
"""
BTC 15分钟预测市场 自动监控
当新市场出现时自动提醒
"""

import subprocess
import json
import time
from datetime import datetime
import re

def get_all_events():
    """获取所有事件"""
    result = subprocess.run(
        ["polymarket", "events", "list", "-o", "json"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        return data
    except:
        return []

def find_btc_15m_events(events):
    """查找BTC 15分钟市场"""
    btc_events = []
    for e in events:
        title = e.get('title', '')
        slug = e.get('slug', '')
        active = e.get('active', False)
        closed = e.get('closed', True)
        
        # 匹配 btc up/down 15m
        if ('btc' in slug.lower() or 'bitcoin' in slug.lower()) and \
           ('up' in slug.lower() or 'down' in slug.lower()) and \
           ('15m' in slug.lower() or '15-min' in slug.lower()):
            btc_events.append(e)
        
        # 也匹配新格式
        if 'btc-updown' in slug.lower() or 'bitcoin-up-or-down' in title.lower():
            btc_events.append(e)
    
    return btc_events

def get_market_details(slug):
    """获取市场详情"""
    result = subprocess.run(
        ["polymarket", "markets", "get", slug, "-o", "json"],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except:
        return None

def format_alert(event, market):
    """格式化警报消息"""
    title = event.get('title', '')
    slug = event.get('slug', '')
    volume = event.get('volume', '$0')
    liquidity = event.get('liquidity', '$0')
    
    prices = market.get('outcomePrices', '[]')
    outcomes = market.get('outcomes', '[]')
    
    try:
        price_list = json.loads(prices)
        outcome_list = json.loads(outcomes)
    except:
        price_list = []
        outcome_list = []
    
    alert = f"""
🎯 新BTC 15分钟市场出现！

📌 {title}
📊 Slug: {slug}
💰 成交量: ${volume}
💧 流动性: ${liquidity}

📈 价格:"""
    
    for i, outcome in enumerate(outcome_list):
        if i < len(price_list):
            alert += f" {outcome}: {price_list[i]}"
    
    alert += f"""

⏰ 发现时间: {datetime.now().strftime('%H:%M:%S')}
🔗 https://polymarket.com/event/{slug}
"""
    return alert

def main():
    print("🔍 BTC 15分钟市场监控启动")
    print("按 Ctrl+C 退出\n")
    
    last_alerted = set()
    
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 扫描市场...")
        
        events = get_all_events()
        btc_events = find_btc_15m_events(events)
        
        for e in btc_events:
            slug = e.get('slug', '')
            active = e.get('active', False)
            
            if slug not in last_alerted and active:
                market = get_market_details(slug)
                if market:
                    alert = format_alert(e, market)
                    print(alert)
                    last_alerted.add(slug)
        
        if not btc_events:
            print("  → 暂无BTC 15分钟市场，等待中...")
        
        time.sleep(30)  # 每30秒检查一次

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
