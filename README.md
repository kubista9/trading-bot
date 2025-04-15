# NASDAQ Stock Valuation Scanner

## 📌 Overview
This Python script scans NASDAQ-listed stocks and evaluates whether they're undervalued or overvalued based on key financial metrics using the Yahoo Finance API.

## 🛠️ Installation
    pip install yfinance pandas numpy tqdm

## 🚀 How to Run
    python stock_valuation_scanner_NASDAQ.py 

## 📊 Understanding the Output
The script generates a CSV file (`nasdaq_valuation_scan.csv`) with these columns:

1. **P/E** (Price-to-Earnings Ratio)  
   *Measures price relative to earnings*  
   - **<15**: Cheap (value territory)  
   - **15-25**: Fair (market average)  
   - **>25**: Expensive (justified only for high-growth companies)  

2. **P/B** (Price-to-Book Ratio)  
   *Compares market value to accounting book value*  
   - **<1**: Cheap (trading below asset value)  
   - **1-3**: Fair (typical for most industries)  
   - **>3**: Expensive (common for tech/IP-driven firms)  

3. **P/S** (Price-to-Sales Ratio)  
   *Evaluates price relative to revenue*  
   - **<1**: Cheap (often found in turnaround situations)  
   - **1-4**: Fair (healthy companies)  
   - **>4**: Expensive (requires high-profit margins)  

4. **PEG** (Price/Earnings-to-Growth Ratio)  
   *Combines P/E with earnings growth rate*  
   - **<0.8**: Potentially undervalued (growth not priced in)  
   - **0.8-1.5**: Fairly valued  
   - **>2**: Potentially overvalued  

5. **D/E** (Debt-to-Equity Ratio)  
   *Measures financial leverage and risk*  
   - **<0.5**: Low debt (conservative structure)  
   - **0.5-2**: Moderate leverage (industry-dependent)  
   - **>2**: High risk (caution required)  

6. **FCF Yield** (Free Cash Flow Yield)  
   *Shows cash generation relative to market price*  
   - **>8%**: Strong value (rare bargain)  
   - **4-8%**: Attractive (healthy cash flow)  
   - **<4%**: Expensive (unless reinvesting for high growth)  