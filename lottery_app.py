import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="機構抽籤系統", layout="wide")
st.title("🏠 特約機構抽籤系統")

# 模擬機構資料
data = {
    "單位名稱": ["高雄市私立富宜居家長照機構", "高雄市私立富盛居家長照機構"],
    "設立區域": ["苓雅區", "左營區"],
    "地址": ["高雄市苓雅區中華四路2號13樓B室", "高雄市左營區自由路99號"],
    "電話": ["TEL: 0938-091897", "TEL: 0939-725712"]
}

# 將資料轉換為 DataFrame
df = pd.DataFrame(data)

# 顯示資料表
st.title("可選機構名單")
st.dataframe(df)

# 初始化抽籤結果存儲
if 'lottery_results' not in st.session_state:
    st.session_state.lottery_results = []

# 顯示已抽中的機構
if st.session_state.lottery_results:
    selected_results = st.selectbox("已抽籤機構", st.session_state.lottery_results, index=0)
else:
    selected_results = st.selectbox("已抽籤機構", ["尚無抽中機構"], index=0)

# 按鈕進行抽籤
if st.button("抽籤"):
    # 只抽未被抽中的機構
    available = df[~df['單位名稱'].isin(st.session_state.lottery_results)]
    
    if not available.empty:
        drawn = available.sample(n=1)
        drawn_name = drawn['單位名稱'].iloc[0]
        st.session_state.lottery_results.append(drawn_name)
        st.success(f"✅ 抽中：{drawn_name}")
    else:
        st.warning("所有機構已抽完。")

