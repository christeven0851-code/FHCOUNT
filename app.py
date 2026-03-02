import streamlit as st
import pandas as pd
import math
import os
from fpdf import FPDF

# --- 核心計算邏輯 ---
def labor_round(x):
    return math.ceil(round(x, 1))

# --- PDF 生成函數 (修正版) ---
# --- PDF 生成函數 (同步調整排版) ---
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. 字體註冊
    font_filename = "msjh.ttc" 
    try:
        target_font = None
        if os.path.exists(font_filename):
            target_font = font_filename
        elif os.path.exists("MSJH.TTC"):
            target_font = "MSJH.TTC"

        if target_font:
            pdf.add_font('MSJH', '', target_font) 
            pdf.set_font('MSJH', size=24)
            font_ready = True
        else:
            font_ready = False
    except:
        font_ready = False

    if font_ready:
        # --- PDF 內容排版 ---
        # 標題
        pdf.cell(200, 10, txt=f"{data['company_name']} 移工試算報告", ln=True, align='C')
        pdf.ln(10)
        
        # 基礎現況
        pdf.set_font('MSJH', size=11)
        pdf.cell(200, 8, txt=f"公司名稱：{data['company_name']}", ln=True)
        pdf.cell(200, 8, txt=f"目前現況：外國人總數 {data['sum_all_foreign']} 人 (藍領 {data['total_blue']} / 技術 {data['tech']})，有效及廢聘名額 {data['total_control']}", ln=True)
        pdf.cell(200, 8, txt=f"全廠總人數 (含本國籍)：{data['all_deno']} 人", ln=True)
        pdf.ln(5)
        
        # 核心結論 (加粗感)
        pdf.set_font('MSJH', size=14)
        pdf.cell(200, 10, txt=f"【預估可再申請總數：{data['final_rem-total_control']} 人】", ln=True)
        
        pdf.set_font('MSJH', size=12)
        pdf.cell(200, 8, txt=f"  ● 藍領尚可申請：{data['blue_rem']} 人", ln=True)
        pdf.cell(200, 8, txt=f"  ● 外國技術人力尚可申請：{data['tech_rem']} 人", ln=True)
        pdf.set_font('MSJH', size=10)
        pdf.cell(200, 8, txt="  (註：兩者加總不可超過預估可再申請總數)", ln=True)
        pdf.ln(10)
        
        # 詳細項目餘額
        pdf.set_font('MSJH', size=12)
        pdf.cell(200, 10, txt="【各項案目前人數及空間明細】", ln=True)
        pdf.cell(200, 1, txt="-" * 80, ln=True)
        pdf.ln(2)
        
        # 以清單方式呈現表格內容
        items = [
            ("項目", "目前使用", "剩餘空間"),
            ("本案", f"{data['b1']} 人", f"{data['rem_b1']} 人"),
            ("增額", f"{data['b_extra_total']} 人", f"{data['rem_extra']} 人"),
            ("承接", f"{data['b6']} 人", f"{data['rem_b6']} 人"),
            ("加薪", f"{data['b7']} 人", f"{data['rem_b7']} 人"),
            ("技術人力", f"{data['tech']} 人", f"{data['rem_tech']} 人")
        ]

        for name, current, remain in items:
            pdf.cell(60, 10, txt=name, border=0)
            pdf.cell(60, 10, txt=current, border=0)
            pdf.cell(60, 10, txt=remain, border=0, ln=True)     

            
    else:
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Font Error: Please check msjh.ttc", ln=True)

    return bytes(pdf.output())

# --- Streamlit 介面 ---
st.set_page_config(page_title="製造業移工試算系統", layout="centered")
st.title("🏗️ 製造業移工試算系統")

