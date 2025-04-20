# analysis/valuation.py
"""Stock valuation analysis logic."""

from utils.api_utils import fetch_stock_data
from analysis.metrics import get_industry_averages, calculate_fcf_yield
from config import VALUATION_THRESHOLDS

def evaluate_metric(actual, benchmark, thresholds):
    """Evaluate a single metric against benchmark."""
    if actual is None or benchmark is None:
        return 0
    
    if actual < benchmark * thresholds['undervalued']:
        return 1
    elif actual > benchmark * thresholds['overvalued']:
        return -1
    return 0

def analyze_stock(ticker):
    """Analyze a single stock's valuation."""
    info = fetch_stock_data(ticker)
    
    if not info:
        return None
        
    # Get key metrics with fallback values
    pe = info.get('trailingPE', info.get('forwardPE'))
    pb = info.get('priceToBook')
    ps = info.get('priceToSalesTrailing12Months')
    peg = info.get('pegRatio')
    de = info.get('debtToEquity')
    
    # Calculate FCF yield
    fcf_yield = calculate_fcf_yield(info)
    
    # Get industry averages
    industry_avgs = get_industry_averages(info)
    
    # Prepare valuation data
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
    
    # Calculate valuation score
    score = 0
    
    # Evaluate key metrics
    score += evaluate_metric(pe, industry_avgs['pe'], VALUATION_THRESHOLDS['pe'])
    score += evaluate_metric(pb, industry_avgs['pb'], VALUATION_THRESHOLDS['pb'])
    score += evaluate_metric(ps, industry_avgs['ps'], VALUATION_THRESHOLDS['ps'])
    score += evaluate_metric(peg, industry_avgs['peg'], VALUATION_THRESHOLDS['peg'])
    
    # Evaluate FCF yield (higher is better)
    if fcf_yield:
        if fcf_yield > VALUATION_THRESHOLDS['fcf_yield']['undervalued']:
            score += 1
        elif fcf_yield < VALUATION_THRESHOLDS['fcf_yield']['overvalued']:
            score -= 1
    
    # Evaluate debt-to-equity (lower is better)
    if de:
        if de < VALUATION_THRESHOLDS['de']['undervalued']:
            score += 0.5
        elif de > VALUATION_THRESHOLDS['de']['overvalued']:
            score -= 0.5
    
    # Final assessment
    if score >= 2:
        valuation['Assessment'] = 'Undervalued'
    elif score <= -2:
        valuation['Assessment'] = 'Overvalued'
    
    return valuation
