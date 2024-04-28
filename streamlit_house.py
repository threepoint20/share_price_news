import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.font_manager import FontProperties
import sqlite3
import io


## 設置 matplotlib 支援中文顯示（使用系统默认字体）
#plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # 或其他可用的字体
#plt.rcParams['axes.unicode_minus'] = False

# 設置matplotlib支援中文顯示
font_prop = FontProperties(fname='GenSekiGothic-L.ttc')  # 示範路径，请根据实际情况修改
plt.rcParams['font.sans-serif'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False



# 連接到 SQLite 資料庫
conn = sqlite3.connect('target.db')

# 載入資料
@st.cache_data
def load_data():
    data = pd.read_sql('SELECT * FROM sale_house_record;', conn)
    return data


# 將交易年月日轉換為 datetime 格式
def convert_date(date_int):
    date_str = str(date_int)  # 將整數轉換為字符串
    year = int(date_str[:3]) + 1911
    month = int(date_str[3:5])
    day = int(date_str[5:])

    try:
        return datetime(year, month, day)
    except ValueError as e:
        print(f"無效的日期: 年={year}, 月={month}, 日={day}")
        print("錯誤信息:", e)
        # 可以返回 None 或特定的默認日期
        return None


# 繪製趨勢圖
def plot_trend(data, title, y_label):
    # 清除空字符串或者不可轉換為浮點數的值
    data = data.copy()
    data[y_label] = pd.to_numeric(data[y_label], errors='coerce')  # 'coerce'會將錯誤轉換為NaN
    data.dropna(subset=[y_label], inplace=True)  # 刪除y_label列中含有NaN的行

    # 繼續繪製趨勢圖
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(data['交易年月日'], data[y_label], marker='o', s=50)
    ax.set_xlabel('交易年月日', fontsize=12)
    ax.set_ylabel(f'{y_label} ($NT)', fontsize=12)
    ax.set_title(title, fontsize=14)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    st.pyplot(fig)

# 主程式
def main():
    st.title('新竹房產交易趨勢分析')

    # 載入資料
    data = load_data()

    # 從 'Name' 欄位中獲取所有值作為下拉式菜單的選項
    name_options = data['Name'].unique()
    trade_object_options = data['交易標的'].unique()
    floor_level_options = data['建物型態'].unique()

    # 選擇要顯示的名稱、交易標的和移轉層次
    selected_name = st.selectbox('選擇名稱', options=[None] + list(name_options))
    selected_trade_object = st.multiselect('選擇交易標的', options=trade_object_options)
    selected_floor_level = st.multiselect('建物型態', options=floor_level_options)

    # 篩選資料
    filtered_data = data
    if selected_name:
        filtered_data = filtered_data[filtered_data['Name'] == selected_name]
    if selected_trade_object:
        filtered_data = filtered_data[filtered_data['交易標的'].isin(selected_trade_object)]
    if selected_floor_level:
        filtered_data = filtered_data[filtered_data['建物型態'].isin(selected_floor_level)]

    # 將交易年月日轉換為 datetime 格式
    if '交易年月日' in filtered_data.columns:
        filtered_data['交易年月日'] = filtered_data['交易年月日'].apply(convert_date)

    # 確保單價元平方公尺為數值型，並計算每坪單價
    if '單價元平方公尺' in filtered_data.columns:
        filtered_data['單價元平方公尺'] = pd.to_numeric(filtered_data['單價元平方公尺'], errors='coerce')
        filtered_data['單價元坪'] = filtered_data['單價元平方公尺'] * 3.3058  # 計算每坪單價

    # 確保 '總價元' 列是數字型態
    filtered_data['總價元'] = pd.to_numeric(filtered_data['總價元'], errors='coerce')

    # 檢查是否有NaN值存在
    if filtered_data['總價元'].isnull().any():
        st.write("一些 '總價元' 數據不能轉換為數字，這些將不被計入趨勢圖。")

    # 然後進行除法操作
    filtered_data['總價元 (萬)'] = filtered_data['總價元'] / 10000  # 轉換為萬元單位

    # 繪製總價元趨勢圖
    if not filtered_data.empty and '總價元 (萬)' in filtered_data.columns:
        plot_trend(filtered_data, f'{selected_name if selected_name else "所有名稱"} 房產總價趨勢', '總價元 (萬)')
    
    # 繪製單價元坪趨勢圖
    if not filtered_data.empty and '單價元坪' in filtered_data.columns:
        plot_trend(filtered_data, f'{selected_name if selected_name else "所有名稱"} 房產單價每坪趨勢', '單價元坪')

if __name__ == "__main__":
    main()
