#!/usr/bin/env python3
import json

# Current portfolio values
cash = 722.77
btc_shares = 308
btc_avg = 0.4865
btc_last = 0.1025

bitboy_shares = 1449.4091
bitboy_avg = 0.088
bitboy_last = 0.1025

# Calculate
btc_value = btc_shares * btc_last
btc_cost = btc_shares * btc_avg
btc_pnl = btc_value - btc_cost

bitboy_value = bitboy_shares * bitboy_last
bitboy_cost = bitboy_shares * bitboy_avg
bitboy_pnl = bitboy_value - bitboy_cost

total_value = cash + btc_value + bitboy_value
total_pnl = total_value - 1000

print('=== Poly 持仓反馈 (2026-03-26 07:52 UTC) ===')
print(f'现金: ${cash:.2f}')
print()
print('--- BTC $1M before GTA VI YES ---')
print(f'  持仓: {btc_shares} 股 @ 平均 ${btc_avg:.4f}')
print(f'  当前: ${btc_last:.4f} → 价值 ${btc_value:.2f}')
print(f'  盈亏: ${btc_pnl:.2f} ({btc_pnl/btc_cost*100:.1f}%)')
print(f'  止损: 40% (触发价 ${btc_avg*0.6:.4f}) - 未触及')
print(f'  止盈: 80% (目标价 ${btc_avg*1.8:.4f}) - 未触及')
print()
print('--- BitBoy 定罪 YES ---')
print(f'  持仓: {bitboy_shares:.2f} 股 @ 平均 ${bitboy_avg:.4f}')
print(f'  当前: ${bitboy_last:.4f} → 价值 ${bitboy_value:.2f}')
print(f'  盈亏: ${bitboy_pnl:.2f} ({bitboy_pnl/bitboy_cost*100:.1f}%)')
print(f'  止损: 5% (触发价 ${bitboy_avg*0.95:.4f}) - 未触及')
print(f'  止盈: 20% (目标价 ${bitboy_avg*1.2:.4f}) - 未触及')
print()
print('=== 汇总 ===')
print(f'总价值: ${total_value:.2f}')
print(f'总盈亏: ${total_pnl:.2f} ({total_pnl/1000*100:.1f}%)')
print()
print('状态: 无交易执行 - 未触及止盈止损')