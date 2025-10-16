"""
Correlation Analysis
Analyzes relationship between FOMC sentiment and asset price movements
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Dict, Tuple, List


class CorrelationAnalyzer:
    """Analyzes correlation between FOMC sentiment and asset returns"""
    
    def __init__(self):
        """Initialize the correlation analyzer"""
        self.results = {}
    
    def merge_sentiment_and_returns(self, sentiment_df: pd.DataFrame, 
                                    returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sentiment data with asset returns
        
        Args:
            sentiment_df: DataFrame with FOMC sentiment scores
            returns_df: DataFrame with asset returns around events
            
        Returns:
            Merged DataFrame
        """
        # Ensure date columns are datetime
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
        returns_df['event_date'] = pd.to_datetime(returns_df['event_date'])
        
        # Merge on date
        merged = returns_df.merge(
            sentiment_df[['date', 'weighted_sentiment', 'tone', 'type']],
            left_on='event_date',
            right_on='date',
            how='inner'
        )
        
        return merged
    
    def calculate_correlation(self, df: pd.DataFrame, 
                             sentiment_col: str = 'weighted_sentiment',
                             return_col: str = 'post_event_return') -> Dict:
        """
        Calculate correlation between sentiment and returns
        
        Args:
            df: Merged DataFrame with sentiment and returns
            sentiment_col: Column name for sentiment scores
            return_col: Column name for returns
            
        Returns:
            Dictionary with correlation results
        """
        # Remove NaN values
        clean_df = df[[sentiment_col, return_col]].dropna()
        
        if len(clean_df) < 3:
            return {
                'pearson_r': np.nan,
                'pearson_p': np.nan,
                'spearman_r': np.nan,
                'spearman_p': np.nan,
                'n_observations': len(clean_df)
            }
        
        # Pearson correlation
        pearson_r, pearson_p = stats.pearsonr(
            clean_df[sentiment_col], 
            clean_df[return_col]
        )
        
        # Spearman correlation (rank-based, more robust)
        spearman_r, spearman_p = stats.spearmanr(
            clean_df[sentiment_col], 
            clean_df[return_col]
        )
        
        return {
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
            'spearman_r': spearman_r,
            'spearman_p': spearman_p,
            'n_observations': len(clean_df)
        }
    
    def analyze_by_asset(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlations for each asset
        
        Args:
            merged_df: Merged DataFrame with sentiment and returns
            
        Returns:
            DataFrame with correlation results by asset
        """
        results = []
        
        for asset in merged_df['asset'].unique():
            asset_df = merged_df[merged_df['asset'] == asset]
            
            for window in asset_df['window_days'].unique():
                window_df = asset_df[asset_df['window_days'] == window]
                
                # Post-event correlation
                post_corr = self.calculate_correlation(
                    window_df, 
                    'weighted_sentiment', 
                    'post_event_return'
                )
                
                # Event-day correlation
                event_corr = self.calculate_correlation(
                    window_df,
                    'weighted_sentiment',
                    'event_return'
                )
                
                results.append({
                    'asset': asset,
                    'window_days': window,
                    'post_pearson_r': post_corr['pearson_r'],
                    'post_pearson_p': post_corr['pearson_p'],
                    'post_spearman_r': post_corr['spearman_r'],
                    'event_pearson_r': event_corr['pearson_r'],
                    'event_pearson_p': event_corr['pearson_p'],
                    'n_observations': post_corr['n_observations']
                })
        
        return pd.DataFrame(results)
    
    def run_regression(self, merged_df: pd.DataFrame, 
                      asset: str = 'S&P 500') -> Dict:
        """
        Run linear regression of returns on sentiment
        
        Args:
            merged_df: Merged DataFrame
            asset: Asset to analyze
            
        Returns:
            Dictionary with regression results
        """
        asset_df = merged_df[merged_df['asset'] == asset].copy()
        asset_df = asset_df.dropna(subset=['weighted_sentiment', 'post_event_return'])
        
        if len(asset_df) < 3:
            return {'error': 'Insufficient data'}
        
        X = asset_df[['weighted_sentiment']].values
        y = asset_df['post_event_return'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate R-squared
        y_pred = model.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'coefficient': model.coef_[0],
            'intercept': model.intercept_,
            'r_squared': r_squared,
            'n_observations': len(asset_df)
        }
    
    def generate_summary_statistics(self, merged_df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics
        
        Args:
            merged_df: Merged DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_events': merged_df['event_date'].nunique(),
            'total_assets': merged_df['asset'].nunique(),
            'date_range': f"{merged_df['event_date'].min()} to {merged_df['event_date'].max()}",
            'hawkish_events': len(merged_df[merged_df['tone'] == 'hawkish']['event_date'].unique()),
            'dovish_events': len(merged_df[merged_df['tone'] == 'dovish']['event_date'].unique()),
            'neutral_events': len(merged_df[merged_df['tone'] == 'neutral']['event_date'].unique()),
            'avg_sentiment': merged_df['weighted_sentiment'].mean(),
            'sentiment_std': merged_df['weighted_sentiment'].std()
        }
        
        return summary
    
    def save_results(self, results_df: pd.DataFrame, summary: Dict, output_dir: str):
        """
        Save analysis results
        
        Args:
            results_df: DataFrame with correlation results
            summary: Summary statistics dictionary
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Save correlation results
        results_df.to_csv(os.path.join(output_dir, 'correlation_results.csv'), index=False)
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(os.path.join(output_dir, 'summary_statistics.csv'), index=False)
        
        print(f"Results saved to {output_dir}")


if __name__ == "__main__":
    # Example usage
    analyzer = CorrelationAnalyzer()
    
    # Load sentiment data
    sentiment_path = os.path.join("data", "processed", "fomc_sentiment.csv")
    
    # For demonstration, create sample event returns
    # In production, this would come from the financial data module
    sample_returns = pd.DataFrame({
        'event_date': ['2024-12-18', '2024-11-07'],
        'asset': ['S&P 500', 'S&P 500'],
        'window_days': [5, 5],
        'post_event_return': [0.015, -0.008],
        'event_return': [0.005, -0.003]
    })
    
    if os.path.exists(sentiment_path):
        sentiment_df = pd.read_csv(sentiment_path)
        merged_df = analyzer.merge_sentiment_and_returns(sentiment_df, sample_returns)
        
        # Analyze correlations
        results = analyzer.analyze_by_asset(merged_df)
        summary = analyzer.generate_summary_statistics(merged_df)
        
        # Save results
        analyzer.save_results(results, summary, "results")
        
        print("\nAnalysis Summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")
    else:
        print(f"Sentiment data not found: {sentiment_path}")
