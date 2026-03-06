#!/usr/bin/env python3
"""
交易工具集 - Trading Tools Package
"""

import requests
import json
import subprocess
from datetime import datetime

# ========== 价格数据 ==========
class PriceData:
    """多交易所价格数据"""
    
    @staticmethod
    def coingecko(coins=['bitcoin', 'ethereum']):
        """CoinGecko 价格"""
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ",".join(coins), "vs_currencies": "usd"}
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    
    @staticmethod
    def binance(symbol="BTCUSDT"):
        """Binance 现货价格"""
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=10)
        return r.json()
    
    @staticmethod
    def okx(inst_id="BTC-USDT"):
        """OKX 价格"""
        url = f"https://www.okx.com/api/v5/market/ticker?instId={inst_id}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('code') == '0':
            return data['data'][0]
        return None
    
    @staticmethod
    def bybit(symbol="BTCUSDT"):
        """Bybit 价格"""
        url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('retCode') == 0:
            return data['result']['list'][0]
        return None
    
    @staticmethod
    def cryptocompare(symbols=['BTC', 'ETH']):
        """CryptoCompare 多交易所价格"""
        url = "https://min-api.cryptocompare.com/data/pricemulti"
        params = {"fsyms": ",".join(symbols), "tsyms": "USD"}
        r = requests.get(url, params=params, timeout=10)
        return r.json()

# ========== K线数据 ==========
class KLineData:
    """K线数据"""
    
    @staticmethod
    def binance(symbol="BTCUSDT", interval="5m", limit=50):
        """Binance K线"""
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    
    @staticmethod
    def calculate_indicators(klines):
        """计算技术指标"""
        closes = [float(k[4]) for k in klines]
        volumes = [float(k[5]) for k in klines]
        
        # RSI
        def calc_rsi(prices, period=5):
            gains, losses = [], []
            for i in range(1, len(prices)):
                d = prices[i] - prices[i-1]
                gains.append(d if d > 0 else 0)
                losses.append(abs(d) if d < 0 else 0)
            if sum(losses[-period:]) == 0:
                return 100
            rs = sum(gains[-period:]) / (sum(losses[-period:]) + 1e-9)
            return 100 - (100 / (1 + rs))
        
        # VWAP
        def calc_vwap(prices, volumes):
            vol_sum = sum(volumes)
            pv_sum = sum(p * v for p, v in zip(prices, volumes))
            return pv_sum / vol_sum if vol_sum > 0 else 0
        
        # EMA
        def calc_ema(prices, period):
            if len(prices) < period:
                return None
            multiplier = 2 / (period + 1)
            ema = sum(prices[:period]) / period
            for price in prices[period:]:
                ema = (price - ema) * multiplier + ema
            return ema
        
        current = closes[-1]
        
        return {
            'price': current,
            'rsi_5': calc_rsi(closes, 5),
            'rsi_14': calc_rsi(closes, 14),
            'vwap_15': calc_vwap(closes[-15:], volumes[-15:]),
            'ema_9': calc_ema(closes, 9),
            'ema_21': calc_ema(closes, 21),
            'volume': sum(volumes[-5:]),
            'cvd': sum(volumes[-5:]) - sum(volumes[-10:-5])
        }

# ========== DeFi 数据 ==========
class DeFiData:
    """DeFi 数据"""
    
    @staticmethod
    def tvl_chains():
        """各链 TVL"""
        url = "https://api.llama.fi/chains"
        r = requests.get(url, timeout=30)
        return r.json()
    
    @staticmethod
    def protocol_tvl(protocol):
        """协议 TVL 历史"""
        url = f"https://api.llama.fi/protocol/{protocol}"
        r = requests.get(url, timeout=30)
        return r.json()

# ========== Polymarket ==========
class PolymarketData:
    """Polymarket 预测市场"""
    
    @staticmethod
    def get_market(slug):
        """获取市场数据"""
        result = subprocess.run(
            ["polymarket", "markets", "get", slug, "-o", "json"],
            capture_output=True, text=True, timeout=15
        )
        try:
            return json.loads(result.stdout)
        except:
            return None
    
    @staticmethod
    def get_btc_15m_markets():
        """获取 BTC 15分钟市场"""
        import time
        now = int(time.time())
        period = 15 * 60
        current = (now // period) * period
        
        markets = []
        for i in range(3):
            ts = current + i * period
            slug = f"btc-updown-15m-{ts}"
            market = PolymarketData.get_market(slug)
            if market and market.get('active'):
                try:
                    prices = json.loads(market.get('outcomePrices', '[]'))
                    markets.append({
                        'slug': slug,
                        'question': market.get('question'),
                        'up_price': float(prices[0]) if len(prices) > 0 else 0.5,
                        'down_price': float(prices[1]) if len(prices) > 1 else 0.5,
                        'liquidity': float(market.get('liquidity', 0)),
                        'end_date': market.get('end_date_iso')
                    })
                except:
                    pass
        return markets

# ========== 交易所数据 ==========
class ExchangeData:
    """交易所数据"""
    
    @staticmethod
    def binance_orderbook(symbol="BTCUSDT", limit=20):
        """Binance 深度"""
        url = f"https://api.binance.com/api/v3/depth"
        params = {"symbol": symbol, "limit": limit}
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    
    @staticmethod
    def binance_funding(symbol="BTCUSDT"):
        """Binance 资金费率"""
        url = "https://fapi.binance.com/futures/data/fundingRateHistory"
        params = {"symbol": symbol, "limit": 1}
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    
    @staticmethod
    def binance_liquidation(symbol="BTCUSDT"):
        """Binance 爆仓数据 (模拟)"""
        # 实际需要 WebSocket
        return {"note": "需要 WebSocket 实时监控"}


# ========== 主函数 ==========
def main():
    print("=" * 50)
    print("交易工具集 - Trading Tools")
    print("=" * 50)
    
    # 价格
    print("\n📊 价格数据:")
    price = PriceData.binance()
    print(f"  BTC: ${price['price']}")
    
    # K线指标
    print("\n📈 技术指标:")
    klines = KLineData.binance(limit=50)
    indicators = KLineData.calculate_indicators(klines)
    print(f"  价格: ${indicators['price']:,.0f}")
    print(f"  RSI(5): {indicators['rsi_5']:.1f}")
    print(f"  VWAP: ${indicators['vwap_15']:,.0f}")
    print(f"  EMA9/21: {indicators['ema_9']:,.0f} / {indicators['ema_21']:,.0f}")
    
    # Polymarket
    print("\n🎯 Polymarket BTC 15m:")
    markets = PolymarketData.get_btc_15m_markets()
    for m in markets:
        print(f"  {m['slug']}: Up {m['up_price']*100:.1f}% / Down {m['down_price']*100:.1f}%")
        print(f"    流动性: ${m['liquidity']:,.0f}")

if __name__ == "__main__":
    main()
