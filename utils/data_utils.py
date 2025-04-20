# utils/data_utils.py
"""Data processing utilities."""

import pandas as pd

def save_results_to_csv(results, filename):
    """Save analysis results to CSV file."""
    try:
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)
        return df
    except Exception as e:
        print(f"Error saving results to CSV: {str(e)}")
        return pd.DataFrame()

def display_sample_results(df, sample_size=10):
    """Display a sample of the results."""
    if not df.empty:
        print("\nSample results:")
        display_columns = ['Ticker', 'Name', 'Assessment', 'P/E', 'P/B', 'P/S']
        sample = df[display_columns].head(sample_size)
        print(sample)
    else:
        print("No results to display.")