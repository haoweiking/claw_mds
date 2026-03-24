#!/bin/bash
# Elon Tweets 持仓监控 - 纯脚本计算，避免 AI 算错
# 用法: ./elon-monitor.sh

set -euo pipefail

POSITIONS_FILE="/Users/az_ken/.openclaw/workspace/memory/elon-tweet-positions.json"

# 获取市场价格
get_prices() {
    polymarket events get "elon-musk-of-tweets-march-10-march-17" -o json 2>/dev/null | python3 -c "
import json, sys

raw = sys.stdin.read()
data = json.loads(raw)
if isinstance(data, list):
    for e in data:
        if isinstance(e, dict) and 'markets' in e:
            data = e
            break
    if isinstance(data, list):
        data = data[0]

# Get tweet count from description or event info
end = data.get('endDate', '')

for m in data.get('markets', []):
    label = m.get('groupItemTitle', '')
    op = m.get('outcomePrices', '[]')
    prices = json.loads(op)  # outcomePrices is a JSON string
    yes_price = float(prices[0])
    print(f'{label}|{yes_price}')
"
}

# 计算并输出
OUTPUT=$(get_prices)

python3 -c "
import sys, json, re
from datetime import datetime, timezone, timedelta

# Parse prices from stdin
lines = '''$OUTPUT'''.strip().split('\n')
prices = {}
for line in lines:
    parts = line.split('|')
    if len(parts) == 2:
        prices[parts[0]] = float(parts[1])

# Positions (hardcoded to avoid AI errors)
positions = [
    {'range': '200-219', 'invested': 1.0, 'buyPrice': 0.013},
    # 240-259: SOLD @ 5.55¢ on 2026-03-16 (PnL: +$0.78)
    # {'range': '240-259', 'invested': 5.0, 'buyPrice': 0.048},  # REMOVED - already sold
    {'range': '380-399', 'invested': 5.0, 'buyPrice': 0.079},
]

total_invested = sum(p['invested'] for p in positions)
total_current = 0

# Time
now = datetime.now(timezone(timedelta(hours=8)))
end = datetime(2026, 3, 17, 16, 0, tzinfo=timezone.utc)  # 12:00 PM ET = 16:00 UTC
days_left = (end - now.astimezone(timezone.utc)).total_seconds() / 86400

print(f'📊 Elon 持仓监控')
print(f'⏰ {now.strftime(\"%m/%d %H:%M\")} CST | 距截止还有 {days_left:.1f} 天')
print()

# Header
print('| 区间 | 买入价 | 当前价 | 涨跌幅 | 当前价值 | 盈亏 |')
print('|------|--------|--------|--------|----------|------|')

for pos in positions:
    rng = pos['range']
    invested = pos['invested']
    buy = pos['buyPrice']
    current = prices.get(rng, 0)
    
    current_value = invested * (current / buy) if buy > 0 else 0
    pnl = current_value - invested
    change_pct = ((current - buy) / buy) * 100
    
    total_current += current_value
    
    buy_c = buy * 100
    curr_c = current * 100
    
    warn = ''
    if change_pct <= -30:
        warn = ' ⚠️'
    elif change_pct >= 80:
        warn = ' 🎯'
    
    print(f'| {rng} | {buy_c:.1f}¢ | {curr_c:.2f}¢ | {change_pct:+.1f}%{warn} | \${current_value:.2f} | \${pnl:+.2f} |')

total_pnl = total_current - total_invested
total_pct = (total_pnl / total_invested) * 100

print()
print(f'总览：投入 \${total_invested:.2f} → 当前 \${total_current:.2f} | 总 PnL: \${total_pnl:+.2f} ({total_pct:+.1f}%)')

# Update positions file
import os
pos_file = os.environ.get('POSITIONS_FILE', '$POSITIONS_FILE')
if os.path.exists(pos_file):
    with open(pos_file) as f:
        data = json.load(f)
    
    for pos_data in data.get('positions', []):
        rng = pos_data['range']
        if rng in prices:
            pos_data['currentPrice'] = prices[rng]
            pos_data['currentValue'] = pos_data['invested'] * (prices[rng] / pos_data['buyPrice'])
            pos_data['pnl'] = pos_data['currentValue'] - pos_data['invested']
    
    data['totalPnl'] = total_pnl
    data['currentValue'] = total_current
    data['updated'] = now.isoformat()
    
    with open(pos_file, 'w') as f:
        json.dump(data, f, indent=2)
"
