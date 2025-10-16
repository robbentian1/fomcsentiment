"""
Financial Data Collector
Collects asset price data for correlation analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from typing import List, Dict
import os


class FinancialDataCollector:
    """Collects financial market data for major U.S. assets"""
    
    def __init__(self, start_date: str = "2020-10-01"):
        """
        Initialize the financial data collector
        
        Args:
            start_date: Start date for data collection (format: YYYY-MM-DD)
        """
        self.start_date = start_date
        self.end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Define major U.S. financial assets to track
        self.assets = {
            # Stock Market Indices
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            
            # Treasury Yields
            '^TNX': '10-Year Treasury Yield',
            '^FVX': '5-Year Treasury Yield',
            '^TYX': '30-Year Treasury Yield',
            
            # Dollar Index
            'DX-Y.NYB': 'US Dollar Index',
            
            # Volatility
            '^VIX': 'VIX Volatility Index',
            
            # Commodities
            'GC=F': 'Gold Futures',
            'CL=F': 'Crude Oil Futures'
        }
    
    def fetch_price_data(self, ticker: str, asset_name: str) -> pd.DataFrame:
        """
        Fetch price data for a specific asset
        
        Args:
            ticker: Ticker symbol
            asset_name: Human-readable asset name
            
        Returns:
            DataFrame with price data
        """
        try:
            print(f"Fetching data for {asset_name} ({ticker})...")
            data = yf.download(ticker, start=self.start_date, end=self.end_date, 
                             progress=False)
            
            if data.empty:
                print(f"  Warning: No data available for {ticker}")
                return pd.DataFrame()
            
            # Calculate returns
            data['Returns'] = data['Close'].pct_change()
            data['Asset'] = asset_name
            data['Ticker'] = ticker
            
            return data
        except Exception as e:
            print(f"  Error fetching {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_all_assets(self) -> pd.DataFrame:
        """
        Fetch data for all assets
        
        Returns:
            Combined DataFrame with all asset data
        """
        all_data = []
        
        for ticker, asset_name in self.assets.items():
            df = self.fetch_price_data(ticker, asset_name)
            if not df.empty:
                all_data.append(df)
        
        if not all_data:
            return pd.DataFrame()
        
        # Combine all data
        combined_df = pd.concat(all_data)
        combined_df.reset_index(inplace=True)
        combined_df.rename(columns={'index': 'Date'}, inplace=True)
        
        return combined_df
    
    def calculate_event_returns(self, price_data: pd.DataFrame, 
                                event_dates: List[str], 
                                window_days: int = 5) -> pd.DataFrame:
        """
        Calculate asset returns around FOMC events
        
        Args:
            price_data: DataFrame with asset prices
            event_dates: List of FOMC event dates
            window_days: Number of days before/after event to analyze
            
        Returns:
            DataFrame with event-window returns
        """
        event_returns = []
        
        for event_date in event_dates:
            event_date = pd.to_datetime(event_date)
            
            for asset in price_data['Asset'].unique():
                asset_data = price_data[price_data['Asset'] == asset].copy()
                asset_data['Date'] = pd.to_datetime(asset_data['Date'])
                
                # Find closest trading day to event
                closest_idx = (asset_data['Date'] - event_date).abs().idxmin()
                event_day = asset_data.loc[closest_idx, 'Date']
                
                # Calculate returns for different windows
                for window in [1, 2, 5]:
                    try:
                        # Pre-event return
                        pre_mask = (asset_data['Date'] >= event_day - timedelta(days=window)) & \
                                  (asset_data['Date'] < event_day)
                        pre_return = asset_data.loc[pre_mask, 'Returns'].sum()
                        
                        # Post-event return
                        post_mask = (asset_data['Date'] > event_day) & \
                                   (asset_data['Date'] <= event_day + timedelta(days=window))
                        post_return = asset_data.loc[post_mask, 'Returns'].sum()
                        
                        # Event day return
                        event_return = asset_data.loc[asset_data['Date'] == event_day, 'Returns'].values
                        event_return = event_return[0] if len(event_return) > 0 else np.nan
                        
                        event_returns.append({
                            'event_date': event_date,
                            'asset': asset,
                            'window_days': window,
                            'pre_event_return': pre_return,
                            'event_return': event_return,
                            'post_event_return': post_return,
                            'total_return': pre_return + event_return + post_return
                        })
                    except Exception as e:
                        print(f"Error calculating returns for {asset} on {event_date}: {str(e)}")
        
        return pd.DataFrame(event_returns)
    
    def save_data(self, df: pd.DataFrame, output_path: str):
        """
        Save financial data to file
        
        Args:
            df: DataFrame with financial data
            output_path: Path to save the data
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Financial data saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    collector = FinancialDataCollector(start_date="2020-10-01")
    
    # Fetch asset data
    df = collector.fetch_all_assets()
    
    if not df.empty:
        # Save raw data
        output_path = os.path.join("data", "raw", "financial_data.csv")
        collector.save_data(df, output_path)
        
        print(f"\nCollected data for {df['Asset'].nunique()} assets:")
        print(df.groupby('Asset').size())
    else:
        print("No data collected")
