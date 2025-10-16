# FOMC Sentiment Analysis - Technical Documentation

## Project Overview

This project analyzes the sentiment of Federal Open Market Committee (FOMC) communications and tests their impact on U.S. financial markets. The analysis framework includes:

1. **Data Collection**: Gathering FOMC documents (Statements, Minutes, Speeches)
2. **Sentiment Analysis**: Quantifying hawkish/dovish tone using NLP
3. **Financial Data**: Collecting market data for major U.S. assets
4. **Correlation Analysis**: Testing statistical relationships

## Architecture

### Module Structure

```
src/
├── data_collection/
│   ├── fomc_collector.py       # FOMC document collection
│   └── __init__.py
├── sentiment_analysis/
│   ├── sentiment_analyzer.py    # Sentiment scoring
│   └── __init__.py
├── financial_data/
│   ├── market_data.py          # Market data collection
│   └── __init__.py
├── correlation_analysis/
│   ├── correlation.py          # Statistical analysis
│   └── __init__.py
└── main.py                     # Main pipeline orchestrator
```

### Data Flow

```
FOMC Documents → Sentiment Analysis → Event Returns → Correlation Analysis → Results
                                    ↗
                    Financial Data →
```

## Methodology Details

### 1. Sentiment Scoring Algorithm

The sentiment analyzer uses a keyword-based approach with the following components:

#### Hawkish Keywords (Tight Monetary Policy)
- inflation, raise, increase, tight, tighten, restrictive
- reduce, reduction, elevated, concerns, risks, upside
- accelerat, strong, robust, overheating, vigilant
- firm, firmer, appropriate, well above, persistent
- higher for longer, remain restrictive, additional firming

#### Dovish Keywords (Loose Monetary Policy)
- lower, cut, decrease, ease, easing, accommodative
- support, stimulus, gradual, patient, cautious
- downside, weak, subdued, moderate, moderating
- decline, declining, well anchored, transitory
- appropriate to reduce, recalibrat, normalize

#### Scoring Formula

```python
# Raw scores (per 100 words)
hawkish_score = (hawkish_count / total_words) * 100
dovish_score = (dovish_count / total_words) * 100

# Net sentiment
net_sentiment = hawkish_score - dovish_score

# Weighted by document type
weighted_sentiment = net_sentiment * type_weight
```

#### Document Type Weights
- Statements: 1.5x (most official and market-moving)
- Minutes: 1.2x (detailed policy discussion)
- Speeches: 1.0x (individual views)

#### Tone Classification
- Hawkish: weighted_sentiment > 0.5
- Dovish: weighted_sentiment < -0.5
- Neutral: -0.5 ≤ weighted_sentiment ≤ 0.5

### 2. Event-Window Analysis

For each FOMC communication date, we calculate:

#### Return Windows
- **Pre-event**: 1, 2, or 5 days before
- **Event day**: Day of announcement
- **Post-event**: 1, 2, or 5 days after

#### Calculation
```python
pre_return = sum(returns in pre-event window)
event_return = return on event day
post_return = sum(returns in post-event window)
total_return = pre_return + event_return + post_return
```

### 3. Statistical Analysis

#### Correlation Tests

**Pearson Correlation**: Linear relationship
```python
r, p_value = pearsonr(sentiment_scores, returns)
```

**Spearman Correlation**: Rank-based (robust to outliers)
```python
r, p_value = spearmanr(sentiment_scores, returns)
```

#### Regression Analysis
```python
returns = β₀ + β₁ × sentiment + ε
```

Where:
- β₁ (coefficient): Change in returns per unit sentiment
- R²: Proportion of variance explained

## Assets Tracked

### Stock Market Indices
- S&P 500 (^GSPC)
- Dow Jones (^DJI)
- NASDAQ (^IXIC)

### Treasury Yields
- 10-Year (^TNX)
- 5-Year (^FVX)
- 30-Year (^TYX)

### Other Markets
- US Dollar Index (DX-Y.NYB)
- VIX Volatility (^VIX)
- Gold Futures (GC=F)
- Crude Oil Futures (CL=F)

## Expected Relationships

### Theoretical Predictions

1. **Hawkish Communications → Higher Yields**
   - Tighter policy → Higher interest rates
   - Expected: Positive correlation

2. **Hawkish Communications → Lower Stocks**
   - Higher rates → Lower valuations
   - Expected: Negative correlation

3. **Hawkish Communications → Stronger Dollar**
   - Higher yields → Capital inflows
   - Expected: Positive correlation

4. **Hawkish Communications → Higher Volatility**
   - Policy uncertainty → Market volatility
   - Expected: Positive correlation (short-term)

## Usage Examples

### Basic Usage

```python
# Import modules
from src.data_collection.fomc_collector import FOMCDataCollector
from src.sentiment_analysis.sentiment_analyzer import FOMCSentimentAnalyzer

# Collect data
collector = FOMCDataCollector(start_date="2020-10-01")
documents = collector.collect_all()

# Analyze sentiment
analyzer = FOMCSentimentAnalyzer()
results = analyzer.analyze_dataframe(documents)

# View results
print(results[['date', 'type', 'tone', 'weighted_sentiment']])
```

