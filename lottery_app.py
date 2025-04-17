import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="機構抽籤系統", layout="wide")
st.title("🏠 特約機構抽籤系統")

# 上傳 Excel 檔案
uploaded_file = st.file_uploader("請上傳特約機構名冊 Excel 檔案", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = "本市113年7月1日起特約居家式長照機構名冊"
    df_raw = xls.parse(sheet_name)

    # 清理資料：跳過前兩列標題與說明，重新命名欄位
    df = df_raw.iloc[2:].copy()
    df.columns = [
        "編號", "備註", "單位名稱", "設立區域", "地址", "電話", "Email",
        "長照服務項目", "居家服務履約區域", "居家喘息服務履約區域",
        "短照喘息服務履約區域", "服務時段", "承辦人員"
    ]

    # 篩選高雄地區的區域
    kaohsiung_areas = [
        "苓雅區", "三民區", "鳳山區", "左營區", "楠梓區", "小港區", "鼓山區",
        "鹽埕區", "前金區", "新興區", "旗山區", "旗津區", "苓雅分區", "三民分區",
        "左楠分區", "小港分區", "岡山區", "橋頭區", "林園區", "大寮區", "大樹區"
    ]

    # 擷取高雄地區區域
    area_cols = ["居家喘息服務履約區域", "短照喘息服務履約區域"]
    all_area_texts = df[area_cols[0]].fillna('') + '\\n' + df[area_cols[1]].fillna('')
    split_texts = all_area_texts.str.split('[、，\\n()（）]')
    all_areas = set()
    for lst in split_texts:
        all_areas.update([a.strip() for a in lst if a and "區" in a and a in kaohsiung_areas])
    area_options = sorted(all_areas)

    # 側邊欄選擇區域
    st.sidebar.header("🎯 篩選條件")
    selected_area_respite = st.sidebar.selectbox("選擇居家喘息服務履約區域：", area_options)
    selected_area_shortterm = st.sidebar.selectbox("選擇短照喘息服務履約區域：", area_options)
    num_to_draw = 1  # 每次只抽取一間機構

    # 進行篩選（兩欄各自篩選）
    df_match_respite = df[df["居家喘息服務履約區域"].fillna('').str.contains(selected_area_respite)]
    df_match_shortterm = df[df["短照喘息服務履約區域"].fillna('').str.contains(selected_area_shortterm)]
    
    # 抽取過的機構儲存
    if 'used_respite' not in st.session_state:
        st.session_state.used_respite = set()
    if 'used_shortterm' not in st.session_state:
        st.session_state.used_shortterm = set()

    # 分別抽取
    st.markdown(f"### ✅ 居家喘息服務履約區域 `{selected_area_respite}` 的機構")
    available_respite = df_match_respite[~df_match_respite["單位名稱"].isin(st.session_state.used_respite)]
    if len(available_respite) > 0:
        drawn_respite = available_respite.sample(n=1, random_state=random.randint(1, 9999))
        st.session_state.used_respite.add(drawn_respite["單位名稱"].iloc[0])  # 將抽取的機構標記為已使用
        st.dataframe(drawn_respite[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))
    else:
        st.warning(f"找不到更多符合 `{selected_area_respite}` 區域的機構。")

    st.markdown(f"### ✅ 短照喘息服務履約區域 `{selected_area_shortterm}` 的機構")
    available_shortterm = df_match_shortterm[~df_match_shortterm["單位名稱"].isin(st.session_state.used_shortterm)]
    if len(available_shortterm) > 0:
        drawn_shortterm = available_shortterm.sample(n=1, random_state=random.randint(1, 9999))
        st.session_state.used_shortterm.add(drawn_shortterm["單位名稱"].iloc[0])  # 將抽取的機構標記為已使用
        st.dataframe(drawn_shortterm[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))
    else:
        st.warning(f"找不到更多符合 `{selected_area_shortterm}` 區域的機構。")
else:
    st.info("請先上傳 Excel 檔案。")
