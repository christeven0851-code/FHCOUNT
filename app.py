import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
import base64

# --- 核心計算邏輯 ---
def labor_round(x):
    """勞動部公式：ROUNDUP(ROUND(X, 1), 0)"""
    return math.ceil(round(x, 1))

# --- PDF 生成函數 ---
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # 支援中文需要字體，這裡使用預設字體或簡單表格
    # 注意：雲端伺服器通常沒中文字體，若要完美中文需上傳字體檔，這裡先以通用格式處理
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Labor Calculation Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Company: {data['company_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Total Foreign Workers: {data['sum_all_foreign']}", ln=True)
    pdf.cell(200, 10, txt=f"Blue Collar Total: {data['total_blue']}", ln=True)
    pdf.cell(200, 10, txt="-----------------------------------------------------", ln=True)
    
    res_text = f"Estimate Available: {data['final_rem']} (Blue: {data['blue_rem']} / Tech: {data['tech_rem']})"
    pdf.cell(200, 10, txt=res_text, ln=True)
    pdf.ln(5)
    
    items = [
        f"Base Case (B1): Current {data['b1']} / Rem {data['rem_b1']}",
        f"Extra Case: Current {data['b_extra']} / Rem {data['rem_extra']}",
        f"Transfer Case: Current {data['b6']} / Rem {data['rem_b6']}",
        f"Salary Case: Current {data['b7']} / Rem {data['rem_b7']}",
        f"Tech Staff: Current {data['tech']} / Rem {data['rem_tech']}"
    ]
    for item in items:
        pdf.cell(200, 10, txt=item, ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

# 設定網頁標題
st.set_page_config(page_title="製造業移工試算系統", layout="centered")
st.title("🏗️ 製造業移工試算系統")

# --- 1. 基礎資料 ---
st.header("【 1.基礎資料】")
company_name = st.text_input("公司名稱", "範例公司")
tw_staff = st.number_input("台灣籍員工總人數", min_value=0, value=121)

rate_options = {"A+(35%)": 0.35, "A(25%)": 0.25, "B(20%)": 0.2, "C(15%)": 0.15, "D(10%)": 0.1}
selected_rate_text = st.selectbox("產業基準比例", list(rate_options.keys()), index=2)
rate = rate_options[selected_rate_text]

# --- 2. 現有藍領移工 ---
st.header("【2.現有藍領】")
col1, col2 = st.columns(2)
with col1:
    b1 = st.number_input("本案人數", min_value=0, value=0)
    b2 = st.number_input("增額 5%", min_value=0, value=0)
    b3 = st.number_input("增額 10%", min_value=0, value=0)
    b4 = st.number_input("增額 15%", min_value=0, value=0)
with col2:
    b5 = st.number_input("增額 20%", min_value=0, value=0)
    b6 = st.number_input("承接 5%", min_value=0, value=0)
    b7 = st.number_input("加薪方案 10%", min_value=0, value=0)

st.header("【3.技術/專業人力】")
col3, col4 = st.columns(2)
with col3:
    tech = st.number_input("外國技術人力", min_value=0, value=0)
with col4:
    pro = st.number_input("外國專業人力", min_value=0, value=0)

# --- 計算數據 ---
b_extra_total = b2 + b3 + b4 + b5
total_blue = b1 + b_extra_total + b6 + b7
sum_all_foreign = total_blue + tech + pro
all_denominator = tw_staff + sum_all_foreign

base_deno = tw_staff + b1 + b7 + tech + pro
lim_b1 = labor_round(base_deno * rate)
lim_p20 = labor_round(all_denominator * (rate + 0.20))
up_extra_total = max(0, lim_p20 - lim_b1)
lim_b6 = labor_round(all_denominator * 0.05)
lim_b7 = labor_round(all_denominator * 0.10)
lim_tech = labor_round(all_denominator * rate)

rem1 = labor_round((all_denominator - b6) * 0.4) - (b1 + b_extra_total)
rem2 = labor_round(all_denominator * 0.4) - (b1 + b_extra_total + b6)
rem3 = labor_round(all_denominator * 0.45) - (b1 + b_extra_total + b6 + b7)
rem4 = labor_round(all_denominator * 0.5) - sum_all_foreign

blue_remaining = max(0, min(rem1, rem2, rem3))
tech_remaining = max(0, min(lim_tech - tech, rem4))
final_rem = max(0, min(rem1, rem2, rem3, rem4))

# --- 4. 結果報告 ---
st.divider()
st.subheader("即時試算結果報告")

st.write(f"目前全廠使用外國人 **{sum_all_foreign}** 人、藍領總數 **{total_blue}** 人")
if final_rem >= 0:
    st.markdown(f"**預估可再申請：{final_rem} 人 ，其中藍領 {min(final_rem,blue_remaining)} 人、外國技術人力 {min(final_rem,tech_remaining)} 人**")
else:
    st.markdown(f"**:red[超出法規總量限制：{abs(final_rem)} 人]**")

st.write("-----------------------------------------------------")
st.write(f"本案：目前 {b1} 人 / 剩餘 {max(0, lim_b1-b1)} 人")
st.write(f"增額：目前 {b_extra_total} 人 / 剩餘 {max(0, up_extra_total-b_extra_total)} 人")
st.write(f"承接：目前 {b6} 人 / 剩餘 {max(0, lim_b6-b6)} 人")
st.write(f"加薪：目前 {b7} 人 / 剩餘 {max(0, lim_b7-b7)} 人")
st.write(f"技術人力：目前 {tech} 人 / 剩餘 {max(0, lim_tech-tech)} 人")

st.info(f"全廠總人數 (含本國+外國人)：{all_denominator} 人")

# --- 5. 下載 PDF 功能 ---
report_data = {
    "company_name": company_name,
    "sum_all_foreign": sum_all_foreign,
    "total_blue": total_blue,
    "final_rem": final_rem,
    "blue_rem": min(final_rem, blue_remaining),
    "tech_rem": min(final_rem, tech_remaining),
    "b1": b1, "rem_b1": max(0, lim_b1-b1),
    "b_extra": b_extra_total, "rem_extra": max(0, up_extra_total-b_extra_total),
    "b6": b6, "rem_b6": max(0, lim_b6-b6),
    "b7": b7, "rem_b7": max(0, lim_b7-b7),
    "tech": tech, "rem_tech": max(0, lim_tech-tech)
}

st.sidebar.divider()
if st.sidebar.button("📄 生成並下載 PDF 報表"):
    pdf_bytes = create_pdf(report_data)
    st.sidebar.download_button(
        label="點此下載 PDF",
        data=pdf_bytes,
        file_name=f"{company_name}.pdf",
        mime="application/pdf"
    )
