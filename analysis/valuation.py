"""Enhanced stock valuation analysis logic with growth and competitive analysis."""

from utils.api_utils import fetch_stock_data
from analysis.growth_metrics import GrowthAnalyzer
from analysis.competitive_analysis import CompetitiveAnalyzer
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

def analyze_stock(ticker, industry_calculator, include_growth=True, include_competitive=True):
    """Analyze a stock's valuation with enhanced metrics."""
    info = fetch_stock_data(ticker)
    
    if not info:
        return None
        
    # Initialize analyzers if needed
    growth_analyzer = GrowthAnalyzer() if include_growth else None
    competitive_analyzer = CompetitiveAnalyzer() if include_competitive else None
    
    # Get basic financial metrics
    pe = info.get('trailingPE', info.get('forwardPE'))
    pb = info.get('priceToBook')
    ps = info.get('priceToSalesTrailing12Months')
    peg = info.get('pegRatio')
    de = info.get('debtToEquity')
    fcf = info.get('freeCashflow')
    market_cap = info.get('marketCap')
    
    # Calculate FCF yield
    fcf_yield = (fcf / market_cap) * 100 if fcf and market_cap and market_cap > 0 else None
    
    # Get industry averages
    industry_avgs = industry_calculator.get_averages_for_stock(info)
    
    # Get growth metrics if requested
    growth_metrics = {}
    if include_growth:
        growth_metrics = growth_analyzer.calculate_growth_metrics(ticker)
    
    # Get competitive metrics if requested
    competitive_metrics = {}
    if include_competitive:
        competitive_metrics = competitive_analyzer.get_competitive_metrics(ticker)
    
    # Prepare valuation data (basic metrics)
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
    }
    
    # Add growth metrics
    if growth_metrics:
        valuation.update({
            'Revenue Growth 3Y CAGR': growth_metrics.get('revenue_cagr_3yr'),
            'Earnings Growth 3Y CAGR': growth_metrics.get('earnings_cagr_3yr'),
            'Gross Margin Trend': growth_metrics.get('gross_margin_trend'),
            'Operating Margin Trend': growth_metrics.get('operating_margin_trend'),
            'ROE Trend': growth_metrics.get('roe_trend'),
            'Growth Score': growth_metrics.get('growth_score'),
        })
    
    # Add competitive metrics
    if competitive_metrics:
        valuation.update({
            'Market Share %': competitive_metrics.get('market_share'),
            'Relative P/E': competitive_metrics.get('relative_pe'),
            'Relative Margins': competitive_metrics.get('relative_margins'),
            'Competitive Position': competitive_metrics.get('moat_score'),
        })
    
    # Calculate valuation score (basic)
    score = 0
    
    # Evaluate key valuation metrics
    score += evaluate_metric(pe, industry_avgs.get('pe'), VALUATION_THRESHOLDS['pe'])
    score += evaluate_metric(pb, industry_avgs.get('pb'), VALUATION_THRESHOLDS['pb'])
    score += evaluate_metric(ps, industry_avgs.get('ps'), VALUATION_THRESHOLDS['ps'])
    score += evaluate_metric(peg, industry_avgs.get('peg'), VALUATION_THRESHOLDS['peg'])
    
    # Evaluate FCF yield
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
    
    # Evaluate debt-to-equity
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
    
    # Add growth factors to score
    if 'growth_score' in valuation and valuation['Growth Score'] is not None:
        growth_score = valuation['Growth Score']
        # Scale growth score contribution to overall score
        if growth_score > 3:
            score += 1.5
        elif growth_score > 1:
            score += 1
        elif growth_score < -1:
            score -= 1
    
    # Add competitive position to score
    if 'Competitive Position' in valuation and valuation['Competitive Position'] is not None:
        moat_score = valuation['Competitive Position']
        if moat_score > 3.5:
            score += 1.5
        elif moat_score > 2.5:
            score += 1
    
    # If valuation seems fair but growth and moat are strong, adjust score up
    if score == 0 and 'Growth Score' in valuation and 'Competitive Position' in valuation:
        if (valuation['Growth Score'] or 0) + (valuation['Competitive Position'] or 0) > 7:
            score += 1
    
    # Final assessment with consideration for growth and competitive position
    valuation['Valuation Score'] = round(score, 1)
    
    if score >= 3:
        valuation['Assessment'] = 'Strongly Undervalued'
    elif score >= 1.5:
        valuation['Assessment'] = 'Undervalued'
    elif score <= -3:
        valuation['Assessment'] = 'Strongly Overvalued'
    elif score <= -1.5:
        valuation['Assessment'] = 'Overvalued'
    else:
        valuation['Assessment'] = 'Fair Value'
    
    return valuation