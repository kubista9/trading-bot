# utils/api_utils.py
"""API utilities for fetching stock data."""

import requests
import time
from random import uniform
import yfinance as yf
from config import NASDAQ_API_URL, API_HEADERS, MIN_DELAY, MAX_DELAY

def get_nasdaq_tickers():
    """Fetch live NASDAQ symbols from NASDAQ API."""
    try:
        response = requests.get(NASDAQ_API_URL, headers=API_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and 'table' in data['data'] and 'rows' in data['data']['table']:
            # Filter out tickers with special characters that might cause issues
            return [row['symbol'] for row in data['data']['table']['rows'] 
                   if isinstance(row['symbol'], str) 
                   and len(row['symbol']) <= 5  # Exclude long symbols
                   and not any(c in row['symbol'] for c in ['/', '^', '$'])]  # Exclude symbols with special chars
        else:
            raise ValueError("Unexpected API response structure")
            
    except Exception as e:
        print(f"Failed to fetch NASDAQ tickers: {str(e)}")
        raise

def fetch_stock_data(ticker):
    """Fetch detailed stock data with rate limiting."""
    try:
        # Add random delay to avoid rate limiting
        time.sleep(uniform(MIN_DELAY, MAX_DELAY))
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return None