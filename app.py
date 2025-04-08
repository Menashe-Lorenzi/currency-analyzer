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
            st.write(f"**Mean Price**: {mean_price:.4f}")
            st.write(f"**Standard Deviation**: {std_price:.4f}")
            st.write(f"**Within 1 Std**: ({one_std_lower:.4f}, {one_std_upper:.4f}) → {within_one_std:.2f}%")
            st.write(f"**Within 2 Std**: ({two_std_lower:.4f}, {two_std_upper:.4f}) → {within_two_std:.2f}%")
            st.write(f"**{int(confidence_level * 100)}% Confidence Interval**: ({ci_lower:.4f}, {ci_upper:.4f})")

            st.subheader("📊 Price Distribution Histogram")
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='#111111')  # רקע כללי כהה
            ax.set_facecolor('#111111')  # רקע פנימי של הגרף
            
            # היסטוגרמה עם צבע בהיר
            ax.hist(prices, bins=50, color='#1ABC9C', edgecolor='white', alpha=0.85)
            
            # קווים סטטיסטיים עם צבעים זוהרים ונעימים לעין
            ax.axvline(mean_price, color='#3498DB', linestyle='--', linewidth=2, label='Mean')
            ax.axvline(one_std_lower, color='#2ECC71', linestyle='--', linewidth=1, label='-1 Std Dev')
            ax.axvline(one_std_upper, color='#2ECC71', linestyle='--', linewidth=1, label='+1 Std Dev')
            ax.axvline(two_std_lower, color='#E74C3C', linestyle='--', linewidth=1, label='-2 Std Dev')
            ax.axvline(two_std_upper, color='#E74C3C', linestyle='--', linewidth=1, label='+2 Std Dev')
            ax.axvline(ci_lower, color='#9B59B6', linestyle='-.', linewidth=0.5, label='CI Lower')
            ax.axvline(ci_upper, color='#9B59B6', linestyle='-.', linewidth=0.5, label='CI Upper')
            
            # כותרות וצירים
            ax.set_title(f' Price Distribution with Std Dev Bands & CI\n({symbol})', fontsize=12, weight='normal', color='white')
            ax.set_xlabel(f'Price ({symbol})', fontsize=12, color='white')
            ax.set_ylabel('Frequency', fontsize=10, color='white')
            
            # הסרת גריד, קווים סביב הגרף בצבע כהה
            ax.grid(False)
            for spine in ax.spines.values():
                spine.set_color('#444444')
            
            # צבעי טקסט בצירים
            ax.tick_params(colors='white', labelsize=10)
            
            # מקרא (לג׳נד) בלי רקע
            ax.legend(frameon=False, fontsize=10, loc='upper right', facecolor='none', labelcolor='white')
            
            st.pyplot(fig)

            # ==============================
            # Step 3: Percentage Above/Below Mean & Median + Visualization
            # ==============================
            
            st.subheader("📈 Percentage of Days Above/Below Mean & Median")
            
            # חשב ממוצע וחציון
            overall_mean = float(prices.mean())
            overall_median = float(prices.median())
            
            # הדפס לבדיקה
            # st.write(f"Mean: {overall_mean}, Median: {overall_median}")
            
            # דגלים לימים מעל ממוצע/חציון
            data['Above Mean'] = prices > overall_mean
            data['Above Median'] = prices > overall_median
            
            # אחוזים
            perc_above_mean = data['Above Mean'].mean() * 100
            perc_below_mean = 100 - perc_above_mean
            perc_above_median = data['Above Median'].mean() * 100
            perc_below_median = 100 - perc_above_median
            
            # הצגת ערכים
            st.markdown(f"""
            - **Percentage of days above Mean**: `{perc_above_mean:.2f}%`
            - **Percentage of days below Mean**: `{perc_below_mean:.2f}%`
            - **Percentage of days above Median**: `{perc_above_median:.2f}%`
            - **Percentage of days below Median**: `{perc_below_median:.2f}%`
            """)
            
            # גרף כהה מודרני
            fig, ax = plt.subplots(figsize=(12, 6), facecolor='#111111')
            ax.set_facecolor('#111111')
            
            # קו מחיר
            ax.plot(data.index, prices, color='white', alpha=0.6, label='Price')
            
            # נקודות ירוקות/אדומות
            colors = data['Above Mean'].map({True: '#2ECC71', False: '#E74C3C'})
            ax.scatter(data.index, prices, c=colors, s=6, label='Above/Below Mean')
            
            # קווים לממוצע וחציון
            ax.axhline(overall_mean, color='#3498DB', linestyle='--', linewidth=1.5, label=f'Mean: {overall_mean:.2f}')
            ax.axhline(overall_median, color='#F39C12', linestyle='--', linewidth=1.5, label=f'Median: {overall_median:.2f}')
            
            # טקסטים ועיצוב
            ax.set_title(f'Price vs Mean & Median ({symbol})', fontsize=16, weight='bold', color='white')
            ax.set_xlabel('Date', fontsize=12, color='white')
            ax.set_ylabel(f'Price ({symbol})', fontsize=12, color='white')
            ax.tick_params(colors='white')
            ax.legend(frameon=False, fontsize=10, loc='best', labelcolor='white')
            
            # הסרת גבולות מיותרים
            for spine in ax.spines.values():
                spine.set_color('#333333')
            
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Error: {e}")