# 1. 基礎資料
st.header("【 1.基礎資料】")
company_name = st.text_input("公司名稱", "範例")
tw_staff = st.number_input("台灣籍員工總人數", min_value=0, value=100)
rate_options = {"A+(35%)": 0.35, "A(25%)": 0.25, "B(20%)": 0.2, "C(15%)": 0.15, "D(10%)": 0.1}
selected_rate_text = st.selectbox("產業基準比例", list(rate_options.keys()), index=2)
rate = rate_options[selected_rate_text]

# 目前使用的最高增額
rate_options2 = {"+20%": 0.20, "+15%": 0.15, "+10%": 0.10, "+5%": 0.05, "無": 0}
select_extra_rate = st.selectbox("現在申請最高增額%數", list(rate_options2.keys()), index=2)
use_extra_rate = rate_options2[select_extra_rate]

# 2. 現有人力 (加入動態鎖定邏輯)
st.header("【2.現有藍領】")

# 判斷邏輯：根據選擇的比例鎖定增額輸入框
disable_10 = (selected_rate_text == "A+(35%)")
disable_15 = (selected_rate_text == "A+(35%)")
disable_20 = (selected_rate_text == "A+(35%)" or selected_rate_text == "A(25%)")

col1, col2 = st.columns(2)
with col1:
    b1 = st.number_input("本案人數", min_value=0, value=10)
    b2 = st.number_input("增額 5%", min_value=0, value=5)
    
    # 如果是 A+，這裡會變灰色不能輸入，且強制數值為 0
    b3 = st.number_input("增額 10%", min_value=0, value=0 if disable_10 else 0, disabled=disable_10)
    b4 = st.number_input("增額 15%", min_value=0, value=0 if disable_15 else 0, disabled=disable_15)

with col2:
    # 如果是 A+ 或 A，這裡會變灰色不能輸入
    b5 = st.number_input("增額 20%", min_value=0, value=0 if disable_20 else 0, disabled=disable_20)
    b6 = st.number_input("承接 5%", min_value=0, value=0)
    b7 = st.number_input("加薪方案 10%", min_value=0, value=0)

# 💡 增加小提醒，讓使用者知道為什麼被鎖定
if disable_20:
    st.caption(f"⚠️ 當前產業比例為 {selected_rate_text}，受限於 40% 總量限制，部分增額選項已鎖定。")

st.header("【3.技術/專業人力】")
col3, col4 = st.columns(2)
with col3:
    tech = st.number_input("外國技術人力", min_value=0, value=0)
with col4:
    pro = st.number_input("外國專業人力", min_value=0, value=0)

st.header("【4.有效/廢聘名額】")
col5, col6 = st.columns(2)
with col5:
    val = st.number_input("有效名額", min_value=0, value=0)
with col6:
    abo = st.number_input("廢聘管制名額", min_value=0, value=0)

# 3. 計算邏輯
# 增額
b_extra_total = b2 + b3 + b4 + b5

#增額使用到的比例
if b5 > 0 :
    max_extra_rate = 0.20
elif b4 >0 :
    max_extra_rate = 0.15
elif b3 >0 :
    max_extra_rate = 0.10
elif b2 >0 :
    max_extra_rate = 0.05
else :
    max_extra_rate = 0.00

# 所有藍領
total_blue = b1 + b_extra_total + b6 + b7
# 所有外國人
sum_all_foreign = total_blue + tech + pro
# 全體員工
all_denominator = tw_staff + sum_all_foreign
# 管控名額
total_control = val + abo

# 內框人數基準(台灣+本案+技術+專業)
base_deno = tw_staff + b1 + tech + pro
# 內框人數上限=內框人數基準*比例
lim_b1 = labor_round(base_deno * rate)
# 外框人數上限=全體員工*(比例+20%)
lim_p20 = labor_round((all_denominator - b6) * min ((rate + 0.20), 0.40))
# 附加案人數上限                      
up_extra_total = max(0, lim_p20 - lim_b1)
# 承接案人數上限 (需計算目前使用增額比例)
lim_b6 = labor_round(all_denominator * (rate + use_extra_rate + 0.05)) - labor_round(all_denominator * (rate + use_extra_rate +0.05))
# 加薪案人數上限      
lim_b7 = min(labor_round(all_denominator * 0.10) , labor_round(all_denominator * min (rate + 0.20 + 0.10 , 0.45)))
# 外國技術人數上限      
lim_tech = labor_round(all_denominator * rate)

