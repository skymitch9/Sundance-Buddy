# 📈 Using EODHD with Sundance Buddy

Welcome! This guide will help you set up and run EODHD data fetching with Sundance Buddy.

---

## 🚀 Quick Start

### 1. Set Your API Key

1. Copy `.env.example` to `.env`
2. Open `.env` and paste your EODHD API token in the quotes:
    ```
    EODHD_API_KEY="your_token_here"
    ```

---

### 2. Configure Fetcher

- **Configs Location:**  
  `eodhd_fetcher/config/` (JSON files)

- **Config Options:**
  - `tickers`: List of tickers with exchange suffix (e.g., `AAPL.US`, `SPY.US`)
  - `from` / `to`: Date range (`YYYY-MM-DD`)
  - `data.period`: `"d"` (daily), `"w"` (weekly), `"m"` (monthly)
  - `output.format`: `"csv"` or `"parquet"`
  - `output.per_ticker`:  
     - `true` = one file per ticker  
     - `false` = one combined file

---

### 3. Run the Fetcher

1. Navigate to the project root:
    ```sh
    cd SUNDANCE-BUDDY
    ```
2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Enter the fetcher directory:
    ```sh
    cd eodhd_fetcher
    ```
4. Run the app with your config:
    ```sh
    python app.py --config config/sample.config.json
    ```
    > Replace `sample.config.json` with your config file name.

---

**Happy Fetching!**
