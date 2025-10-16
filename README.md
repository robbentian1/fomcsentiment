# FOMC Sentiment Analysis

Evaluating the Impact of FOMC Communications on Asset Prices

## Overview

This project investigates how the tone of Federal Open Market Committee (FOMC) communications affects major U.S. financial markets. Using textual analysis of Statements, Minutes, and Speeches since October 2020, we quantify the degree of hawkishness or dovishness in each document and test whether these tone shifts are reflected in asset-price movements.

## Research Question

**How does the hawkish or dovish tone of FOMC communications affect major U.S. financial markets?**

## Methodology

### 1. Data Collection
- **FOMC Documents**: Statements, Minutes, and Speeches from October 2020 onwards
- **Financial Data**: Major U.S. assets including:
  - Stock indices (S&P 500, Dow Jones, NASDAQ)
  - Treasury yields (2-year, 10-year, 30-year)
  - US Dollar Index
  - VIX Volatility Index
  - Commodities (Gold, Oil)

### 2. Sentiment Analysis
- **Keyword-based approach**: Using dictionaries of hawkish and dovish terms
- **Weighted scoring**: Documents weighted by type (Statements: 1.5x, Minutes: 1.2x, Speeches: 1.0x)
- **Net sentiment**: Positive scores indicate hawkish tone, negative scores indicate dovish tone

**Hawkish indicators** (tight monetary policy):
- inflation, raise, increase, tight, restrictive, elevated, vigilant, higher for longer

**Dovish indicators** (loose monetary policy):
- lower, cut, ease, accommodative, support, patient, moderate, normalize

### 3. Correlation Analysis
- **Event-window methodology**: Analyzing asset returns around FOMC communication dates
- **Multiple time windows**: 1-day, 2-day, and 5-day pre/post event
- **Statistical tests**: Pearson and Spearman correlations with significance testing

## Project Structure

```
fomcsentiment/
├── data/
│   ├── raw/                    # Raw collected data
│   └── processed/              # Processed data with sentiment scores
├── src/
│   ├── data_collection/        # FOMC document collection
│   ├── sentiment_analysis/     # Sentiment scoring algorithms
│   ├── financial_data/         # Market data collection
│   ├── correlation_analysis/   # Statistical analysis
│   └── main.py                 # Main analysis pipeline
├── notebooks/
│   └── analysis.ipynb          # Jupyter notebook for visualization
├── results/                    # Analysis results and reports
└── requirements.txt            # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/robbentian1/fomcsentiment.git
cd fomcsentiment
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download NLTK data (required for text processing):
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Usage

### Run Full Analysis Pipeline

```bash
python src/main.py
```

This will:
1. Collect FOMC documents since October 2020
2. Analyze sentiment and quantify hawkish/dovish tone
3. Collect financial market data
4. Calculate event-window returns
5. Perform correlation analysis

### Interactive Analysis

Launch Jupyter notebook for interactive exploration:

```bash
jupyter notebook notebooks/analysis.ipynb
```

### Individual Modules

You can also run individual components:

```python
# Collect FOMC data
from src.data_collection.fomc_collector import FOMCDataCollector
collector = FOMCDataCollector(start_date="2020-10-01")
df = collector.collect_all()

# Analyze sentiment
from src.sentiment_analysis.sentiment_analyzer import FOMCSentimentAnalyzer
analyzer = FOMCSentimentAnalyzer()
sentiment_df = analyzer.analyze_dataframe(df)

# Collect financial data
from src.financial_data.market_data import FinancialDataCollector
fin_collector = FinancialDataCollector(start_date="2020-10-01")
financial_df = fin_collector.fetch_all_assets()
```

## Results

The analysis generates:

1. **Sentiment Scores**: Quantified hawkish/dovish tone for each FOMC communication
2. **Correlation Results**: Statistical relationships between sentiment and asset returns
3. **Visualizations**: Charts showing sentiment trends and market impacts
4. **Summary Report**: Key findings and interpretation

Results are saved in the `results/` directory:
- `correlation_results.csv` - Detailed correlation statistics
- `summary_statistics.csv` - Summary metrics
- `analysis_report.txt` - Narrative findings

## Key Findings

The analysis reveals:
- The distribution of hawkish vs dovish FOMC communications since October 2020
- Sentiment trends over time and by document type
- Statistical correlations between FOMC tone and asset price movements
- Which assets are most sensitive to FOMC communications

## Interpretation

- **Hawkish communications** (positive sentiment) typically signal:
  - Concerns about inflation
  - Likelihood of interest rate increases
  - Tighter monetary policy stance

- **Dovish communications** (negative sentiment) typically signal:
  - Focus on economic support
  - Likelihood of rate cuts or holds
  - Accommodative monetary policy

- **Market reactions** depend on:
  - How much policy shift was already priced in
  - Current economic conditions
  - Investor expectations

## Limitations and Future Work

**Current Limitations:**
- Keyword-based sentiment analysis (could be enhanced with ML models)
- Sample implementation with placeholder data collection
- Limited to U.S. markets

**Future Enhancements:**
- Implement actual web scraping for FOMC documents
- Use transformer-based NLP models (BERT, FinBERT)
- Extend to international markets
- Add control variables (economic indicators)
- Implement event study methodology with abnormal returns

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## References

- Federal Reserve: https://www.federalreserve.gov/
- FOMC Statements: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- FOMC Minutes: https://www.federalreserve.gov/monetarypolicy/fomcminutes.htm

## Contact

For questions or feedback, please open an issue on GitHub.
