# NASDAQ Stock Valuation Scanner

## 📌 Overview
This Python script scans NASDAQ-listed stocks and evaluates whether they're undervalued or overvalued based on key financial metrics using the Yahoo Finance API.

## 🛠️ Installation
    pip install yfinance pandas numpy tqdm

## 🚀 How to Run
    python stock_valuation_scanner_NASDAQ.py 

## 📊 Understanding the Output
The script generates a CSV file (nasdaq_valuation_scan.csv) with these columns:

Column      Description	                Interpretation Guide
Ticker      Stock symbol	            NASDAQ trading symbol
Name        Company name	            Short name of the company
Assessment	Valuation conclusion	    Undervalued/Neutral/Overvalued
P/E	        Price-to-Earnings ratio	    <15=Cheap, 15-25=Fair, >25=Expensive
P/B	        Price-to-Book ratio     	<1=Cheap, 1-3=Fair, >3=Expensive
P/S	        Price-to-Sales ratio	    <1=Cheap, 1-4=Fair, >4=Expensive