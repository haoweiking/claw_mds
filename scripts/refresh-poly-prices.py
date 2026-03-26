#!/usr/bin/env python3
"""Refresh Polymarket prices to portfolio."""

import json
import subprocess
import os

PORTFOLIO_PATH = os.path.expanduser("~/.openclaw/workspace/memory/poly-portfolio.json")

def get_market_price(slug: str) -> float | None:
    """Fetch current price for a market via CLI."""
    try:
        result = subprocess.run(
            ["polymarket", "markets", "get", slug, "-o", "json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            # Market might be unavailable (404) or archived
            return None
        data = json.loads(result.stdout)
        # Handle error response
        if isinstance(data, dict) and data.get("error"):
            return None
        # Get the best yes/no price
        outcomes = data.get("outcomes", [])
        if not outcomes:
            return None
        # If there's a YES outcome, return its price
        for outcome in outcomes:
            if outcome.get("title", "").upper() == "YES":
                return float(outcome.get("price", 0))
        # Otherwise return first outcome price
        return float(outcomes[0].get("price", 0))
    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"Error fetching {slug}: {e}")
        return None

def main():
    with open(PORTFOLIO_PATH) as f:
        portfolio = json.load(f)

    # Collect all markets to fetch
    markets = set()
    
    # From positions (open only)
    for pos in portfolio.get("positions", []):
        if pos.get("status") == "open":
            markets.add(pos.get("slug", ""))
    
    # From lastPrices keys
    markets.update(portfolio.get("lastPrices", {}).keys())
    
    # From markets config
    markets.update(portfolio.get("markets", {}).keys())

    print(f"Fetching prices for {len(markets)} markets...")

    new_prices = {}
    for slug in markets:
        price = get_market_price(slug)
        if price is not None:
            new_prices[slug] = price
            print(f"  {slug}: {price:.4f}")
        else:
            # Keep old price if available
            old = portfolio.get("lastPrices", {}).get(slug)
            if old:
                new_prices[slug] = old
                print(f"  {slug}: kept {old:.4f}")

    # Update portfolio
    portfolio["lastPrices"] = new_prices
    
    # Update positions with current prices
    for pos in portfolio.get("positions", []):
        if pos.get("status") == "open":
            slug = pos.get("slug", "")
            if slug in new_prices:
                pos["lastPrice"] = new_prices[slug]

    portfolio["lastCheck"] = f"{subprocess.run(['date', '+%Y-%m-%d %H:%M UTC'], capture_output=True, text=True).stdout.strip()}"

    with open(PORTFOLIO_PATH, "w") as f:
        json.dump(portfolio, f, indent=2)

    print(f"Updated {len(new_prices)} prices")

if __name__ == "__main__":
    main()