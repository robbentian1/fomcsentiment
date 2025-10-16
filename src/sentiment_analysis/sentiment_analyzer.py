"""
Sentiment Analyzer for FOMC Communications
Quantifies hawkish/dovish tone using NLP techniques
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import re
from textblob import TextBlob
import os


class FOMCSentimentAnalyzer:
    """Analyzes sentiment in FOMC communications to determine hawkish/dovish tone"""
    
    def __init__(self):
        """Initialize the sentiment analyzer with hawkish/dovish dictionaries"""
        
        # Hawkish keywords (tight monetary policy, anti-inflation)
        self.hawkish_keywords = [
            'inflation', 'raise', 'increase', 'tight', 'tighten', 'restrictive',
            'reduce', 'reduction', 'elevated', 'concerns', 'risks', 'upside',
            'accelerat', 'strong', 'robust', 'overheating', 'vigilant',
            'firm', 'firmer', 'appropriate', 'well above', 'persistent',
            'higher for longer', 'remain restrictive', 'additional firming'
        ]
        
        # Dovish keywords (loose monetary policy, pro-growth)
        self.dovish_keywords = [
            'lower', 'cut', 'decrease', 'ease', 'easing', 'accommodative',
            'support', 'stimulus', 'gradual', 'patient', 'cautious',
            'downside', 'weak', 'subdued', 'moderate', 'moderating',
            'decline', 'declining', 'well anchored', 'transitory',
            'appropriate to reduce', 'recalibrat', 'normalize'
        ]
        
        # Weights for different communication types
        self.type_weights = {
            'statement': 1.5,  # Statements carry more weight
            'minutes': 1.2,     # Minutes provide detailed context
            'speech': 1.0       # Individual speeches
        }
    
    def calculate_keyword_score(self, text: str) -> Tuple[float, float]:
        """
        Calculate hawkish and dovish scores based on keyword frequency
        
        Args:
            text: Document text
            
        Returns:
            Tuple of (hawkish_score, dovish_score)
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        
        if total_words == 0:
            return 0.0, 0.0
        
        # Count keyword occurrences
        hawkish_count = sum(1 for word in self.hawkish_keywords 
                           if word in text_lower)
        dovish_count = sum(1 for word in self.dovish_keywords 
                          if word in text_lower)
        
        # Normalize by document length (per 100 words)
        hawkish_score = (hawkish_count / total_words) * 100
        dovish_score = (dovish_count / total_words) * 100
        
        return hawkish_score, dovish_score
    
    def calculate_net_sentiment(self, hawkish_score: float, dovish_score: float) -> float:
        """
        Calculate net sentiment score
        
        Args:
            hawkish_score: Hawkish keyword score
            dovish_score: Dovish keyword score
            
        Returns:
            Net sentiment (positive = hawkish, negative = dovish)
        """
        return hawkish_score - dovish_score
    
    def analyze_document(self, text: str, doc_type: str = 'statement') -> Dict:
        """
        Analyze a single document
        
        Args:
            text: Document text
            doc_type: Type of document (statement, minutes, speech)
            
        Returns:
            Dictionary with sentiment metrics
        """
        hawkish_score, dovish_score = self.calculate_keyword_score(text)
        net_sentiment = self.calculate_net_sentiment(hawkish_score, dovish_score)
        
        # Apply type weight
        weight = self.type_weights.get(doc_type, 1.0)
        weighted_sentiment = net_sentiment * weight
        
        # Classify tone
        if weighted_sentiment > 0.5:
            tone = 'hawkish'
        elif weighted_sentiment < -0.5:
            tone = 'dovish'
        else:
            tone = 'neutral'
        
        # Use TextBlob for additional sentiment analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        return {
            'hawkish_score': hawkish_score,
            'dovish_score': dovish_score,
            'net_sentiment': net_sentiment,
            'weighted_sentiment': weighted_sentiment,
            'tone': tone,
            'polarity': polarity,
            'subjectivity': subjectivity
        }
    
    def analyze_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze all documents in a DataFrame
        
        Args:
            df: DataFrame with 'text' and 'type' columns
            
        Returns:
            DataFrame with added sentiment columns
        """
        results = []
        
        for idx, row in df.iterrows():
            sentiment = self.analyze_document(row['text'], row['type'])
            results.append(sentiment)
        
        # Add sentiment columns to DataFrame
        sentiment_df = pd.DataFrame(results)
        result_df = pd.concat([df.reset_index(drop=True), sentiment_df], axis=1)
        
        return result_df
    
    def generate_sentiment_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary statistics of sentiment over time
        
        Args:
            df: DataFrame with sentiment scores and dates
            
        Returns:
            DataFrame with summary statistics
        """
        df['date'] = pd.to_datetime(df['date'])
        df['year_month'] = df['date'].dt.to_period('M')
        
        summary = df.groupby('year_month').agg({
            'weighted_sentiment': ['mean', 'std', 'min', 'max'],
            'hawkish_score': 'mean',
            'dovish_score': 'mean',
            'tone': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'neutral'
        }).round(3)
        
        return summary


if __name__ == "__main__":
    # Example usage
    analyzer = FOMCSentimentAnalyzer()
    
    # Load data
    input_path = os.path.join("data", "raw", "fomc_documents.csv")
    if os.path.exists(input_path):
        df = pd.read_csv(input_path)
        
        # Analyze sentiment
        df_with_sentiment = analyzer.analyze_dataframe(df)
        
        # Save results
        output_path = os.path.join("data", "processed", "fomc_sentiment.csv")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_with_sentiment.to_csv(output_path, index=False)
        
        print("Sentiment analysis complete!")
        print(f"\nSentiment distribution:")
        print(df_with_sentiment['tone'].value_counts())
        print(f"\nAverage weighted sentiment: {df_with_sentiment['weighted_sentiment'].mean():.3f}")
    else:
        print(f"Data file not found: {input_path}")
        print("Please run fomc_collector.py first to collect data.")
