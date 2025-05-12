import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from datetime import date

ticker = []

st.title("Matrix of correlation")
st.write("")

# Sidebar inputs
with st.sidebar:
    st.title('⚙️ Parameters.')
    tickers_input = st.text_input("Enter tickers separated by commas (e.g., AAPL, AMZN, NVDA)", value="AAPL,AMZN,NVDA")
    ticker = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
    start_date = st.date_input("Choose your start date", value=date(2024, 1, 1))
    end_date = st.date_input("Choose your end date", value=date(2025, 1, 1))
    color = st.text_input("Choose a color theme for the heatmap (e.g., 'vlag', 'coolwarm', 'rocket')", value="coolwarm")

# Download data
maindf = pd.DataFrame()

for stock in ticker:
    data = yf.download(stock, start=start_date, end=end_date)
    if data is not None and not data.empty and 'Close' in data.columns:
        df = data[['Close']].copy()
        df = df['Close'].pct_change().dropna()
        df.name = stock
        maindf = pd.concat([maindf, df], axis=1)
    else:
        st.warning(f"No data found or invalid ticker: {stock}")

# Rename columns BEFORE plotting
if not maindf.empty:
    with st.sidebar:
        with st.expander("Rename Columns"):
            new_columns = {}
            for col in maindf.columns:
                new_name = st.text_input(f"Rename '{col}'", value=col, key=f"rename_{col}")
                new_columns[col] = new_name
            maindf.rename(columns=new_columns, inplace=True)

# Correlation matrix & heatmap
if not maindf.empty:
    matrix = maindf.corr().round(2)
    mask = np.triu(np.ones_like(matrix, dtype=bool))

    fig, ax = plt.subplots()
    sns.heatmap(matrix, annot=True, vmin=-1, vmax=1, mask=mask, cmap=color, ax=ax)
    ax.set_xlabel('')
    ax.set_ylabel('')

    with st.expander("Show Matrix", expanded=True):
        st.pyplot(fig)

# Edit & download
if not maindf.empty:
    with st.expander("Edit DataFrame"):
        edited_df = st.data_editor(maindf, use_container_width=True, height=400, hide_index=False)
        st.text("The data is provided by yahoo finance using the 'yfinance' python library.")

        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="edited_data.csv", mime="text/csv")