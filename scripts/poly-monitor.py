#!/usr/bin/env python3
"""Polymarket 模拟交易 - 全自动执行"""
import json, subprocess, sys, os, time
from datetime import datetime, timezone

PORTFOLIO = "/Users/az_ken/.openclaw/workspace/memory/poly-portfolio.json"

def get_btc_price():
    """Get BTC price with fallback"""
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "8", "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"], capture_output=True, text=True, timeout=12)
        d = json.loads(r.stdout)
        p = d.get("bitcoin", {}).get("usd", 0)
        if p > 10000: return p
    except: pass
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "8", "https://api.coinbase.com/v2/prices/BTC-USD/spot"], capture_output=True, text=True, timeout=12)
        d = json.loads(r.stdout)
        p = float(d["data"]["amount"])
        if p > 10000: return p
    except: pass
    return None

def get_market_price(slug, match_text):
    """Get YES price for a market"""
    try:
        r = subprocess.run(["polymarket", "events", "get", slug, "-o", "json"], capture_output=True, text=True, timeout=25)
        data = json.loads(r.stdout)
        if isinstance(data, list): data = data[0]
        for m in data.get("markets", []):
            label = m.get("groupItemTitle", "") or m.get("question", "")
            if match_text.lower() in label.lower():
                return float(json.loads(m["outcomePrices"])[0])
    except Exception as e:
        print(f"ERR: {slug}: {e}", file=sys.stderr)
    return None

