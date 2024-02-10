import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_data(file_path):
    df = pd.read_csv(file_path, sep=';')  # 使用分号作为分隔符读取 CSV 文件
    #df = pd.read_csv(file_path)
    # 確保資料中存在 'Event' 欄位，如果不存在則不執行下面的操作
    if 'Event' in df.columns:
        # 將 'Event' 欄位移動到第四個位置
        cols = df.columns.tolist()  # 獲取所有欄位名稱的列表
        event_index = cols.index('Event')  # 找到 'Event' 欄位的當前索引
        # 移動 'Event' 欄位
        cols.insert(3, cols.pop(event_index))  # 從當前位置移除，並插入到索引為3的位置（第四列）
        df = df.reindex(columns=cols)  # 重新排列欄位順序
        df['Event'] = df['Event'].fillna('')  # 將 'Event' 欄位中的 NaN 值填充為空字符串
    return df

def select_stock_id(data):
    unique_stock_ids = data['股票代號'].unique()
    selected_stock_id = st.selectbox("Select Stock ID", unique_stock_ids)
    return selected_stock_id

def filter_news_data(data):
    # 只保留具有新聞值的列
    filtered_data = data[data['Event'] != '']
    return filtered_data

def plot_trend_chart(filtered_data, y_axis_range):
    filtered_data['date'] = pd.to_datetime(filtered_data['date']).dt.date  
    filtered_data = filtered_data.sort_values(by='date')
    
    fig = px.line(filtered_data, x='date', y='收盤價', labels={'收盤價': 'Closing Price'}, title='Stock Price Trend')
    fig.update_xaxes(type='category')
    fig.update_yaxes(range=y_axis_range)

    # Add event markers if 'Event' column has entries
    event_data = filtered_data[filtered_data['Event'] != '']
    for index, row in event_data.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['date']],
            y=[row['收盤價']],
            mode='markers',
            marker=dict(size=10, color='red'),
            hoverinfo='text',
            text=row['Event'],  
            name='Event',
            showlegend=False
        ))

    st.plotly_chart(fig)
    
    st.text_input("Enter your text here", key="event_text_input")

def main():
    st.title("Stock Price Trend Web App")

    #file_path = "corrected_all_data_with_date_streamlit_test.csv"
    file_path = "result.csv"
    
    

    df = load_data(file_path)
    st.write("Please select a stock ID:")
    selected_stock_id = select_stock_id(df)
    

    # 檢查是否有選擇股票 ID
    if selected_stock_id:
        with pd.option_context('mode.chained_assignment', None):
            filtered_data = df[df['股票代號'] == selected_stock_id]
            filtered_data['收盤價'] = filtered_data['收盤價'].astype(float)

        mean_price = filtered_data['收盤價'].mean()
        sigma = filtered_data['收盤價'].std()

        min_price = mean_price - 6 * sigma
        max_price = mean_price + 6 * sigma

        st.write("Selected Stock ID:", selected_stock_id)
        df_with_event = filter_news_data(filtered_data)
        
        # 删除索引列
        df_with_event.reset_index(drop=True, inplace=True)
        
        st.dataframe(df_with_event)

        min_price = st.number_input("Enter Minimum Y-axis Value", min_value=0.0, max_value=max_price, value=min_price)
        max_price = st.number_input("Enter Maximum Y-axis Value", min_value=min_price, max_value=10000.0, value=max_price)

        if st.button("Reset to Default Range"):
            min_price = mean_price - 6 * sigma
            max_price = mean_price + 6 * sigma
            st.write("Reset to the default Y-axis range")
            
        y_axis_range = (min_price, max_price)

        plot_trend_chart(filtered_data, y_axis_range)


if __name__ == '__main__':
    main()
