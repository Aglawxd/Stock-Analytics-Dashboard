import argparse
import os
import sys
import time

import pandas as pd
import yfinance as yf

from sectors import TICKERS

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def download_single_ticker(ticker: str, start: str, end: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker,
                         start = start, end = end,
                         progress = False, auto_adjust = True)
        if df.empty:
            print(f'Warning: No data for {ticker}')
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]. copy()
        df.index.name = 'Date'
        return df

    except Exception as e:
        print(f'ERROR {ticker}: {e}')
        return pd.DataFrame()

def download_all(start: str, end: str, force: bool = False) -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    all_data = {}
    failed = []

    for i, ticker in enumerate(TICKERS,1):
        cache_path = os.path.join(DATA_DIR, f'{ticker}.csv')

        if not force and os.path.exists(cache_path):
            print(f'[{i}/{len(TICKERS)}] {ticker}: loading from cache')
            df = pd.read_csv(cache_path, index_col= 'Date', parse_dates = True)
        else:
            print(f'[{i}/{len(TICKERS)}] {ticker}: downloading from yfiannce...')
            df = download_single_ticker(ticker, start, end)
            if not df.empty:
                df.to_csv(cache_path)
            time.sleep(0.3)

        if df.empty:
            failed.append(ticker)
        else:
            all_data[ticker] = df

    if failed:
        print(f'\n[SUMMARY] Failed to download: {failed}')
    else:
        print(f'\n[SUMMARY] Successfully downloaded all {len(TICKERS)} tickers')

    return all_data

def build_close_matrix(all_data: dict) -> pd.DataFrame:
    closes = {ticker: df['Close'] for ticker, df in all_data.items()}
    matrix = pd.DataFrame(closes)
    matrix = matrix.sort_index()
    return matrix

def report_coverage(matrix: pd.DataFrame):
    print('\n DATA COVERAGE')
    for ticker in matrix.columns:
        series = matrix[ticker].dropna()
        if series.empty:
            print(f' {ticker}: NO DATA')
            continue

        first, last = series.index.min(), series.index.max()
        n_missing = matrix[ticker].isna().sum()
        print(f'{ticker}: {first.date()} -> {last.date()} ({n_missing} missing data)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', default ='2022-01-01')
    parser.add_argument('--end', default = None)
    parser.add_argument('--force', action = 'store_true')
    args = parser.parse_args()

    end = args.end or pd.Timestamp.today().strftime('%Y-%m-%d')

    print(f'Downloading data for {len(TICKERS)} tickers: {args.start} -> {end}\n')
    data  = download_all(args.start, end, force = args.force)

    if not data:
        print('No data has been downloaded')
        sys.exit(1)

    close_matrix = build_close_matrix(data)
    close_matrix.to_parquet(os.path.join(DATA_DIR, 'close_prices.parquet'))
    close_matrix.to_csv(os.path.join(DATA_DIR, 'close_prices.csb'))
