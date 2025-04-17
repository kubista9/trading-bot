# analysis/metrics.py
"""Financial metrics calculations."""

from config import INDUSTRY_AVERAGES

def get_industry_averages(stock_info):
    """Get industry averages for comparison."""
    sector = stock_info.get('sector', 'Technology')
    return INDUSTRY_AVERAGES.get(sector, INDUSTRY_AVERAGES['General'])

def calculate_fcf_yield(stock_info):
    """Calculate Free Cash Flow yield."""
    fcf = stock_info.get('freeCashflow')
    market_cap = stock_info.get('marketCap')
    
    if fcf and market_cap and market_cap > 0:
        return (fcf / market_cap) * 100
    return None