from alpaca_trade_api import REST
api = REST("API_KEY", "API_SECRET", base_url="https://paper-api.alpaca.markets")

# Get Account Balance
account = api.get_account()
print(f"Account Equity: ${account.equity}")

# Place a Market Order (Buying 10 shares of AAPL)
api.submit_order(symbol="AAPL", qty=10, side="buy", type="market", time_in_force="gtc")
