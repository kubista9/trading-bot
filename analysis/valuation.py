"""Stock valuation analysis logic."""

from utils.api_utils import fetch_stock_data
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

def analyze_stock(ticker, industry_calculator):
    """Analyze a single stock's valuation using dynamic industry averages."""
    info = fetch_stock_data(ticker)
    
    if not info:
        return None
        
    # Get key metrics with fallback values
    pe = info.get('trailingPE', info.get('forwardPE'))
    pb = info.get('priceToBook')
    ps = info.get('priceToSalesTrailing12Months')
    peg = info.get('pegRatio')
    de = info.get('debtToEquity')
    fcf = info.get('freeCashflow')
    market_cap = info.get('marketCap')
    
    # Calculate FCF yield
    fcf_yield = (fcf / market_cap) * 100 if fcf and market_cap and market_cap > 0 else None
    
    # Get industry averages dynamically
    industry_avgs = industry_calculator.get_averages_for_stock(info)
    
    # Prepare valuation data
    valuation = {
        'Ticker': ticker,
        'Name': info.get('shortName', ticker),
        'Sector': info.get('sector', 'N/A'),
        'Industry': info.get('industry', 'N/A'),
        'Price': info.get('currentPrice', 'N/A'),
        'Market Cap': market_cap,
        'P/E': pe,
        'P/B': pb,
        'P/S': ps,
        'PEG': peg,
        'Debt/Equity': de,
        'FCF Yield %': fcf_yield,
        'Industry Avg P/E': industry_avgs.get('pe'),
        'Industry Avg P/B': industry_avgs.get('pb'),
        'Industry Avg P/S': industry_avgs.get('ps'),
        'Assessment': 'Neutral'
    }
    
    # Calculate valuation score
    score = 0
    
    # Evaluate key metrics
    score += evaluate_metric(pe, industry_avgs.get('pe'), VALUATION_THRESHOLDS['pe'])
    score += evaluate_metric(pb, industry_avgs.get('pb'), VALUATION_THRESHOLDS['pb'])
    score += evaluate_metric(ps, industry_avgs.get('ps'), VALUATION_THRESHOLDS['ps'])
    score += evaluate_metric(peg, industry_avgs.get('peg'), VALUATION_THRESHOLDS['peg'])
    
    # Evaluate FCF yield (higher is better)
    if fcf_yield and industry_avgs.get('fcf_yield'):
        if fcf_yield > industry_avgs.get('fcf_yield') * 1.5:
            score += 1
        elif fcf_yield < industry_avgs.get('fcf_yield') * 0.5:
            score -= 1
    elif fcf_yield:
        if fcf_yield > VALUATION_THRESHOLDS['fcf_yield']['undervalued']:
            score += 1
        elif fcf_yield < VALUATION_THRESHOLDS['fcf_yield']['overvalued']:
            score -= 1
    
    # Evaluate debt-to-equity (lower is better)
    if de and industry_avgs.get('de'):
        if de < industry_avgs.get('de') * 0.7:
            score += 0.5
        elif de > industry_avgs.get('de') * 1.3:
            score -= 0.5
    elif de:
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