"""Module for analyzing company competitive positioning."""

import yfinance as yf
import pandas as pd
import numpy as np
from utils.api_utils import fetch_stock_data
import math

class CompetitiveAnalyzer:
    """Analyzes company's competitive position against industry peers."""
    
    def __init__(self):
        self.industry_peers = {}
        self.industry_data = {}
    
    def find_peers(self, ticker, sector, industry):
        """Find industry peers for comparison."""
        # Use cached peers if already identified
        peer_key = f"{sector}_{industry}".replace(" ", "_")
        if peer_key in self.industry_peers:
            return self.industry_peers[peer_key]
        
        # Otherwise, get peers from Yahoo Finance
        try:
            stock = yf.Ticker(ticker)
            peer_tickers = stock.info.get('peersList', [])
            
            # If Yahoo doesn't provide peers, use empty list
            # In a full implementation, you'd want to lookup peers some other way
            self.industry_peers[peer_key] = peer_tickers
            return peer_tickers
        except Exception as e:
            print(f"Error finding peers for {ticker}: {str(e)}")
            return []
    
    def get_competitive_metrics(self, ticker):
        """Analyze competitive position metrics for a company."""
        info = fetch_stock_data(ticker)
        
        if not info:
            return {}
        
        sector = info.get('sector', 'Unknown')
        industry = info.get('industry', 'Unknown')
        
        # Find industry peers
        peers = self.find_peers(ticker, sector, industry)
        
        # Create empty result dict
        competitive_metrics = {
            'sector': sector,
            'industry': industry,
            'peer_count': len(peers),
            'market_share': None,
            'relative_pe': None,
            'relative_growth': None,
            'relative_margins': None,
            'relative_roe': None,
            'moat_score': None
        }
        
        # If we couldn't find peers, return limited analysis
        if not peers:
            competitive_metrics['moat_score'] = self._calculate_moat_score(info)
            return competitive_metrics
        
        # Get peer data
        peer_data = self._get_peer_data(peers)
        if not peer_data or len(peer_data) == 0:
            competitive_metrics['moat_score'] = self._calculate_moat_score(info)
            return competitive_metrics
        
        # Calculate market share if market cap data is available
        if 'marketCap' in info and info['marketCap']:
            total_market_cap = sum([p.get('marketCap', 0) for p in peer_data.values() if p.get('marketCap')])
            total_market_cap += info['marketCap']
            if total_market_cap > 0:
                competitive_metrics['market_share'] = (info['marketCap'] / total_market_cap) * 100
        
        # Calculate relative valuation metrics
        competitive_metrics.update(self._calculate_relative_metrics(info, peer_data))
        
        # Calculate moat score
        competitive_metrics['moat_score'] = self._calculate_moat_score(info)
        
        return competitive_metrics
    
    def _get_peer_data(self, peer_tickers):
        """Fetch data for peer companies."""
        peer_data = {}
        
        for ticker in peer_tickers:
            info = fetch_stock_data(ticker)
            if info:
                peer_data[ticker] = info
                
        return peer_data
    
    def _calculate_relative_metrics(self, company_info, peer_data):
        """Calculate company metrics relative to peers."""
        metrics = {}
        
        # Function to safely get the median value of a metric across peers
        def get_peer_median(metric_name):
            values = [p.get(metric_name) for p in peer_data.values() 
                      if p.get(metric_name) is not None and not math.isnan(p.get(metric_name, float('nan')))]
            if values:
                return np.median(values)
            return None
        
        # Relative P/E ratio
        company_pe = company_info.get('trailingPE', company_info.get('forwardPE'))
        peer_median_pe = get_peer_median('trailingPE')
        if peer_median_pe is None:
            peer_median_pe = get_peer_median('forwardPE')
        
        if company_pe is not None and peer_median_pe is not None and peer_median_pe != 0:
            metrics['relative_pe'] = company_pe / peer_median_pe
        
        # Relative profit margins
        company_margin = company_info.get('profitMargins')
        peer_median_margin = get_peer_median('profitMargins')
        
        if company_margin is not None and peer_median_margin is not None and peer_median_margin != 0:
            metrics['relative_margins'] = company_margin / peer_median_margin
        
        # Relative ROE
        company_roe = company_info.get('returnOnEquity')
        peer_median_roe = get_peer_median('returnOnEquity')
        
        if company_roe is not None and peer_median_roe is not None and peer_median_roe != 0:
            metrics['relative_roe'] = company_roe / peer_median_roe
        
        # Relative expected growth (earnings growth)
        company_growth = company_info.get('earningsGrowth')
        peer_median_growth = get_peer_median('earningsGrowth')
        
        if company_growth is not None and peer_median_growth is not None and peer_median_growth != 0:
            metrics['relative_growth'] = company_growth / peer_median_growth
        
        return metrics
    
    def _calculate_moat_score(self, info):
        """Calculate an economic moat score based on available metrics."""
        score = 0
        metrics_count = 0
        
        # High gross margins often indicate pricing power / strong brand
        if info.get('grossMargins') is not None:
            metrics_count += 1
            if info['grossMargins'] > 0.50:  # > 50%
                score += 2
            elif info['grossMargins'] > 0.35:  # > 35%
                score += 1
        
        # High ROE indicates a strong competitive position
        if info.get('returnOnEquity') is not None:
            metrics_count += 1
            if info['returnOnEquity'] > 0.25:  # > 25%
                score += 2
            elif info['returnOnEquity'] > 0.15:  # > 15%
                score += 1
        
        # High profit margins indicate competitive advantage
        if info.get('profitMargins') is not None:
            metrics_count += 1
            if info['profitMargins'] > 0.20:  # > 20%
                score += 2
            elif info['profitMargins'] > 0.10:  # > 10%
                score += 1
        
        # Market dominance (based on market cap - imperfect but available)
        if info.get('marketCap') is not None:
            metrics_count += 1
            if info['marketCap'] > 100e9:  # > $100B
                score += 2
            elif info['marketCap'] > 10e9:  # > $10B
                score += 1
        
        # Normalization
        if metrics_count > 0:
            normalized_score = (score / metrics_count) * 5  # Scale to 0-5 range
            return round(normalized_score, 1)
        else:
            return None