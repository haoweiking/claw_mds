#!/usr/bin/env python3
"""
Polymarket Trading Bot - 完整版
"""

import requests
import json
import time
from datetime import datetime

API_KEY = "019cb8db-70fb-79cd-979c-1e8fe7ca89d2"
BASE_URL = "https://clob.polymarket.com"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class PolymarketBot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_markets(self, limit=50, active_only=True):
        """获取市场列表"""
        params = {"limit": limit}
        if active_only:
            params["active"] = "true"
        
        resp = requests.get(f"{BASE_URL}/markets", headers=self.headers, params=params)
        return resp.json().get("data", [])
    
    def get_market_prices(self, condition_id):
        """获取市场当前价格"""
        # 通过市场详情获取
        resp = requests.get(f"{BASE_URL}/markets/{condition_id}", headers=self.headers)
        data = resp.json()
        
        tokens = data.get("tokens", [])
        prices = {}
        for t in tokens:
            prices[t.get("outcome")] = t.get("price")
        return prices, data
    
    def search_markets(self, query, limit=20):
        """搜索市场"""
        resp = requests.get(
            f"{BASE_URL}/markets", 
            headers=self.headers, 
            params={"question__contains": query, "limit": limit}
        )
        return resp.json().get("data", [])
    
    def display_markets(self, markets):
        """美化显示市场列表"""
        print("\n📊 当前热门市场")
        print("=" * 80)
        
        for i, m in enumerate(markets[:15], 1):
            q = m.get("question", "")[:60]
            active = "✅" if m.get("active") else "❌"
            closed = "🔒" if m.get("closed") else "📈"
            
            print(f"{i:2}. {active} {closed} {q}")
            
            # 显示当前价格
            tokens = m.get("tokens", [])
            if tokens:
                prices = [f"{t.get('outcome', '')}: ${t.get('price', 'N/A')}" for t in tokens[:3]]
                print(f"    💰 {' | '.join(prices)}")
            print()
    
    def find_opportunities(self, markets):
        """寻找高价值机会（价格被低估的市场）"""
        opportunities = []
        
        for m in markets:
            if m.get("closed") or not m.get("active"):
                continue
            
            tokens = m.get("tokens", [])
            if len(tokens) < 2:
                continue
            
            # 找价格极端的选项
            for t in tokens:
                price = float(t.get("price", 0))
                if price < 0.1:  # 低于10%
                    opportunities.append({
                        "question": m.get("question"),
                        "condition_id": m.get("condition_id"),
                        "outcome": t.get("outcome"),
                        "price": price,
                        "reason": "可能被低估"
                    })
        
        return opportunities


def main():
    bot = PolymarketBot(API_KEY)
    
    print("🏈 Polymarket Trading Bot v1.0")
    print("=" * 50)
    
    # 获取活跃市场
    print("\n🔄 加载市场数据...")
    markets = bot.get_markets(limit=100, active_only=True)
    
    # 显示市场
    bot.display_markets(markets)
    
    # 找机会
    print("\n🎯 低价格机会 (可能被低估)")
    print("-" * 50)
    opps = bot.find_opportunities(markets)
    for o in opps[:5]:
        print(f"• {o['outcome']}: ${o['price']}")
        print(f"  市场: {o['question'][:50]}...")
    
    # 搜索 BTC
    print("\n\n🔍 搜索 BTC 相关市场...")
    btc = bot.search_markets("Bitcoin")
    bot.display_markets(btc[:5])


if __name__ == "__main__":
    main()
