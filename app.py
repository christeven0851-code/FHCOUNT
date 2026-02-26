def create_pdf(data):
    # 使用 FPDF2，並指定為實體格式
    pdf = FPDF()
    pdf.add_page()
    
    # 取得字體路徑 (確保在 Streamlit Cloud 也能讀到同資料夾檔案)
    import os
    font_path = os.path.join(os.getcwd(), "msjh.ttf")
    
    # 註冊微軟正黑體
    try:
        # 重點：必須確保檔名完全一致（包含大小寫）
        pdf.add_font('MSJH', '', font_path)
        pdf.set_font('MSJH', size=16)
    except Exception as e:
        # 如果還是失敗，顯示具體錯誤在網頁上方便排查
        st.error(f"字體檔案讀取錯誤: {e}")
        # 萬一失敗，強制用預設字體，但中文會變問號（避免程式直接崩潰）
        pdf.set_font("Arial", size=12)

    # --- 寫入內容 (確保每一行都先設定字體) ---
    pdf.cell(200, 10, txt="製造業移工試算報告", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font('MSJH', size=12)
    pdf.cell(200, 10, txt=f"公司名稱: {data['company_name']}", ln=True)
    pdf.cell(200, 10, txt=f"目前全廠使用外國人 {data['sum_all_foreign']} 人、藍領總數 {data['total_blue']} 人", ln=True)
    
    # 核心結論
    pdf.set_font('MSJH', size=13)
    pdf.cell(200, 10, txt=f"預估可再申請：{data['final_rem']} 人", ln=True)
    pdf.cell(200, 10, txt=f"(其中藍領 {data['blue_rem']} 人、外國技術人力 {data['tech_rem']} 人)", ln=True)
    
    pdf.set_font('MSJH', size=12)
    pdf.cell(200, 10, txt="-" * 50, ln=True)
    
    # 詳細數據
    pdf.cell(200, 10, txt=f"本案：目前 {data['b1']} 人 / 剩餘 {data['rem_b1']} 人", ln=True)
    pdf.cell(200, 10, txt=f"增額：目前 {data['b_extra']} 人 / 剩餘 {data['rem_extra']} 人", ln=True)
    pdf.cell(200, 10, txt=f"承接：目前 {data['b6']} 人 / 剩餘 {data['rem_b6']} 人", ln=True)
    pdf.cell(200, 10, txt=f"加薪：目前 {data['b7']} 人 / 剩餘 {data['rem_b7']} 人", ln=True)
    pdf.cell(200, 10, txt=f"技術人力：目前 {data['tech']} 人 / 剩餘 {data['rem_tech']} 人", ln=True)
    
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"全廠總人數 (含本國+外國人)：{data['all_deno']} 人", ln=True)
    
    return pdf.output()
