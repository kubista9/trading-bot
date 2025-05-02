# analysis/growth_metrics.py
"""Module for analyzing company growth metrics and trends."""

import yfinance as yf
import pandas as pd
import numpy as np
from utils.api_utils import fetch_stock_data
from datetime import datetime, timedelta

class GrowthAnalyzer:
    """Analyzes company growth metrics and historical trends."""
    
    def __init__(self):
        self.industry_growth_rates = {}
    
    def get_historical_financials(self, ticker, years=3):
        """Fetch historical financial data for the given ticker."""
        try:
            stock = yf.Ticker(ticker)
            
            # Get income statement data
            income_stmt = stock.income_stmt
            
            # Get balance sheet data
            balance_sheet = stock.balance_sheet
            
            # Get cash flow data
            cash_flow = stock.cashflow
            
            # If any of these are empty, return None
            if income_stmt.empty or balance_sheet.empty or cash_flow.empty:
                return None
                
            return {
                'income_stmt': income_stmt,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow
            }
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {str(e)}")
            return None
    
    def calculate_growth_metrics(self, ticker):
        """Calculate comprehensive growth metrics for a company."""
        financials = self.get_historical_financials(ticker)
        current_data = fetch_stock_data(ticker)
        
        if not financials or not current_data:
            return {}
        
        growth_metrics = {}
        
        try:
            # Income statement metrics
            income = financials['income_stmt']
            
            # Calculate revenue growth rates
            if 'TotalRevenue' in income.index:
                revenues = income.loc['TotalRevenue']
                revenue_growth = {}
                
                # Annual growth rates
                for i in range(1, min(4, len(revenues))):
                    if revenues.iloc[i-1] and revenues.iloc[i]:
                        year_growth = ((revenues.iloc[i-1] / revenues.iloc[i]) - 1) * 100
                        year = str(revenues.columns[i-1].year)
                        revenue_growth[f'revenue_growth_{year}'] = year_growth
                
                # 3-year CAGR if available
                if len(revenues) >= 3:
                    latest = revenues.iloc[0]
                    oldest = revenues.iloc[min(3, len(revenues)-1)]
                    if latest and oldest:
                        cagr = ((latest / oldest) ** (1 / min(3, len(revenues)-1)) - 1) * 100
                        revenue_growth['revenue_cagr_3yr'] = cagr
                
                growth_metrics.update(revenue_growth)
            
            # Calculate earnings growth rates
            if 'NetIncome' in income.index:
                earnings = income.loc['NetIncome']
                earnings_growth = {}
                
                # Annual growth rates
                for i in range(1, min(4, len(earnings))):
                    if earnings.iloc[i-1] and earnings.iloc[i] and earnings.iloc[i] != 0:
                        year_growth = ((earnings.iloc[i-1] / earnings.iloc[i]) - 1) * 100
                        year = str(earnings.columns[i-1].year)
                        earnings_growth[f'earnings_growth_{year}'] = year_growth
                
                # 3-year CAGR if available
                if len(earnings) >= 3:
                    latest = earnings.iloc[0]
                    oldest = earnings.iloc[min(3, len(earnings)-1)]
                    # Only calculate if both values are positive to avoid misleading CAGR
                    if latest > 0 and oldest > 0:
                        cagr = ((latest / oldest) ** (1 / min(3, len(earnings)-1)) - 1) * 100
                        earnings_growth['earnings_cagr_3yr'] = cagr
                
                growth_metrics.update(earnings_growth)
            
            # Calculate margin trends
            if 'GrossProfit' in income.index and 'TotalRevenue' in income.index:
                gross_margins = {}
                revenues = income.loc['TotalRevenue']
                gross_profits = income.loc['GrossProfit']
                
                for i in range(min(4, len(revenues))):
                    if revenues.iloc[i] and revenues.iloc[i] != 0:
                        margin = (gross_profits.iloc[i] / revenues.iloc[i]) * 100
                        year = str(revenues.columns[i].year)
                        gross_margins[f'gross_margin_{year}'] = margin
                
                # Calculate margin trend (positive is expanding, negative is contracting)
                if len(gross_margins) >= 2:
                    years = sorted(list(gross_margins.keys()))
                    margin_trend = gross_margins[years[0]] - gross_margins[years[-1]]
                    growth_metrics['gross_margin_trend'] = margin_trend
                
                growth_metrics.update(gross_margins)
            
            # Calculate operating margin trends
            if 'OperatingIncome' in income.index and 'TotalRevenue' in income.index:
                op_margins = {}
                revenues = income.loc['TotalRevenue']
                op_incomes = income.loc['OperatingIncome']
                
                for i in range(min(4, len(revenues))):
                    if revenues.iloc[i] and revenues.iloc[i] != 0:
                        margin = (op_incomes.iloc[i] / revenues.iloc[i]) * 100
                        year = str(revenues.columns[i].year)
                        op_margins[f'operating_margin_{year}'] = margin
                
                # Calculate margin trend
                if len(op_margins) >= 2:
                    years = sorted(list(op_margins.keys()))
                    margin_trend = op_margins[years[0]] - op_margins[years[-1]]
                    growth_metrics['operating_margin_trend'] = margin_trend
                
                growth_metrics.update(op_margins)
            
            # Balance sheet metrics
            balance = financials['balance_sheet']
            
            # Calculate Return on Equity trend
            if 'TotalAssets' in balance.index and 'TotalLiabilities' in balance.index and 'NetIncome' in income.index:
                roe_values = {}
                assets = balance.loc['TotalAssets']
                liabilities = balance.loc['TotalLiabilities']
                earnings = income.loc['NetIncome']
                
                for i in range(min(4, len(assets))):
                    if i < len(earnings):  # Make sure we have matching earnings data
                        equity = assets.iloc[i] - liabilities.iloc[i]
                        if equity and equity > 0:
                            roe = (earnings.iloc[i] / equity) * 100
                            year = str(assets.columns[i].year)
                            roe_values[f'roe_{year}'] = roe
                
                # Calculate ROE trend
                if len(roe_values) >= 2:
                    years = sorted(list(roe_values.keys()))
                    roe_trend = roe_values[years[0]] - roe_values[years[-1]]
                    growth_metrics['roe_trend'] = roe_trend
                
                growth_metrics.update(roe_values)
            
            # Cash flow metrics
            cash_flow = financials['cash_flow']
            
            # Calculate Free Cash Flow growth
            if 'FreeCashFlow' in cash_flow.index:
                fcf = cash_flow.loc['FreeCashFlow']
                fcf_growth = {}
                
                for i in range(1, min(4, len(fcf))):
                    if fcf.iloc[i-1] and fcf.iloc[i] and fcf.iloc[i] != 0:
                        year_growth = ((fcf.iloc[i-1] / fcf.iloc[i]) - 1) * 100
                        year = str(fcf.columns[i-1].year)
                        fcf_growth[f'fcf_growth_{year}'] = year_growth
                
                # 3-year CAGR if available
                if len(fcf) >= 3:
                    latest = fcf.iloc[0]
                    oldest = fcf.iloc[min(3, len(fcf)-1)]
                    # Only calculate if both values are positive
                    if latest > 0 and oldest > 0:
                        cagr = ((latest / oldest) ** (1 / min(3, len(fcf)-1)) - 1) * 100
                        fcf_growth['fcf_cagr_3yr'] = cagr
                
                growth_metrics.update(fcf_growth)
            
            # Add overall growth score based on available metrics
            growth_score = self._calculate_growth_score(growth_metrics)
            growth_metrics['growth_score'] = growth_score
            
            return growth_metrics
            
        except Exception as e:
            print(f"Error calculating growth metrics for {ticker}: {str(e)}")
            return {}
    
    def _calculate_growth_score(self, metrics):
        """Calculate an overall growth score from the metrics."""
        score = 0
        factors = 0
        
        # Revenue growth
        if 'revenue_cagr_3yr' in metrics:
            factors += 1
            if metrics['revenue_cagr_3yr'] > 15:
                score += 2  # Strong growth
            elif metrics['revenue_cagr_3yr'] > 7:
                score += 1  # Good growth
            elif metrics['revenue_cagr_3yr'] < 0:
                score -= 1  # Negative growth
        
        # Earnings growth
        if 'earnings_cagr_3yr' in metrics:
            factors += 1
            if metrics['earnings_cagr_3yr'] > 20:
                score += 2  # Strong growth
            elif metrics['earnings_cagr_3yr'] > 10:
                score += 1  # Good growth
            elif metrics['earnings_cagr_3yr'] < 0:
                score -= 1  # Negative growth
        
        # Margin trends
        if 'gross_margin_trend' in metrics:
            factors += 1
            if metrics['gross_margin_trend'] > 3:
                score += 2  # Strong expansion
            elif metrics['gross_margin_trend'] > 1:
                score += 1  # Good expansion
            elif metrics['gross_margin_trend'] < -1:
                score -= 1  # Contraction
        
        if 'operating_margin_trend' in metrics:
            factors += 1
            if metrics['operating_margin_trend'] > 2:
                score += 2  # Strong expansion
            elif metrics['operating_margin_trend'] > 0.5:
                score += 1  # Good expansion
            elif metrics['operating_margin_trend'] < -0.5:
                score -= 1  # Contraction
        
        # ROE trend
        if 'roe_trend' in metrics:
            factors += 1
            if metrics['roe_trend'] > 5:
                score += 2  # Strong improvement
            elif metrics['roe_trend'] > 2:
                score += 1  # Good improvement
            elif metrics['roe_trend'] < -2:
                score -= 1  # Deterioration
        
        # FCF growth
        if 'fcf_cagr_3yr' in metrics:
            factors += 1
            if metrics['fcf_cagr_3yr'] > 20:
                score += 2  # Strong growth
            elif metrics['fcf_cagr_3yr'] > 10:
                score += 1  # Good growth
            elif metrics['fcf_cagr_3yr'] < 0:
                score -= 1  # Negative growth
        
        # Normalize score based on available factors
        if factors > 0:
            normalized_score = score / factors
            # Scale to a range from -5 to 5
            return round(normalized_score * 5, 1)
        else:
            return 0