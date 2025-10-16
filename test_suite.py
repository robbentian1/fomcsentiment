#!/usr/bin/env python3
"""
Test Suite for FOMC Sentiment Analysis
Validates core functionality of the analysis modules
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_collection.fomc_collector import FOMCDataCollector
from sentiment_analysis.sentiment_analyzer import FOMCSentimentAnalyzer


def test_data_collection():
    """Test FOMC data collection"""
    print("\n[Test 1] Data Collection")
    print("-" * 60)
    
    collector = FOMCDataCollector(start_date="2020-10-01")
    df = collector.collect_all()
    
    # Validate
    assert len(df) > 0, "Should collect at least one document"
    assert 'date' in df.columns, "Should have date column"
    assert 'type' in df.columns, "Should have type column"
    assert 'text' in df.columns, "Should have text column"
    assert set(df['type'].unique()).issubset({'statement', 'minutes', 'speech'}), \
        "Types should be statement, minutes, or speech"
    
    print(f"✓ Collected {len(df)} documents")
    print(f"✓ Document types: {df['type'].unique().tolist()}")
    print("✓ PASSED")
    
    return df


def test_sentiment_analysis(df):
    """Test sentiment analysis"""
    print("\n[Test 2] Sentiment Analysis")
    print("-" * 60)
    
    analyzer = FOMCSentimentAnalyzer()
    
    # Test single document analysis
    sample_text = "The Federal Reserve remains committed to bringing inflation back to our 2 percent goal"
    result = analyzer.analyze_document(sample_text, 'statement')
    
    assert 'hawkish_score' in result, "Should have hawkish score"
    assert 'dovish_score' in result, "Should have dovish score"
    assert 'net_sentiment' in result, "Should have net sentiment"
    assert 'tone' in result, "Should have tone classification"
    
    print(f"✓ Single document analysis works")
    print(f"  Sample text: '{sample_text[:50]}...'")
    print(f"  Tone: {result['tone']}, Sentiment: {result['net_sentiment']:.3f}")
    
    # Test DataFrame analysis
    sentiment_df = analyzer.analyze_dataframe(df)
    
    assert len(sentiment_df) == len(df), "Should analyze all documents"
    assert 'weighted_sentiment' in sentiment_df.columns, "Should have weighted sentiment"
    assert 'tone' in sentiment_df.columns, "Should have tone"
    
    print(f"✓ DataFrame analysis works")
    print(f"✓ Analyzed {len(sentiment_df)} documents")
    print(f"✓ PASSED")
    
    return sentiment_df


def test_hawkish_dovish_detection():
    """Test hawkish/dovish keyword detection"""
    print("\n[Test 3] Hawkish/Dovish Detection")
    print("-" * 60)
    
    analyzer = FOMCSentimentAnalyzer()
    
    # Test hawkish text
    hawkish_text = "We need to raise interest rates to combat persistent inflation and maintain a restrictive stance"
    hawkish_result = analyzer.analyze_document(hawkish_text, 'statement')
    
    assert hawkish_result['hawkish_score'] > 0, "Should detect hawkish keywords"
    assert hawkish_result['net_sentiment'] > 0, "Net sentiment should be positive (hawkish)"
    
    print(f"✓ Hawkish text detected correctly")
    print(f"  Text: '{hawkish_text[:50]}...'")
    print(f"  Hawkish score: {hawkish_result['hawkish_score']:.3f}")
    print(f"  Tone: {hawkish_result['tone']}")
    
    # Test dovish text
    dovish_text = "We will lower rates to support economic growth and ease financial conditions with patient approach"
    dovish_result = analyzer.analyze_document(dovish_text, 'statement')
    
    assert dovish_result['dovish_score'] > 0, "Should detect dovish keywords"
    assert dovish_result['net_sentiment'] < 0, "Net sentiment should be negative (dovish)"
    
    print(f"✓ Dovish text detected correctly")
    print(f"  Text: '{dovish_text[:50]}...'")
    print(f"  Dovish score: {dovish_result['dovish_score']:.3f}")
    print(f"  Tone: {dovish_result['tone']}")
    
    print("✓ PASSED")


def test_document_type_weighting():
    """Test that different document types have different weights"""
    print("\n[Test 4] Document Type Weighting")
    print("-" * 60)
    
    analyzer = FOMCSentimentAnalyzer()
    
    sample_text = "We will raise interest rates to combat inflation"
    
    # Same text, different types
    statement_result = analyzer.analyze_document(sample_text, 'statement')
    minutes_result = analyzer.analyze_document(sample_text, 'minutes')
    speech_result = analyzer.analyze_document(sample_text, 'speech')
    
    # Check weighting: statement > minutes > speech
    assert statement_result['weighted_sentiment'] > minutes_result['weighted_sentiment'], \
        "Statements should have higher weight than minutes"
    assert minutes_result['weighted_sentiment'] > speech_result['weighted_sentiment'], \
        "Minutes should have higher weight than speeches"
    
    print(f"✓ Document type weighting works correctly")
    print(f"  Statement weight: {statement_result['weighted_sentiment']:.3f}")
    print(f"  Minutes weight: {minutes_result['weighted_sentiment']:.3f}")
    print(f"  Speech weight: {speech_result['weighted_sentiment']:.3f}")
    print("✓ PASSED")


def test_data_persistence():
    """Test that data can be saved and loaded"""
    print("\n[Test 5] Data Persistence")
    print("-" * 60)
    
    # Collect and analyze
    collector = FOMCDataCollector(start_date="2020-10-01")
    df = collector.collect_all()
    
    analyzer = FOMCSentimentAnalyzer()
    sentiment_df = analyzer.analyze_dataframe(df)
    
    # Save
    test_path = os.path.join("data", "processed", "test_sentiment.csv")
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    sentiment_df.to_csv(test_path, index=False)
    
    # Load
    loaded_df = pd.read_csv(test_path)
    
    assert len(loaded_df) == len(sentiment_df), "Loaded data should match saved data"
    assert 'weighted_sentiment' in loaded_df.columns, "Should preserve all columns"
    
    print(f"✓ Data saved to {test_path}")
    print(f"✓ Data loaded successfully")
    print(f"✓ {len(loaded_df)} records preserved")
    
    # Cleanup
    if os.path.exists(test_path):
        os.remove(test_path)
        print(f"✓ Cleaned up test file")
    
    print("✓ PASSED")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n[Test 6] Edge Cases")
    print("-" * 60)
    
    analyzer = FOMCSentimentAnalyzer()
    
    # Empty text
    empty_result = analyzer.analyze_document("", 'statement')
    assert empty_result['hawkish_score'] == 0, "Empty text should have 0 scores"
    assert empty_result['dovish_score'] == 0, "Empty text should have 0 scores"
    print("✓ Empty text handled correctly")
    
    # Very short text
    short_result = analyzer.analyze_document("The Fed.", 'statement')
    assert 'tone' in short_result, "Should handle short text"
    print("✓ Short text handled correctly")
    
    # Text with no keywords
    neutral_text = "The meeting was held on Tuesday at the headquarters."
    neutral_result = analyzer.analyze_document(neutral_text, 'statement')
    assert neutral_result['tone'] == 'neutral', "Text without keywords should be neutral"
    print("✓ Neutral text classified correctly")
    
    print("✓ PASSED")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("FOMC SENTIMENT ANALYSIS - TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run tests
        df = test_data_collection()
        sentiment_df = test_sentiment_analysis(df)
        test_hawkish_dovish_detection()
        test_document_type_weighting()
        test_data_persistence()
        test_edge_cases()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUITE SUMMARY")
        print("=" * 60)
        print("✓ All tests passed successfully!")
        print("\nTested components:")
        print("  • Data collection module")
        print("  • Sentiment analysis algorithm")
        print("  • Hawkish/dovish detection")
        print("  • Document type weighting")
        print("  • Data persistence")
        print("  • Edge case handling")
        print("\nImplementation is working correctly!")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
