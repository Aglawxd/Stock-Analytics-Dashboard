import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sectors import TICKERS, TICKER_SECTOR, SECTOR_COLORS, get_sector, get_color
from analysis import(
    load_close_prices,
    compute_daily_returns,
    compute_correlation_matrix,
    compute_volatility,
    compute_max_drawdown,
    compute_total_return,
    compute_sharpe_ratio,
)

st.set_page_config(page_title = 'Multi sector stock analytics', layout = "wide")

st.title('Multi sector stock analytics dashboard')
st.caption('20 stocks, 9 sectors - prices, correlation, risk, return distribution')

@st.cache_data
def get_data():
    close = load_close_prices()
    returns = compute_daily_returns(close)
    return close, returns

close_prices, daily_returns = get_data()

st.sidebar.header('Settings')

selected_tickers = st.sidebar.multiselect(
    "Choose stocks",
    options = TICKERS,
    default = TICKERS
)

min_date = close_prices.index.min().date()
max_date = close_prices.index.max().date()

date_range = st.sidebar.date_input(
    'Range',
    value = (min_date, max_date),
    min_value = min_date,
    max_value = max_date
)

if len(date_range) != 2:
    st.stop()

start_date, end_date = date_range

if not selected_tickers:
    st.warning("Choose at least one stock")
    st.stop()

filtered_close = close_prices.loc[str(start_date):str(end_date), selected_tickers]
filtered_returns = daily_returns.loc[str(start_date):str(end_date), selected_tickers]

tab_prices, tab_corr, tab_risk, tab_dist = st.tabs(
    ['Price', 'Correlation', 'Risk', 'Distribution']
)

with tab_prices:
    st.subheader('Normalised prices - 1000$ invested at the beginning')
    normalized = filtered_close / filtered_close.iloc[0] * 1000

fig = go.Figure()
for ticker in normalized.columns:
    fig.add_trace(go.Scatter(
        x = normalized.index,
        y = normalized[ticker],
        mode = 'lines',
        name = ticker,
        line = dict(color = get_color(ticker)),
        hovertemplate = f'{ticker}<br>%{{x}}<br>$%{{y:.1f}}<extra></extra>',
    ))

    fig.update_layout(
        height=700,
        hovermode = 'x unified',
        hoverlabel=dict(font_size=10),
        yaxis_title = 'Value of investment',
        xaxis_title = 'Date',
        legend_title = 'Ticker',
        margin = dict(t=40, r=150)

    )
st.plotly_chart(fig, use_container_width = True)

with tab_corr:
    st.subheader('Correlation matrix of daily returns')

    ordered = sorted(filtered_returns.columns, key = lambda t: (get_sector(t) , t))
    corr = filtered_returns[ordered].corr()

    labels = [f'<span style = "color:{get_color(t)}">{t}</span>' for t in ordered]

    fig_corr = go.Figure(go.Heatmap(
        z = corr.values,
        x = ordered,
        y = ordered,
        colorscale = "RdBu",
        zmin = -1,
        zmax = 1,
        reversescale =  True,
        text = corr.round(2).values,
        texttemplate = '%{text}',
        hovertemplate = '%{y} vs %{x}<br> correlation: %{z:.2f}<extra></extra>',
    ))

    fig_corr.update_layout(
        height = 750,
        xaxis = dict(tickmode = 'array', tickvals = ordered, ticktext = labels),
        yaxis = dict(tickmode ='array', tickvals = ordered, ticktext = labels, autorange = 'reversed')

    )

    st.plotly_chart(fig_corr, use_container_width = True)