import datetime
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt

# 定義一個用於繪製和顯示股票數據的函數
def display(option, period, start, end):
    freq = {
        '1 min': '1m',
        '2 mins': '2m',
        '5 mins': '5m',
        '15 mins': '15m',
        '30 mins': '30m',
        '1h': '1h',
        '90 mins': '90m',
        '1 day': '1d',
        '5 days': '5d',
        '1 week': '1wk',
        '1 mo': '1mo',
        '3 mo': '3mo'
    }

    try:
        tickerData = yf.Ticker(option)
        st.write("""### Company presentation:""")
        st.write(tickerData.info['longBusinessSummary'])

        tickerDf = tickerData.history(period=freq[period], start=start, end=end)
        st.write(f"""
        Shown is the stock **closing price** and **volume** of {option} from {start} to {end}""")

        # 繪製收盤價趨勢圖
        if not tickerDf.empty:
            years = tickerDf.index.year.unique()
            fig, ax = plt.subplots(figsize=(10, 6))
            for year in years:
                year_data = tickerDf[tickerDf.index.year == year]
                ax.plot(year_data.index, year_data['Close'], label=str(year))

            plt.xlabel('Date')
            plt.ylabel('Closing Price')
            plt.title('Stock Trend')
            plt.legend()
            st.pyplot(fig)

            # 顯示交易量圖表
            st.write("### Stock Volume:")
            st.line_chart(tickerDf.Volume)
        else:
            st.error("No data available for the selected date range.")
    except yf.exceptions.YFinanceException as e:
        st.error(f"Error occurred: {e}")

# 界面布局和表單
st.write("# Simple Stock Price App")

with st.form("stock_selection_form"):
    option = st.text_input('Enter the company symbol (e.g., AAPL for Apple/2330.TW for TSMC-上市/3105.TWO for 穩懋-上櫃)')
    period = st.select_slider(
        'Select a frequency of data to display',
        options=['1 min', '2 mins', '5 mins', '15 mins', '30 mins', '1h', '90 mins', '1 day', '5 days', '1 week', '1 mo', '3 mo'],
        value='1 day'
    )
    col1, col2 = st.columns(2)
    start = col1.date_input("Select the start date (format is yyyy-MM-dd)", datetime.date(2010, 1, 1))
    end = col2.date_input("Select the end date (format is yyyy-MM-dd)")

    # 確保結束日期在開始日期之後
    if start > end:
        st.error("End date must be after start date.")

    submitted = st.form_submit_button("Submit")
    if submitted:
        display(option, period, start, end)
