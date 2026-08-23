import numpy as np
import pandas as pd
import yfinance as yf

from sectors import TICKERS, get_sector

def load_close_prices(path: str = 'data/close_prices.parquet') -> pd.DataFrame:
    df = pd.read_parquet(path)

    return df

def compute_daily_returns(close_prices: pd.DataFrame) -> pd.DataFrame:
    returns = close_prices.pct_change()
    return returns

def compute_correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    corr = returns.corr()
    return corr

def compute_volatility(returns: pd.DataFrame, annualize: bool = True) -> pd.Series:
    daily_vol = returns.std()
    if annualize:
        daily_vol = daily_vol * np.sqrt(252) #amount of open exchange days
    return daily_vol.sort_values(ascending=False)

def compute_drawdown_series(close_prices: pd.DataFrame) -> pd.Series:
    running_max = close_prices.cummax()
    drawdown = (close_prices - running_max) / running_max
    return drawdown

def compute_max_drawdown(close_prices: pd.DataFrame) -> pd.Series:
    drawdown = compute_drawdown_series(close_prices)
    max_dd = drawdown.min()
    return max_dd.sort_values()

def compute_total_return(close_prices: pd.DataFrame) -> pd.Series:
    first_valid = close_prices.apply(lambda col: col.dropna().iloc[0])
    last_valid = close_prices.apply(lambda col: col.dropna().iloc[-1])
    total_return = (last_valid - first_valid) / first_valid * 100
    return total_return.sort_values(ascending=False)

def compute_sharpe_ratio(returns: pd.DataFrame, risk_free_rate: float = 0.04) -> pd.Series:
    daily_rf = risk_free_rate / 252
    excess_returns = returns.mean() - daily_rf
    daily_vol = returns.std()
    sharpe_ratio = (excess_returns / daily_vol) * np.sqrt(252)
    return sharpe_ratio.sort_values(ascending=False)

def fetch_benchmark_returns(start: str, end: str, ticker: str = "SPY") -> pd.Series:
    spy = yf.download(ticker, start= start, end=end, progress=False, auto_adjust=True)
    if isinstance(spy.columns, pd.MultiIndex):
        spy.columns = spy.columns.get_level_values(0)
    return spy['Close'].pct_change()

def compute_beta_alpha(returns: pd.DataFrame, benchmark_returns: pd.Series,
                       risk_free_rate: float = 0.04) -> pd.DataFrame:
    daily_rf = risk_free_rate / 252
    results = {}

    for ticker in returns.columns:
        aligned = pd.concat([returns[ticker], benchmark_returns],
                            axis = 1, join = 'inner').dropna()
        aligned.columns = ['asset', 'benchmark']

        cov = aligned['asset'].cov(aligned['benchmark'])
        var = aligned['benchmark'].var()

        beta = cov / var

        asset_mean = aligned['asset'].eman()
        bench_mean = aligned['benchmark'].mean()

        alpha_daily = (asset_mean - daily_rf) - beta * (bench_mean - daily_rf)
        alpha_annual = alpha_daily * 252

        results[ticker] =  {'beta': beta, 'alpha': alpha_annual}

    return pd.DataFrame(results).T.sort_values('beta', ascending = False )

if __name__ == '__main__':
    close = load_close_prices()
    returns = compute_daily_returns(close)

    print(' === TOTAL RETURN === ')
    print(compute_total_return(close))

    print('\n === VOLATILITY ===')
    print(compute_volatility(returns))

    print('\n === MAX DRAWDOWN ===')
    print(compute_max_drawdown(close))

    print('\n === SHARPE RATIO ===')
    print(compute_sharpe_ratio(returns))

    print('\n === CORELATION ===')
    corr = compute_correlation_matrix(returns)
    print(corr)