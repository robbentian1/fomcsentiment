#!/usr/bin/env python3
"""
Quick Start Example
Demonstrates basic usage of the FOMC sentiment analysis toolkit
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_collection.fomc_collector import FOMCDataCollector
from sentiment_analysis.sentiment_analyzer import FOMCSentimentAnalyzer


def main():
    print("=" * 80)
    print("FOMC SENTIMENT ANALYSIS - QUICK START EXAMPLE")
    print("=" * 80)
    
    # Step 1: Collect sample FOMC data
    print("\n[1/3] Collecting FOMC documents...")
    collector = FOMCDataCollector(start_date="2020-10-01")
    documents_df = collector.collect_all()
    print(f"✓ Collected {len(documents_df)} documents")
    
    # Display sample
    print("\nSample document:")
    print("-" * 80)
    sample = documents_df.iloc[0]
    print(f"Date: {sample['date']}")
    print(f"Type: {sample['type']}")
    print(f"Title: {sample['title']}")
    print(f"Text preview: {sample['text'][:150]}...")
    
    # Step 2: Analyze sentiment
    print("\n[2/3] Analyzing sentiment...")
    analyzer = FOMCSentimentAnalyzer()
    sentiment_df = analyzer.analyze_dataframe(documents_df)
    print(f"✓ Sentiment analysis complete")
    
    # Display results
    print("\nSentiment Results:")
    print("-" * 80)
    for _, row in sentiment_df.iterrows():
        print(f"\nDate: {row['date']}")
        print(f"Type: {row['type']}")
        print(f"Tone: {row['tone'].upper()}")
        print(f"Weighted Sentiment: {row['weighted_sentiment']:.3f}")
        print(f"Hawkish Score: {row['hawkish_score']:.3f}")
        print(f"Dovish Score: {row['dovish_score']:.3f}")
    
    # Step 3: Summary statistics
    print("\n[3/3] Summary Statistics:")
    print("-" * 80)
    print(f"Total documents analyzed: {len(sentiment_df)}")
    print(f"Average sentiment: {sentiment_df['weighted_sentiment'].mean():.3f}")
    print(f"\nTone distribution:")
    for tone, count in sentiment_df['tone'].value_counts().items():
        print(f"  {tone.capitalize()}: {count}")
    
    # Save results
    output_path = os.path.join("data", "processed", "fomc_sentiment.csv")
    sentiment_df.to_csv(output_path, index=False)
    print(f"\n✓ Results saved to {output_path}")
    
    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run the full pipeline: python src/main.py")
    print("2. Explore results in Jupyter: jupyter notebook notebooks/analysis.ipynb")
    print("3. Customize the analysis by modifying the scripts in src/")


if __name__ == "__main__":
    main()
