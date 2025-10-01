To use EODHD

Set your API key
    1. Copy .env.example to .env
    2. Edit .env and put your real EODHD API token

Configs
    Configs live under eodhd_fetchcher/config/ and are written in JSON
    tickers: list of tickers with exchange suffix (AAPL.US, SPY.US, etc.)
    from / to: date range in YYYY-MM-DD
    data.period: "d" (daily), "w" (weekly), "m" (monthly)
    output.format: "csv" or "parquet"
    output.per_ticker: true = one file per ticker, false = one combined file

Run
    1. cd into SUNDANCE-BUDDY
        2. pip install -r requirements.txt
    3. cd into eodhd_fetcher
       4. python app.py --config config/sample.config.json (replace this with the name of your config.json)
