import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df['Event'] = df['Event'].fillna('') 
    return df

def select_stock_id(data):
    unique_stock_ids = data['股票代號'].unique()
    selected_stock_id = st.selectbox("Select Stock ID", unique_stock_ids)
    return selected_stock_id

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

    # # Display text input box when event marker is clicked
    # selected_point = st.session_state.get('selected_point')
    # if selected_point is not None:
    #     st.text_input("Enter your text here", key="event_text_input")

def main():
    st.title("Stock Price Trend Web App")
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    min_price = 0.0  
    max_price = 1000.0  

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.write("Please select a stock ID:")
        selected_stock_id = select_stock_id(df)

        with pd.option_context('mode.chained_assignment', None):
            filtered_data = df[df['股票代號'] == selected_stock_id]
            filtered_data['收盤價'] = filtered_data['收盤價'].astype(float)

        mean_price = filtered_data['收盤價'].mean()
        sigma = filtered_data['收盤價'].std()

        min_price = mean_price - 6 * sigma
        max_price = mean_price + 6 * sigma

        st.dataframe(filtered_data)

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
