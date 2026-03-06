#!/usr/bin/env python3
"""
Polymarket BTC 15分钟市场监控
直接通过 API 获取所有 btc-updown 市场
"""

import requests
import json
import subprocess
import time

def get_all_btc_markets():
    """获取所有 btc-updown 市场"""
    try:
        # 方法1: 直接通过 API 查询
        url = "https://clob.polymarket.com/markets"
        resp = requests.get(url, params={"active": "true"}, timeout=10)
        data = resp.json()
        
        btc_markets = []
        for m in data:
            slug = m.get('market_slug', '')
            if 'btc-updown' in slug.lower():
                btc_markets.append(m)
        
        if btc_markets:
            return btc_markets
        
        # 方法2: 通过已知 slug 查询
        # 15分钟周期的 slug 格式: btc-updown-15m-{timestamp}
        import datetime
        now = datetime.datetime.utcnow()
        markets = []
        
        # 检查最近几个周期
        for i in range(5):
            # 每个周期15分钟
            ts = int((now.timestamp() // 900) * 900) + i * 900
            slug = f"btc-updown-15m-{ts}"
            result = subprocess.run(
                ["polymarket", "markets", "get", slug],
                capture_output=True, text=True, timeout=10
            )
            if "Status: Active" in result.stdout:
                markets.append(slug)
        
        return markets
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_market_price(slug):
    """获取市场价格"""
    result = subprocess.run(
        ["polymarket", "markets", "get", slug, "-o", "json"],
        capture_output=True, text=True, timeout=10
    )
    try:
        return json.loads(result.stdout)
    except:
        return None

if __name__ == "__main__":
    print("=== BTC 15分钟市场检查 ===")
    markets = get_all_btc_markets()
    print(f"找到 {len(markets)} 个市场")
    for m in markets:
        print(f"- {m}")
