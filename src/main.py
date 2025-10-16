"""
Main Analysis Pipeline
Orchestrates the complete FOMC sentiment analysis workflow
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_collection.fomc_collector import FOMCDataCollector
from sentiment_analysis.sentiment_analyzer import FOMCSentimentAnalyzer
from financial_data.market_data import FinancialDataCollector
from correlation_analysis.correlation import CorrelationAnalyzer


def run_full_analysis(start_date: str = "2020-10-01"):
    """
    Run the complete FOMC sentiment analysis pipeline
    
    Args:
        start_date: Start date for analysis (format: YYYY-MM-DD)
    """
    print("="*80)
    print("FOMC SENTIMENT ANALYSIS PIPELINE")
    print("="*80)
    print(f"Start Date: {start_date}")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Step 1: Collect FOMC documents
    print("\n[Step 1/5] Collecting FOMC documents...")
    print("-"*80)
    collector = FOMCDataCollector(start_date=start_date)
    fomc_df = collector.collect_all()
    fomc_path = os.path.join("data", "raw", "fomc_documents.csv")
    collector.save_data(fomc_df, fomc_path)
    print(f"✓ Collected {len(fomc_df)} documents")
    
    # Step 2: Analyze sentiment
    print("\n[Step 2/5] Analyzing FOMC sentiment...")
    print("-"*80)
    analyzer = FOMCSentimentAnalyzer()
    sentiment_df = analyzer.analyze_dataframe(fomc_df)
    sentiment_path = os.path.join("data", "processed", "fomc_sentiment.csv")
    os.makedirs(os.path.dirname(sentiment_path), exist_ok=True)
    sentiment_df.to_csv(sentiment_path, index=False)
    print(f"✓ Sentiment analysis complete")
    print(f"  - Hawkish: {len(sentiment_df[sentiment_df['tone'] == 'hawkish'])}")
    print(f"  - Dovish: {len(sentiment_df[sentiment_df['tone'] == 'dovish'])}")
    print(f"  - Neutral: {len(sentiment_df[sentiment_df['tone'] == 'neutral'])}")
    
    # Step 3: Collect financial data
    print("\n[Step 3/5] Collecting financial market data...")
    print("-"*80)
    fin_collector = FinancialDataCollector(start_date=start_date)
    financial_df = fin_collector.fetch_all_assets()
    
    if not financial_df.empty:
        fin_path = os.path.join("data", "raw", "financial_data.csv")
        fin_collector.save_data(financial_df, fin_path)
        print(f"✓ Collected data for {financial_df['Asset'].nunique()} assets")
        
        # Step 4: Calculate event-window returns
        print("\n[Step 4/5] Calculating event-window returns...")
        print("-"*80)
        event_dates = sentiment_df['date'].tolist()
        event_returns = fin_collector.calculate_event_returns(financial_df, event_dates)
        event_path = os.path.join("data", "processed", "event_returns.csv")
        event_returns.to_csv(event_path, index=False)
        print(f"✓ Calculated returns for {len(event_dates)} events")
        
        # Step 5: Correlation analysis
        print("\n[Step 5/5] Running correlation analysis...")
        print("-"*80)
        corr_analyzer = CorrelationAnalyzer()
        merged_df = corr_analyzer.merge_sentiment_and_returns(sentiment_df, event_returns)
        
        if not merged_df.empty:
            results = corr_analyzer.analyze_by_asset(merged_df)
            summary = corr_analyzer.generate_summary_statistics(merged_df)
            corr_analyzer.save_results(results, summary, "results")
            
            print(f"✓ Correlation analysis complete")
            print(f"\nKey Findings:")
            print(f"  - Total Events Analyzed: {summary['total_events']}")
            print(f"  - Assets Tracked: {summary['total_assets']}")
            print(f"  - Average Sentiment Score: {summary['avg_sentiment']:.3f}")
            
            # Display top correlations
            print(f"\nTop Correlations (Post-Event, 5-day window):")
            top_corr = results[results['window_days'] == 5].nlargest(3, 'post_pearson_r')
            for _, row in top_corr.iterrows():
                print(f"  - {row['asset']}: r={row['post_pearson_r']:.3f}, p={row['post_pearson_p']:.3f}")
        else:
            print("⚠ No matching data found for correlation analysis")
    else:
        print("⚠ No financial data collected (possibly due to network issues)")
        print("  Analysis will continue with sample data")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nResults saved to:")
    print(f"  - {sentiment_path}")
    print(f"  - results/correlation_results.csv")
    print(f"  - results/summary_statistics.csv")
    print("\nTo visualize results, run: jupyter notebook notebooks/analysis.ipynb")


if __name__ == "__main__":
    run_full_analysis(start_date="2020-10-01")
