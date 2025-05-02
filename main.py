"""Main entry point for the enhanced NASDAQ stock valuation scanner."""

import sys
from tqdm import tqdm
from utils.api_utils import get_nasdaq_tickers
from analysis.valuation import analyze_stock
from analysis.industry_metrics import IndustryMetricsCalculator
from utils.data_utils import save_results_to_csv, display_sample_results
from config import OUTPUT_FILE, SAMPLE_SIZE

def scan_nasdaq(include_growth=True, include_competitive=True):
    """Scan all NASDAQ stocks with enhanced analysis."""
    try:
        tickers = get_nasdaq_tickers()
        results = []
        
        # Initialize industry metrics calculator
        industry_calculator = IndustryMetricsCalculator()
        industry_calculator.initialize_with_sample(tickers)
        
        print(f"Scanning {len(tickers)} NASDAQ companies...")
        print(f"Growth analysis: {'Enabled' if include_growth else 'Disabled'}")
        print(f"Competitive analysis: {'Enabled' if include_competitive else 'Disabled'}")
        
        # Process all tickers
        for ticker in tqdm(tickers):
            analysis = analyze_stock(ticker, industry_calculator, 
                                    include_growth=include_growth,
                                    include_competitive=include_competitive)
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

if __name__ == "__main__":
    try:
        # Provide command line options to enable/disable features
        # In a real implementation, you'd use argparse to handle command line args
        include_growth = True  # Set to False to speed up scan
        include_competitive = True  # Set to False to speed up scan
        
        results_df = scan_nasdaq(include_growth, include_competitive)
        if results_df is not None:
            display_sample_results(results_df, SAMPLE_SIZE)
    except Exception as e:
        print(f"\nScript failed: {str(e)}")
        sys.exit(1)