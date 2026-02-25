import streamlit as st
import pandas as pd
import math

# --- 核心計算邏輯 ---
def labor_round(x):
    return math.ceil(round(x, 1))

# 設定網頁標題與排版
st.set_page_config(page_title="製造業移工試算系統", layout="wide")
st.title("🏗️ 製造業移工試算系統 v7.0 (網頁版)")

# --- 側邊欄：基礎資料 ---
with st.sidebar:
    st.header("1. 基礎與母數資料")
    company_name = st.text_input("公司名稱", "範例股份有限公司")
    tw_staff = st.number_input("台灣籍員工總人數", min_value=0, value=121)
    rate_options = {"A+(35%)": 0.35, "A(25%)": 0.25, "B(20%)": 0.2, "C(15%)": 0.15, "D(10%)": 0.1}
    selected_rate_text = st.selectbox("產業基準比例", list(rate_options.keys()), index=2)
    rate = rate_options[selected_rate_text]

# --- 中間層：輸入區 (分為兩欄) ---
st.header("2. 現有移工及專業人力輸入")
col1, col2 = st.columns(2)

with col1:
    b1 = st.number_input("本案人數 (3K案)", min_value=0, value=0)
    b2 = st.number_input("增額 5% (補填)", min_value=0, value=0)
    b3 = st.number_input("增額 10% (補填)", min_value=0, value=0)
    b4 = st.number_input("增額 15% (補填)", min_value=0, value=0)
    b5 = st.number_input("增額 20% (補填)", min_value=0, value=0)

with col2:
    b6 = st.number_input("承接 5%", min_value=0, value=0)
    b7 = st.number_input("加薪方案 10%", min_value=0, value=0)
    tech = st.number_input("外國技術人力 (移工轉中階)", min_value=0, value=0)
    pro = st.number_input("外國專業人力 (白領)", min_value=0, value=0)

# --- 計算邏輯 ---
b_extra_total = b2 + b3 + b4 + b5
total_blue = b1 + b_extra_total + b6 + b7
sum_all_foreign = total_blue + tech + pro
all_denominator = tw_staff + sum_all_foreign

# 上限計算
base_deno = tw_staff + b1 + b7 + tech + pro
lim_b1 = labor_round(base_deno * rate)
lim_p20 = labor_round(all_denominator * (rate + 0.20))
up_extra_total = max(0, lim_p20 - lim_b1)
lim_b6 = labor_round(all_denominator * 0.05)
lim_b7 = labor_round(all_denominator * 0.10)
lim_tech = labor_round(all_denominator * rate)

# 四道天花板攔截
rem1 = labor_round((all_denominator - b6) * 0.4) - (b1 + b_extra_total)
rem2 = labor_round(all_denominator * 0.4) - (b1 + b_extra_total + b6)
rem3 = labor_round(all_denominator * 0.45) - (b1 + b_extra_total + b6 + b7)
rem4 = labor_round(all_denominator * 0.5) - sum_all_foreign

blue_remaining = max(0, min(rem1, rem2, rem3))
tech_remaining = max(0, min(lim_tech - tech, rem4))
final_rem = max(0, min(rem1, rem2, rem3, rem4))

# --- 即時試算報告區 ---
st.divider()
st.header("📊 即時試算結果報告")
st.subheader(f"目前公司：{company_name}")

res_col1, res_col2 = st.columns(2)
res_col1.metric("全廠外國人總數", f"{sum_all_foreign} 人")
res_col2.metric("藍領移工總數", f"{total_blue} 人")

if final_rem > 0:
    st.success(f"✅ 預估可再申請：**{final_rem}** 人 (藍領 **{blue_remaining}** / 技術 **{tech_remaining}**)")
else:
    st.error(f"⚠️ 已達法規上限，無法再申請新額度")

# --- 表格化呈現 ---
df_data = {
    "項目": ["本案", "增額(總)", "承接", "加薪", "技術人力"],
    "目前人數": [b1, b_extra_total, b6, b7, tech],
    "個別上限": [lim_b1, up_extra_total, lim_b6, lim_b7, lim_tech],
    "剩餘空間": [max(0, lim_b1-b1), max(0, up_extra_total-b_extra_total), max(0, lim_b6-b6), max(0, lim_b7-b7), max(0, lim_tech-tech)]
}
df = pd.DataFrame(df_data)
st.table(df) # 使用美觀的靜態表格呈現

st.info(f"💡 全廠總人數 (含本國+外國人)：{all_denominator} 人")