### Advanced Analysis

```python
from src.correlation_analysis.correlation import CorrelationAnalyzer

# Merge sentiment and returns
analyzer = CorrelationAnalyzer()
merged_data = analyzer.merge_sentiment_and_returns(sentiment_df, returns_df)

# Calculate correlations
correlations = analyzer.analyze_by_asset(merged_data)

# Run regression for specific asset
regression_results = analyzer.run_regression(merged_data, asset='S&P 500')
```

## Output Files

### Data Files

1. **fomc_documents.csv** (data/raw/)
   - Columns: date, title, text, type, url

2. **fomc_sentiment.csv** (data/processed/)
   - Columns: date, type, text, hawkish_score, dovish_score, 
     net_sentiment, weighted_sentiment, tone, polarity, subjectivity

3. **financial_data.csv** (data/raw/)
   - Columns: Date, Open, High, Low, Close, Volume, Returns, Asset, Ticker

4. **event_returns.csv** (data/processed/)
   - Columns: event_date, asset, window_days, pre_event_return, 
     event_return, post_event_return, total_return

### Results Files

1. **correlation_results.csv** (results/)
   - Correlations by asset and time window
   - Pearson and Spearman coefficients with p-values

2. **summary_statistics.csv** (results/)
   - Overall analysis summary
   - Event counts, date ranges, sentiment statistics

3. **analysis_report.txt** (results/)
   - Narrative summary of findings

## Interpretation Guide

### Sentiment Scores

- **Score > 2**: Strongly hawkish
- **Score 0.5 to 2**: Moderately hawkish
- **Score -0.5 to 0.5**: Neutral
- **Score -2 to -0.5**: Moderately dovish
- **Score < -2**: Strongly dovish

### Statistical Significance

- **p < 0.01**: Highly significant (strong evidence)
- **p < 0.05**: Significant (moderate evidence)
- **p < 0.10**: Marginally significant (weak evidence)
- **p ≥ 0.10**: Not significant (insufficient evidence)

### Correlation Strength (|r|)

- **0.7 - 1.0**: Very strong
- **0.5 - 0.7**: Strong
- **0.3 - 0.5**: Moderate
- **0.1 - 0.3**: Weak
- **0.0 - 0.1**: Very weak/none

## Limitations

### Current Implementation

1. **Sample Data**: Uses placeholder FOMC documents
   - Production version would scrape actual Fed website
   
2. **Simple NLP**: Keyword-based sentiment
   - Could be enhanced with ML models (BERT, FinBERT)

3. **Limited Controls**: No adjustment for
   - Market expectations
   - Economic conditions
   - Other news events

4. **Attribution**: Assumes causal relationship
   - Correlation ≠ causation
   - Multiple factors affect markets

### Future Enhancements

1. **Advanced NLP**
   - Transformer models (BERT, GPT)
   - Fine-tuned on financial text (FinBERT)
   - Topic modeling (LDA, NMF)

2. **Robust Statistics**
   - Event study with abnormal returns
   - Control for market expectations
   - Panel regression with fixed effects

3. **Extended Scope**
   - International markets
   - Additional assets (crypto, commodities)
   - Real-time analysis

4. **Production Features**
   - Automated data collection
   - API endpoints
   - Real-time dashboard

## References

### Academic Literature

1. Rosa, C. (2011). "Words that shake traders: The stock market's reaction to central bank communication in real time." Journal of Empirical Finance.

2. Schmeling, M., & Wagner, C. (2019). "Does Central Bank Tone Move Asset Prices?" Working Paper.

3. Picault, M., & Renault, T. (2017). "Words are not all created equal: A new measure of ECB communication." Journal of International Money and Finance.

### Data Sources

- Federal Reserve: https://www.federalreserve.gov/
- FOMC Statements: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- FOMC Minutes: https://www.federalreserve.gov/monetarypolicy/fomcminutes.htm
- Speeches: https://www.federalreserve.gov/newsevents/speeches.htm

### Technical Resources

- TextBlob Documentation: https://textblob.readthedocs.io/
- Pandas Documentation: https://pandas.pydata.org/
- SciPy Stats: https://docs.scipy.org/doc/scipy/reference/stats.html
- yfinance: https://pypi.org/project/yfinance/

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Install all dependencies
   pip install -r requirements.txt
   ```

2. **Financial Data Not Available**
   - Check internet connection
   - Verify ticker symbols are correct
   - Some data may have download limits

3. **No Correlations Found**
   - Ensure sufficient data points (n > 3)
   - Check date alignment between sentiment and returns
   - Verify sentiment scores are calculated

4. **Jupyter Notebook Issues**
   ```bash
   # Install Jupyter
   pip install jupyter
   
   # Launch notebook
   jupyter notebook notebooks/analysis.ipynb
   ```

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Contact

For questions or issues, please open an issue on GitHub.
