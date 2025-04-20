# analysis/industry_metrics.py
"""Module for dynamically calculating industry average metrics."""

import pandas as pd
import numpy as np
from utils.api_utils import fetch_stock_data
from tqdm import tqdm
import time
from random import uniform
from config import MIN_DELAY, MAX_DELAY

class IndustryMetricsCalculator:
    """Calculates and manages industry average metrics dynamically."""
    
    def __init__(self):
        self.industry_data = {}
        self.sector_data = {}
        self.is_initialized = False
    
    def initialize_with_sample(self, tickers, sample_size=100):
        """Initialize industry averages using a sample of stocks from each sector/industry."""
        print(f"Calculating industry averages from a sample of stocks...")
        
        # Group tickers by sector/industry first
        sector_industry_map = {}
        ticker_data = {}
        
        # First pass - collect sector/industry info
        for ticker in tqdm(tickers[:min(500, len(tickers))], desc="Collecting sector data"):
            try:
                time.sleep(uniform(MIN_DELAY/2, MAX_DELAY/2))  # Reduced delay for this scan
                info = fetch_stock_data(ticker)
                if not info:
                    continue
                
                sector = info.get('sector')
                industry = info.get('industry')
                
                if not sector or not industry:
                    continue
                    
                if sector not in sector_industry_map:
                    sector_industry_map[sector] = {}
                
                if industry not in sector_industry_map[sector]:
                    sector_industry_map[sector][industry] = []
                
                sector_industry_map[sector][industry].append(ticker)
                ticker_data[ticker] = {
                    'sector': sector,
                    'industry': industry
                }
                
            except Exception as e:
                print(f"Error collecting sector data for {ticker}: {str(e)}")
        
        # Select sample tickers from each sector/industry
        sample_tickers = []
        for sector, industries in sector_industry_map.items():
            sector_tickers = []
            for industry, ind_tickers in industries.items():
                # Take up to sample_size/len(industries) tickers from each industry
                industry_sample_size = max(5, min(20, int(sample_size / len(industries))))
                industry_sample = ind_tickers[:min(industry_sample_size, len(ind_tickers))]
                sector_tickers.extend(industry_sample)
            sample_tickers.extend(sector_tickers)
        
        # Second pass - collect financial metrics for sample tickers
        metrics_data = []
        for ticker in tqdm(sample_tickers, desc="Collecting financial metrics"):
            try:
                time.sleep(uniform(MIN_DELAY/2, MAX_DELAY/2))
                info = fetch_stock_data(ticker)
                if not info:
                    continue
                
                # Get key metrics
                pe = info.get('trailingPE', info.get('forwardPE'))
                pb = info.get('priceToBook')
                ps = info.get('priceToSalesTrailing12Months')
                peg = info.get('pegRatio')
                de = info.get('debtToEquity')
                fcf = info.get('freeCashflow')
                market_cap = info.get('marketCap')
                
                # Calculate FCF yield
                fcf_yield = (fcf / market_cap) * 100 if fcf and market_cap and market_cap > 0 else None
                
                # Add to metrics data
                metrics_data.append({
                    'ticker': ticker,
                    'sector': ticker_data[ticker]['sector'],
                    'industry': ticker_data[ticker]['industry'],
                    'pe': pe,
                    'pb': pb,
                    'ps': ps,
                    'peg': peg,
                    'de': de,
                    'fcf_yield': fcf_yield,
                    'market_cap': market_cap
                })
                
            except Exception as e:
                print(f"Error collecting metrics for {ticker}: {str(e)}")
        
        # Calculate industry averages
        df = pd.DataFrame(metrics_data)
        
        # Function to calculate trimmed mean (removes outliers)
        def trimmed_mean(series):
            if series.count() < 3:  # Not enough data
                return series.mean()
            
            # Filter out NaN values
            valid_values = series.dropna()
            if len(valid_values) < 3:
                return valid_values.mean()
                
            # Trim extreme values (remove top and bottom 10%)
            q_low, q_high = valid_values.quantile([0.1, 0.9])
            trimmed = valid_values[(valid_values >= q_low) & (valid_values <= q_high)]
            return trimmed.mean()
        
        # Calculate industry averages
        industry_averages = df.groupby('industry').agg({
            'pe': trimmed_mean,
            'pb': trimmed_mean,
            'ps': trimmed_mean,
            'peg': trimmed_mean,
            'de': trimmed_mean,
            'fcf_yield': trimmed_mean
        })
        
        # Calculate sector averages
        sector_averages = df.groupby('sector').agg({
            'pe': trimmed_mean,
            'pb': trimmed_mean,
            'ps': trimmed_mean,
            'peg': trimmed_mean,
            'de': trimmed_mean,
            'fcf_yield': trimmed_mean
        })
        
        # Convert to dictionaries for easy access
        self.industry_data = industry_averages.to_dict('index')
        self.sector_data = sector_averages.to_dict('index')
        
        # General market averages (fallback)
        self.market_averages = {
            'pe': trimmed_mean(df['pe']),
            'pb': trimmed_mean(df['pb']),
            'ps': trimmed_mean(df['ps']),
            'peg': trimmed_mean(df['peg']),
            'de': trimmed_mean(df['de']),
            'fcf_yield': trimmed_mean(df['fcf_yield'])
        }
        
        self.is_initialized = True
        
        # Save averages to CSV for reference
        industry_averages.to_csv('industry_averages.csv')
        sector_averages.to_csv('sector_averages.csv')
        
        print(f"Industry averages calculated from {len(metrics_data)} companies across {len(industry_averages)} industries.")
        return self.industry_data, self.sector_data
    
    def get_averages_for_stock(self, stock_info):
        """Get the appropriate industry averages for a stock."""
        if not self.is_initialized:
            # Return default values if not initialized
            return {
                'pe': 20, 'pb': 3, 'ps': 3, 'peg': 1.5, 
                'de': 1.0, 'fcf_yield': 3.0
            }
        
        industry = stock_info.get('industry')
        sector = stock_info.get('sector')
        
        # Try to get industry averages first
        if industry and industry in self.industry_data:
            return self.industry_data[industry]
        
        # Fall back to sector averages
        if sector and sector in self.sector_data:
            return self.sector_data[sector]
        
        # Ultimate fallback to market averages
        return self.market_averages