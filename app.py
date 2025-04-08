import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from itertools import product

st.set_page_config(page_title="Currency Analyzer", layout="wide")
st.title("📊 Currency Analysis Tool (Yahoo Finance)")

# Sidebar Inputs
symbol = st.sidebar.text_input("Enter Symbol (e.g., GBPILS=X)", value="GBPILS=X")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-01-01"))

currencies = ['USD', 'ILS', 'EUR', 'GBP', 'JPY', 'CNY']
rows = []
for from_curr, to_curr in product(currencies, currencies):
    if from_curr != to_curr:
        symbol = f"{from_curr}{to_curr}=X"
        rows.append({
            'From': from_curr,
            'To': to_curr,
            'Yahoo Symbol': symbol
        })

df = pd.DataFrame(rows)
print(df)
st.subheader("🪙 Currency Symbol Table (Yahoo Finance)")
st.dataframe(df)

if st.sidebar.button("Analyze"):
    try:
        data = yf.download(symbol, start=start_date, end=end_date)

        if data.empty:
            st.error("No data found for this symbol and date range.")
        else:
            prices = data['Close']
            if isinstance(prices, pd.DataFrame):
                prices = prices.squeeze()
            mean_price = prices.mean()
            std_price = prices.std(ddof=1)
            n = len(prices)

            one_std_lower = mean_price - std_price
            one_std_upper = mean_price + std_price
            two_std_lower = mean_price - 2 * std_price
            two_std_upper = mean_price + 2 * std_price

            within_one_std = ((prices >= one_std_lower) & (prices <= one_std_upper)).mean() * 100
            within_two_std = ((prices >= two_std_lower) & (prices <= two_std_upper)).mean() * 100

            confidence_level = 0.95
            stderr = std_price / np.sqrt(n)
            z_score = stats.norm.ppf((1 + confidence_level) / 2)
            ci_lower = mean_price - z_score * stderr
            ci_upper = mean_price + z_score * stderr

            st.subheader("📈 Statistics:")
            st.write(f"**Mean Price**: {mean_price:.4f} ILS")
            st.write(f"**Standard Deviation**: {std_price:.4f} ILS")
            st.write(f"**Within 1 Std**: ({one_std_lower:.4f}, {one_std_upper:.4f}) → {within_one_std:.2f}%")
            st.write(f"**Within 2 Std**: ({two_std_lower:.4f}, {two_std_upper:.4f}) → {within_two_std:.2f}%")
            st.write(f"**{int(confidence_level * 100)}% Confidence Interval**: ({ci_lower:.4f}, {ci_upper:.4f})")

            st.subheader("📊 Price Distribution Histogram")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.hist(prices, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
            ax.axvline(mean_price, color='blue', linestyle='--', label='Mean')
            ax.axvline(one_std_lower, color='green', linestyle='--', label='-1 Std Dev')
            ax.axvline(one_std_upper, color='green', linestyle='--', label='+1 Std Dev')
            ax.axvline(two_std_lower, color='red', linestyle='--', label='-2 Std Dev')
            ax.axvline(two_std_upper, color='red', linestyle='--', label='+2 Std Dev')
            ax.axvline(ci_lower, color='purple', linestyle='-.', label='CI Lower')
            ax.axvline(ci_upper, color='purple', linestyle='-.', label='CI Upper')
            ax.set_title("Price Distribution with Std Dev Bands & Confidence Interval")
            ax.set_xlabel(f'Price ({symbol})')
            ax.set_ylabel("Frequency")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")
