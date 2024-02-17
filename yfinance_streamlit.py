import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 設定頁面標題
st.title('股價資料')

# 輸入股票代碼
ticker_symbol = st.text_input("請輸入股票代碼（例如GOOGL）：")

# 添加日期選擇器
start_date = st.date_input("選擇起始日期", value=None, min_value=None, max_value=None, key=None)
end_date = st.date_input("選擇結束日期", value=None, min_value=None, max_value=None, key=None)

# 確保結束日期不早於起始日期
if start_date is not None and end_date is not None:
    if start_date > end_date:
        st.error('錯誤：結束日期不能早於起始日期。請重新選擇。')
    else:
        st.success('你選擇的起始日期是: {}，結束日期是: {}'.format(start_date, end_date))

        if ticker_symbol:
            # 獲取股票的信息
            stock = yf.Ticker(ticker_symbol)
            company_name = stock.info['longName']

            # 獲取股票的股價資料
            stock_data = stock.history(period='1d', start=start_date, end=end_date)

            # 顯示股價資料
            st.write("### 股價資料")
            st.write(stock_data)

            # 創建趨勢圖
            st.write("### 股價趨勢圖")
            fig = go.Figure()

            # 繪製每年的數據
            for year in range(start_date.year, end_date.year + 1):
                year_data = stock_data.loc[str(year)+'-01-01':str(year)+'-12-31']
                fig.add_trace(go.Scatter(x=year_data.index, y=year_data['Close'], mode='lines', name=str(year)))

            fig.update_layout(title=f'{company_name} ({ticker_symbol}) 股價趨勢圖', xaxis_title='日期', yaxis_title='股價（美元）')
            st.plotly_chart(fig, use_container_width=True)
