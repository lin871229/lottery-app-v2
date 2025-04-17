import streamlit as st
import pandas as pd
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="機構抽籤系統", layout="wide")
st.title("🏠 特約機構抽籤系統（寫入 Google Sheet）")

# Google Sheets 設定
SHEET_ID = "1a3aui6nxUoZNBLeT57-M76M9qqychHsLA6taAktSbAQ"
WORKSHEET_NAME = "聖功醫院抽籤記錄表"

# 使用 secrets.toml 建立 Google Sheets 連線
@st.cache_resource
def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
    return sheet

sheet = connect_to_gsheet()

# 上傳 Excel 檔案
uploaded_file = st.file_uploader("請上傳特約機構名冊 Excel 檔案", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = "本市113年7月1日起特約居家式長照機構名冊"
    df_raw = xls.parse(sheet_name)

    df = df_raw.iloc[2:].copy()
    df.columns = [
        "編號", "備註", "單位名稱", "設立區域", "地址", "電話", "Email",
        "長照服務項目", "居家服務履約區域", "居家喘息服務履約區域",
        "短照喘息服務履約區域", "服務時段", "承辦人員"
    ]

    kaohsiung_areas = [
        "鹽埕區", "鼓山區", "左營區", "楠梓區", "三民區", "新興區", "前金區",
        "苓雅區", "前鎮區", "旗津區", "小港區", "鳳山區", "林園區", "大寮區",
        "大樹區", "大社區", "仁武區", "鳥松區", "岡山區", "橋頭區", "燕巢區",
        "田寮區", "阿蓮區", "路竹區", "湖內區", "茄萣區", "永安區", "彌陀區",
        "梓官區", "旗山區", "美濃區", "六龜區", "甲仙區", "杉林區", "內門區",
        "茂林區", "桃源區", "那瑪夏區"
    ]

    area_cols = ["居家喘息服務履約區域", "短照喘息服務履約區域"]
    all_area_texts = df[area_cols[0]].fillna('') + '\\n' + df[area_cols[1]].fillna('')
    split_texts = all_area_texts.str.split('[、，\\n()（）]')
    all_areas = set()
    for lst in split_texts:
        all_areas.update([a.strip() for a in lst if a and "區" in a and a in kaohsiung_areas])
    area_options = sorted(all_areas)

    if 'used_respite' not in st.session_state:
        st.session_state.used_respite = set()
    if 'used_shortterm' not in st.session_state:
        st.session_state.used_shortterm = set()

    area_respite = st.sidebar.selectbox("居家喘息", area_options, key="respite_area")
    if st.sidebar.button("抽籤", key="draw_respite"):
        df_match = df[df["居家喘息服務履約區域"].fillna('').str.contains(area_respite)]
        available = df_match[~df_match["單位名稱"].isin(st.session_state.used_respite)]
        if len(available) > 0:
            drawn = available.sample(n=1, random_state=random.randint(1, 9999))
            st.session_state.used_respite.add(drawn["單位名稱"].iloc[0])
            st.success(f"✅ 居家喘息（{area_respite}）抽中：")
            st.dataframe(drawn[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))
            row = [
                drawn["單位名稱"].iloc[0],
                drawn["設立區域"].iloc[0],
                drawn["地址"].iloc[0],
                drawn["電話"].iloc[0],
                "居家喘息",
                area_respite,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
        else:
            st.warning(f"🚫 居家喘息【{area_respite}】已無可抽籤機構。")

    area_shortterm = st.sidebar.selectbox("短照喘息", area_options, key="shortterm_area")
    if st.sidebar.button("抽籤", key="draw_shortterm"):
        df_match = df[df["短照喘息服務履約區域"].fillna('').str.contains(area_shortterm)]
        available = df_match[~df_match["單位名稱"].isin(st.session_state.used_shortterm)]
        if len(available) > 0:
            drawn = available.sample(n=1, random_state=random.randint(1, 9999))
            st.session_state.used_shortterm.add(drawn["單位名稱"].iloc[0])
            st.success(f"✅ 短照喘息（{area_shortterm}）抽中：")
            st.dataframe(drawn[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))
            row = [
                drawn["單位名稱"].iloc[0],
                drawn["設立區域"].iloc[0],
                drawn["地址"].iloc[0],
                drawn["電話"].iloc[0],
                "短照喘息",
                area_shortterm,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            sheet.append_row(row)
        else:
            st.warning(f"🚫 短照喘息【{area_shortterm}】已無可抽籤機構。")

else:
    st.info("請先上傳 Excel 檔案。")
