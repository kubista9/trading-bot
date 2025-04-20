"""Main entry point for the NASDAQ stock valuation scanner."""

import sys
from tqdm import tqdm
from utils.api_utils import get_nasdaq_tickers
from analysis.valuation import analyze_stock
from analysis.industry_metrics import IndustryMetricsCalculator
from utils.data_utils import save_results_to_csv, display_sample_results
from config import OUTPUT_FILE, SAMPLE_SIZE

def scan_nasdaq():
    """Scan all NASDAQ stocks and analyze their valuation."""
    try:
        tickers = get_nasdaq_tickers()
        results = []
        
        # Initialize industry metrics calculator
        industry_calculator = IndustryMetricsCalculator()
        industry_calculator.initialize_with_sample(tickers)
        
        print(f"Scanning {len(tickers)} NASDAQ companies...")
        
        # Process all tickers
        for ticker in tqdm(tickers):
            analysis = analyze_stock(ticker, industry_calculator)
            if analysis:
                results.append(analysis)
        
        # Save results
        if results:
            df = save_results_to_csv(results, OUTPUT_FILE)
            print(f"\nScan complete! Results saved to '{OUTPUT_FILE}'")
            return df
        else:
            print("\nScan completed but no valid results were obtained")
            return None
            
    except Exception as e:
        print(f"\nFatal error during scan: {str(e)}")
        return None