def execute_trade(p, market_key, side, price, reason):
    """Execute a simulated trade (YES position)"""
    pos = None
    for pp in p["positions"]:
        if pp["market"] == market_key and pp.get("side", "YES") == "YES":
            pos = pp
            break
    if not pos:
        return None
    
    shares = pos["shares"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if side == "SELL":
        value = shares * price
        pnl = value - pos["totalCost"]
        pnl_pct = (pnl / pos["totalCost"]) * 100
        trade = {
            "time": now, "market": market_key, "name": pos["name"],
            "side": "SELL", "price": price, "shares": round(shares, 4),
            "value": round(value, 2), "pnl": round(pnl, 2), "pnl_pct": round(pnl_pct, 1),
            "reason": reason
        }
        p["cash"] = round(p["cash"] + value, 4)
        pos["shares"] = 0
        pos["status"] = "closed"
        p["trades"].append(trade)
        return trade
    
    elif side == "BUY_DIP" and p["cash"] > 0.5:
        buy_amount = min(p["cash"] * 0.5, 1.0)
        new_shares = buy_amount / price
        pos["shares"] = round(pos["shares"] + new_shares, 4)
        pos["totalCost"] = round(pos["totalCost"] + buy_amount, 4)
        pos["avgPrice"] = round(pos["totalCost"] / pos["shares"], 4)
        p["cash"] = round(p["cash"] - buy_amount, 4)
        trade = {
            "time": now, "market": market_key, "name": pos["name"],
            "side": "BUY_DIP", "price": price, "shares": round(new_shares, 4),
            "amount": round(buy_amount, 2), "reason": reason
        }
        p["trades"].append(trade)
        return trade
    return None

def execute_no_trade(p, market_key, side, no_price, reason):
    """Execute a simulated NO trade"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if side == "BUY_NO" and p["cash"] > 0.5:
        buy_amount = min(p["cash"] * 0.3, 0.8)  # NO trades smaller size
        shares = buy_amount / no_price
        
        # Check if NO position already exists
        pos = None
        for pp in p["positions"]:
            if pp["market"] == market_key and pp.get("side") == "NO":
                pos = pp
                break
        
        if pos:
            pos["shares"] = round(pos["shares"] + shares, 4)
            pos["totalCost"] = round(pos["totalCost"] + buy_amount, 4)
            pos["avgPrice"] = round(pos["totalCost"] / pos["shares"], 4)
        else:
            p["positions"].append({
                "market": market_key,
                "name": p["markets"].get(market_key, {}).get("name", market_key) + " (NO)",
                "side": "NO",
                "shares": round(shares, 4),
                "avgPrice": no_price,
                "totalCost": round(buy_amount, 4),
                "status": "active"
            })
        
        p["cash"] = round(p["cash"] - buy_amount, 4)
        trade = {
            "time": now, "market": market_key, "name": f"NO {market_key}",
            "side": "BUY_NO", "price": no_price, "shares": round(shares, 4),
            "amount": round(buy_amount, 2), "reason": reason
        }
        p["trades"].append(trade)
        return trade
    
    elif side == "SELL_NO":
        for pp in p["positions"]:
            if pp["market"] == market_key and pp.get("side") == "NO" and pp["shares"] > 0:
                value = pp["shares"] * no_price
                pnl = value - pp["totalCost"]
                pnl_pct = (pnl / pp["totalCost"]) * 100
                trade = {
                    "time": now, "market": market_key, "name": pp["name"],
                    "side": "SELL_NO", "price": no_price, "shares": round(pp["shares"], 4),
                    "value": round(value, 2), "amount": round(value, 2), "pnl": round(pnl, 2), "pnl_pct": round(pnl_pct, 1),
                    "reason": reason
                }
                p["cash"] = round(p["cash"] + value, 4)
                pp["shares"] = 0
                pp["status"] = "closed"
                p["trades"].append(trade)
                return trade
    return None

def main():
    with open(PORTFOLIO) as f:
        p = json.load(f)
    
    if p["status"] != "active":
        print("PORTFOLIO_CLOSED")
        return
    
    # Get prices
    btc = get_btc_price()
    prices = {
        "btc_75k_march": get_market_price("what-price-will-bitcoin-hit-in-march-2026", "75,000"),
        "us_recession": get_market_price("us-recession-by-end-of-2026", "recession"),
        "fed_0_cuts": get_market_price("how-many-fed-rate-cuts-in-2026", "0 (0 bps)"),
        "ukraine_ceasefire": get_market_price("what-will-happen-before-gta-vi", "Ceasefire"),
    }
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    executed_trades = []
    total_value = p["cash"]
    
    # === ALL TRADING OPPORTUNITIES ===
    # 1. 瑞典 NO - 33.5% - 边际优势 11% - 止损 NO<25¢, 止盈>55¢, 部分>45¢
    # 2. Tampa Bay 冠军 YES - 13.9% - 边际优势 2.6% - 止损<8%, 止盈>25%
    # 3. Carolina 冠军 YES - 10.5% - 边际优势 3.0% - 止损<5%, 止盈>20%
    # 4. 意大利出线 YES - 65.5% - 边际优势 4.5% - 止损<50%, 止盈>80%
    
    sweden_no_price = get_market_price("will-sweden-qualify-for-the-2026-fifa-world-cup", "Sweden")
    if sweden_no_price is None:
        # Fallback to portfolio price
        for pos in p["positions"]:
            if "sweden" in pos.get("market", "").lower():
                sweden_no_price = pos.get("lastPrice", 0.33)
                break
    
    if sweden_no_price:
        prices["sweden_no"] = sweden_no_price
    
    # Check each position for signals
    for pos in p["positions"]:
        mk = pos["market"]
        price = prices.get(mk)
        if price is None or pos.get("shares", 0) == 0:
            continue
        
        value = pos["shares"] * price
        pnl = value - pos["totalCost"]
        pnl_pct = (pnl / pos["totalCost"]) * 100
        total_value += value
        
        trade = None
        
        # === TRADING RULES ===
        
        # 1. 瑞典 NO - 止损<25¢, 止盈>55¢, 部分止盈>45¢
        if "sweden" in mk.lower() and pos.get("side") == "NO":
            # 瑞典 NO 交易规则
            if sweden_no_price > 0.55:
                trade = execute_no_trade(p, mk, "SELL_NO", sweden_no_price, f"🎯 止盈: NO {sweden_no_price*100:.1f}¢ > 55¢, 市场过度悲观")
            elif sweden_no_price < 0.25:
                trade = execute_no_trade(p, mk, "SELL_NO", sweden_no_price, f"⛔ 止损: NO {sweden_no_price*100:.1f}¢ < 25¢, 判断可能错误")
            elif sweden_no_price > 0.45:
                trade = execute_no_trade(p, mk, "SELL_NO", sweden_no_price, f"📊 部分止盈: NO {sweden_no_price*100:.1f}¢ > 45¢")
        
        # 2. Tampa Bay 冠军 YES - 止损<8%, 止盈>25%
        elif "tampa" in mk.lower() and pos.get("side") == "YES":
            if price > 0.25:
                trade = execute_trade(p, mk, "SELL", price, f"🎯 止盈: YES {price*100:.1f}¢ > 25¢")
            elif price < 0.08:
                trade = execute_trade(p, mk, "SELL", price, f"⛔ 止损: YES {price*100:.1f}¢ < 8¢")
        
        # 3. Carolina 冠军 YES - 止损<5%, 止盈>20%
        elif "carolina" in mk.lower() and pos.get("side") == "YES":
            if price > 0.20:
                trade = execute_trade(p, mk, "SELL", price, f"🎯 止盈: YES {price*100:.1f}¢ > 20¢")
            elif price < 0.05:
                trade = execute_trade(p, mk, "SELL", price, f"⛔ 止损: YES {price*100:.1f}¢ < 5¢")
        
        # 4. 意大利出线 YES - 止损<50%, 止盈>80%
        elif "italy" in mk.lower() and pos.get("side") == "YES":
            if price > 0.80:
                trade = execute_trade(p, mk, "SELL", price, f"🎯 止盈: YES {price*100:.1f}¢ > 80¢")
            elif price < 0.50:
                trade = execute_trade(p, mk, "SELL", price, f"⛔ 止损: YES {price*100:.1f}¢ < 50¢")
        
        elif mk == "btc_75k_march":
            if btc and btc > 73500 and price > 0.80:
                trade = execute_trade(p, mk, "SELL", price, f"BTC ${btc:,.0f} > $73.5k, 合约 {price*100:.1f}¢")
            elif btc and btc < 68000:
                trade = execute_trade(p, mk, "SELL", price, f"⛔ 止损: BTC ${btc:,.0f} < $68k")
            elif btc and btc < 70000 and price < 0.58 and p["cash"] > 0.5:
                trade = execute_trade(p, mk, "BUY_DIP", price, f"BTC ${btc:,.0f} 回调, 加仓 @ {price*100:.1f}¢")
            # NO 机会: BTC 跌破 $70k 时，YES 已到 60%+ 但可能冲不到 $75k
            elif btc and btc < 70000 and price > 0.55:
                no_price = 1 - price
                if no_price < 0.50 and p["cash"] > 0.5:
                    trade = execute_no_trade(p, mk, "BUY_NO", no_price, f"BTC ${btc:,.0f} 弱势, NO @ {no_price*100:.1f}¢ 有价值")
        
        elif mk == "us_recession":
            if price > 0.45:
                trade = execute_trade(p, mk, "SELL", price, f"🎯 目标达成: {price*100:.1f}¢ > 45¢")
            elif price < 0.20:
                trade = execute_trade(p, mk, "SELL", price, f"⛔ 止损: {price*100:.1f}¢ < 20¢")
        
        elif mk == "fed_0_cuts":
            if price > 0.35:
                trade = execute_trade(p, mk, "SELL", price, f"🎯 目标达成: {price*100:.1f}¢ > 35¢")
            elif price < 0.15:
                trade = execute_trade(p, mk, "SELL", price, f"⛔ 止损: {price*100:.1f}¢ < 15¢")
            # NO 机会: 若 Fed 转鸽，0 cuts 概率下降，NO 有价值
            elif price > 0.30:
                no_price = 1 - price
                if no_price < 0.75 and p["cash"] > 0.5:
                    trade = execute_no_trade(p, mk, "BUY_NO", no_price, f"Fed 0 cuts YES {price*100:.1f}¢ 偏高, 买 NO @ {no_price*100:.1f}¢")
        
        elif mk == "ukraine_ceasefire":
            if price > 0.62:
                trade = execute_trade(p, mk, "SELL", price, f"🚀 新闻脉冲: {price*100:.1f}¢ > 62¢")
            elif price < 0.40:
                trade = execute_trade(p, mk, "SELL", price, f"⛔ 止损: {price*100:.1f}¢ < 40¢")
            # NO 机会: 停火概率被高估时买 NO
            elif price > 0.55:
                no_price = 1 - price
                if no_price < 0.50 and p["cash"] > 0.5:
                    trade = execute_no_trade(p, mk, "BUY_NO", no_price, f"停火 YES {price*100:.1f}¢ 偏高, 买 NO @ {no_price*100:.1f}¢")
        
        if trade:
            executed_trades.append(trade)
    
    # Recalculate total value
    total_value = p["cash"]
    for pos in p["positions"]:
        if pos.get("shares", 0) > 0:
            price = prices.get(pos["market"])
            if price:
                total_value += pos["shares"] * price
    
    # Save portfolio
    p["lastPrices"] = {k: round(v, 4) for k, v in prices.items() if v is not None}
    p["lastBtc"] = btc or 0
    p["lastCheck"] = now
    p["currentValue"] = round(total_value, 2)
    p["currentPnl"] = round(total_value - p["startValue"], 2)
    p["currentPnlPct"] = round((total_value - p["startValue"]) / p["startValue"] * 100, 1)
    
    with open(PORTFOLIO, "w") as f:
        json.dump(p, f, indent=2)
    
    # === OUTPUT ===
    print(f"📊 Poly交易 | {now}")
    if btc:
        print(f"💰 BTC: ${btc:,.0f}")
    
    print()
    print("| 持仓 | 买入价 | 当前价 | 价值 | 盈亏 |")
    print("|------|--------|--------|------|------|")
    for pos in p["positions"]:
        if pos.get("shares", 0) == 0:
            print(f"| {pos['name']} | -- | 已清仓 | $0 | -- |")
            continue
        price = prices.get(pos["market"])
        if price is None:
            continue
        val = pos["shares"] * price
        pnl = val - pos["totalCost"]
        pnl_pct = (pnl / pos["totalCost"]) * 100
        icon = "✅" if pnl > 0 else ("⚠️" if pnl_pct < -25 else "")
        print(f"| {pos['name']} | {pos['avgPrice']*100:.1f}¢ | {price*100:.1f}¢ | ${val:.2f} | ${pnl:+.2f} ({pnl_pct:+.1f}%) {icon} |")
    
    pnl = total_value - p["startValue"]
    pnl_pct = (pnl / p["startValue"]) * 100
    icon = "📈" if pnl > 0 else ("📉" if pnl < 0 else "")
    print(f"\n💼 总: ${total_value:.2f} | PnL: ${pnl:+.2f} ({pnl_pct:+.1f}%) | 现金: ${p['cash']:.2f} {icon}")
    
    if executed_trades:
        print("\n🔔 已执行交易:")
        for t in executed_trades:
            if t["side"] == "SELL":
                print(f"  卖出 {t['name']} @ {t['price']*100:.1f}¢ → ${t['value']:.2f} (PnL: ${t['pnl']:+.2f} {t['pnl_pct']:+.1f}%)")
                print(f"  原因: {t['reason']}")
            else:
                print(f"  加仓 {t['name']} @ {t['price']*100:.1f}¢ +${t['amount']:.2f}")
                print(f"  原因: {t['reason']}")

if __name__ == "__main__":
    main()
