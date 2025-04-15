# NASDAQ Stock Valuation Scanner

## 📌 Overview
This Python script scans NASDAQ-listed stocks and evaluates whether they're undervalued or overvalued based on key financial metrics using the Yahoo Finance API.

## 🛠️ Installation
    pip install yfinance pandas numpy tqdm

## 🚀 How to Run
    python stock_valuation_scanner_NASDAQ.py 

## 📊 Understanding the Output
The script generates a CSV file (nasdaq_valuation_scan.csv) with these columns:

1. **P/E** ( Price-to-Earnings ratio ) 
    - 15 > Cheap 
    - 15 - 25 Fair
    - 25 < Expensive 

2. **P/B** ( Price-to-Book ratio ) 
    - 1 > Cheap
    - 1 - 3 Fair
    - 3 < Expensive

3. **P/S** ( Price-to-Sales ratio )	
    - 1 > Cheap
    - 1 - 4 Fair
    - 4 < Expensive

4. **PEG** ( Price/Earnings-to-Growth + Annual EPS Growth Rate) 

*What It Measures:*
- Whether a stock's price is justified by its earnings growth
- Combines value (P/E) with growth potential

    - 1 > Potentially undervalued
    - 1 - 2 Fairly valued
    - 2 < Potentially overvalued

5. **D/E** ( Debt-to-Equity ratio )
    - 0.5 > Low debt
    - 0.5 - 2 Moderate leverage
    - 2 < High risk 

6. **FCF** ( Free Cash Flow Yield )
    - 8% < Strong value
    - 4 - 8% Attractive
    - 4% > Expensive ( unless high growth )