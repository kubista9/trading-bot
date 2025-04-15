import yfinance as yf
import pandas as pd
import numpy as np
from tqdm import tqdm

def get_nasdaq_tickers():
    """Fetch NASDAQ-listed company symbols"""
    url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nasdaq/nasdaq_tickers.txt"
    try:
        nasdaq_tickers = pd.read_csv(url, header=None)[0].tolist()
        return nasdaq_tickers
    except:
        print("Failed to fetch NASDAQ tickers. Using a sample list instead.")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'PYPL', 'ADBE', 'INTC']

def get_industry_averages(ticker):
    """Get industry averages for comparison"""
    stock = yf.Ticker(ticker)
    info = stock.info
    sector = info.get('sector', 'Technology')  # Default to Tech if not available
    industry = info.get('industry', 'General')
    
    # These are simplified industry averages - in reality you'd want a proper database
    industry_averages = {
        'Technology': {'pe': 25, 'pb': 5, 'ps': 6, 'peg': 1.5},
        'Financial Services': {'pe': 15, 'pb': 1.2, 'ps': 3, 'peg': 1.2},
        'Healthcare': {'pe': 22, 'pb': 4, 'ps': 5, 'peg': 1.8},
        'Consumer Cyclical': {'pe': 20, 'pb': 3, 'ps': 1.5, 'peg': 1.5},
        'Communication Services': {'pe': 18, 'pb': 3.5, 'ps': 4, 'peg': 1.3},
        'General': {'pe': 20, 'pb': 3, 'ps': 3, 'peg': 1.5}
    }
    
    return industry_averages.get(sector, industry_averages['General'])

def analyze_stock(ticker):
    """Analyze a single stock's valuation"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get key metrics
        pe = info.get('trailingPE', info.get('forwardPE', None))
        pb = info.get('priceToBook', None)
        ps = info.get('priceToSalesTrailing12Months', None)
        peg = info.get('pegRatio', None)
        de = info.get('debtToEquity', None)
        fcf = info.get('freeCashflow', None)
        market_cap = info.get('marketCap', None)
        
        # Calculate FCF yield if possible
        fcf_yield = (fcf / market_cap) * 100 if fcf and market_cap else None
        
        # Get industry averages
        industry_avgs = get_industry_averages(ticker)
        
        # Valuation assessment
        valuation = {
            'Ticker': ticker,
            'Name': info.get('shortName', ticker),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Price': info.get('currentPrice', 'N/A'),
            'P/E': pe,
            'P/B': pb,
            'P/S': ps,
            'PEG': peg,
            'Debt/Equity': de,
            'FCF Yield %': fcf_yield,
            'Assessment': 'Neutral'
        }
        
        # Evaluate valuation
        score = 0
        
        if pe and industry_avgs['pe']:
            if pe < industry_avgs['pe'] * 0.8: score += 1
            elif pe > industry_avgs['pe'] * 1.2: score -= 1
        
        if pb and industry_avgs['pb']:
            if pb < industry_avgs['pb'] * 0.7: score += 1
            elif pb > industry_avgs['pb'] * 1.3: score -= 1
        
        if ps and industry_avgs['ps']:
            if ps < industry_avgs['ps'] * 0.7: score += 1
            elif ps > industry_avgs['ps'] * 1.3: score -= 1
        
        if peg and industry_avgs['peg']:
            if peg < industry_avgs['peg'] * 0.8: score += 1
            elif peg > industry_avgs['peg'] * 1.2: score -= 1
        
        if fcf_yield:
            if fcf_yield > 5: score += 1
            elif fcf_yield < 2: score -= 1
        
        if de:
            if de < 0.5: score += 0.5
            elif de > 2: score -= 0.5
        
        # Final assessment
        if score >= 2:
            valuation['Assessment'] = 'Undervalued'
        elif score <= -2:
            valuation['Assessment'] = 'Overvalued'
        
        return valuation
    
    except Exception as e:
        print(f"Error analyzing {ticker}: {str(e)}")
        return None

def scan_nasdaq():
    """Scan all NASDAQ stocks and analyze their valuation"""
    tickers = get_nasdaq_tickers()
    results = []
    
    print(f"Scanning {len(tickers)} NASDAQ companies...")
    
    for ticker in tqdm(tickers[:50]):  # Limiting to 50 for demo purposes
        analysis = analyze_stock(ticker)
        if analysis:
            results.append(analysis)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv('nasdaq_valuation_scan.csv', index=False)
    print("\nScan complete! Results saved to 'nasdaq_valuation_scan.csv'")
    
    return df

# Run the scanner
if __name__ == "__main__":
    results_df = scan_nasdaq()
    print("\nSample results:")
    print(results_df[['Ticker', 'Name', 'Assessment', 'P/E', 'P/B', 'P/S']].head(10))