# config.py
"""Configuration settings for the stock valuation scanner."""

# API settings
NASDAQ_API_URL = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000"
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.nasdaq.com',
    'Referer': 'https://www.nasdaq.com/',
}

# API call delay range in seconds
MIN_DELAY = 0.5
MAX_DELAY = 1.5

# Industry average metrics
INDUSTRY_AVERAGES = {
    'Technology': {'pe': 25, 'pb': 5, 'ps': 6, 'peg': 1.5},
    'Financial Services': {'pe': 15, 'pb': 1.2, 'ps': 3, 'peg': 1.2},
    'Healthcare': {'pe': 22, 'pb': 4, 'ps': 5, 'peg': 1.8},
    'Consumer Cyclical': {'pe': 20, 'pb': 3, 'ps': 1.5, 'peg': 1.5},
    'Communication Services': {'pe': 18, 'pb': 3.5, 'ps': 4, 'peg': 1.3},
    'General': {'pe': 20, 'pb': 3, 'ps': 3, 'peg': 1.5}
}

# Valuation thresholds
VALUATION_THRESHOLDS = {
    'pe': {'undervalued': 0.8, 'overvalued': 1.2},
    'pb': {'undervalued': 0.7, 'overvalued': 1.3},
    'ps': {'undervalued': 0.7, 'overvalued': 1.3},
    'peg': {'undervalued': 0.8, 'overvalued': 1.2},
    'fcf_yield': {'undervalued': 5, 'overvalued': 2},
    'de': {'undervalued': 0.5, 'overvalued': 2}
}

# Output settings
OUTPUT_FILE = 'nasdaq_valuation_scan.csv'
SAMPLE_SIZE = 10