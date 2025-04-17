import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="機構抽籤系統", layout="wide")
st.title("🏠 特約機構抽籤系統（雙獨立抽籤按鈕）")

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

    # 高雄地區列表
    kaohsiung_areas = [
        "苓雅區", "三民區", "鳳山區", "左營區", "楠梓區", "小港區", "鼓山區",
        "鹽埕區", "前金區", "新興區", "旗山區", "旗津區", "苓雅分區", "三民分區",
        "左楠分區", "小港分區", "岡山區", "橋頭區", "林園區", "大寮區", "大樹區"
    ]

    # 擷取所有符合高雄區域名稱
    area_cols = ["居家喘息服務履約區域", "短照喘息服務履約區域"]
    all_area_texts = df[area_cols[0]].fillna('') + '\\n' + df[area_cols[1]].fillna('')
    split_texts = all_area_texts.str.split('[、，\\n()（）]')
    all_areas = set()
    for lst in split_texts:
        all_areas.update([a.strip() for a in lst if a and "區" in a and a in kaohsiung_areas])
    area_options = sorted(all_areas)

    # session 狀態記錄
    if 'used_respite' not in st.session_state:
        st.session_state.used_respite = set()
    if 'used_shortterm' not in st.session_state:
        st.session_state.used_shortterm = set()

    # 左右兩欄分開控制
    col1, col2 = st.columns(2)

    with col1:
        st.header("🏡 居家喘息服務履約區域")
        area_respite = st.selectbox("選擇區域（居家喘息）", area_options, key="respite_area")
        if st.button("抽籤（居家喘息）", key="draw_respite"):
            df_match_respite = df[df["居家喘息服務履約區域"].fillna('').str.contains(area_respite)]
            available_respite = df_match_respite[~df_match_respite["單位名稱"].isin(st.session_state.used_respite)]
            if len(available_respite) > 0:
                drawn = available_respite.sample(n=1, random_state=random.randint(1, 9999))
                st.session_state.used_respite.add(drawn["單位名稱"].iloc[0])
                st.success("✅ 抽中機構：")
                st.dataframe(drawn[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))
            else:
                st.warning("🚫 此區域已無可抽籤機構。")

    with col2:
        st.header("🏥 短照喘息服務履約區域")
        area_shortterm = st.selectbox("選擇區域（短照喘息）", area_options, key="shortterm_area")
        if st.button("抽籤（短照喘息）", key="draw_shortterm"):
            df_match_shortterm = df[df["短照喘息服務履約區域"].fillna('').str.contains(area_shortterm)]
            available_shortterm = df_match_shortterm[~df_match_shortterm["單位名稱"].isin(st.session_state.used_shortterm)]
            if len(available_shortterm) > 0:
                drawn = available_shortterm.sample(n=1, random_state=random.randint(1, 9999))
                st.session_state.used_shortterm.add(drawn["單位名稱"].iloc[0])
                st.success("✅ 抽中機構：")
                st.dataframe(drawn[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))
            else:
                st.warning("🚫 此區域已無可抽籤機構。")

else:
    st.info("請先上傳 Excel 檔案。")