#本案餘額
rem1 = lim_b1 - b1
#附加案餘額
rem2 = up_extra_total - b_extra_total
#藍領上限
rem3 = labor_round(all_denominator * min ((rate + 0.20+ 0.10 ),0.45)) - (b1 + b_extra_total + b6 + b7)
#外國人人數上限
rem4 = labor_round(all_denominator * 0.5) - sum_all_foreign

#藍領尚可使用
blue_remaining = rem1 + rem2 + lim_b6 + lim_b7 -abo - total_blue
tech_remaining = max(0, min(lim_tech - tech, rem4))
final_rem = rem4

# 4. 結果報告呈現
st.divider()
st.subheader("📋 即時試算結果報告")
st.write(f"{lim_b1}、{up_extra_total}、{lim_b6}、{lim_b7}、{total_blue}")

st.write(f"目前全廠使用外國人 **{sum_all_foreign}** 人、藍領總數 **{total_blue}** 人、外國技術人力 **{tech}** 人")
if total_control > 0:
    st.write(f"(另尚有有效名額**{val}** 人及廢聘名額 **{abo}** 人)")
else:
    st.write(f"")

if final_rem >= 0:
    st.success(f"**預估可再使用：{final_rem-abo} 人**")
    st.markdown(f"其中藍領跟外國技術人力尚可使用的人數分別為 **{min(final_rem, blue_remaining)} 人** 及 **{min(final_rem, tech_remaining)} 人**")
    st.info("💡 提醒：再使用藍領跟外國技術人力加總不能超過預估可再使用人數")
else:
    st.error(f"⚠️ 超出法規總量限制：{abs(final_rem)} 人")

# 5. 詳細數據表格
st.write("")
df_data = {
    "項目": ["本案", "增額(總)", "承接", "加薪", "技術人力"],
    "目前人數": [b1, b_extra_total, b6, b7, tech],
    "個別上限": [lim_b1, up_extra_total, lim_b6, lim_b7, lim_tech],
    "剩餘使用空間": [max(0, lim_b1-b1), max(0, up_extra_total-b_extra_total), max(0, lim_b6-b6-total_control), max(0, lim_b7-b7-total_control), max(0, lim_tech-tech)]
}
st.table(pd.DataFrame(df_data))

st.info(f"全廠總人數 (含本國+外國人)：{all_denominator} 人")

# 下載 PDF 按鈕
report_data = {
    "company_name": company_name, 
    "sum_all_foreign": sum_all_foreign, 
    "total_blue": total_blue,
    "final_rem": final_rem, 
    "blue_rem": min(final_rem, blue_remaining), 
    "tech_rem": min(final_rem, tech_remaining),
    "b1": b1, 
    "rem_b1": max(0, lim_b1-b1), 
    "b_extra_total": b_extra_total, 
    "rem_extra": max(0, up_extra_total-b_extra_total),
    "b6": b6, 
    "rem_b6": max(0, lim_b6-b6), 
    "b7": b7, 
    "rem_b7": max(0, lim_b7-b7),
    "tech": tech, 
    "rem_tech": max(0, lim_tech-tech), 
    "all_deno": all_denominator
}

st.sidebar.header("📋 報表匯出")
if st.sidebar.button("🛠️ 生成 PDF 報表"):
    try:
        pdf_bytes = create_pdf(report_data)
        st.sidebar.download_button(
            label="💾 點此下載 PDF",
            data=pdf_bytes,
            file_name=f"{company_name}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.sidebar.error(f"生成失敗：{e}")


