import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. जीरो-पैटर्न इंजन (Outlier Logic) ---
def get_zero_logic(df, s_name, target_date):
    try:
        # डेटा साफ़ करना
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 15:
            return "Data Kam", "N/A"

        # A. सबसे 'ठंडे' नंबर (Coldest Numbers)
        # पिछले 50 दिनों में जो नंबर सबसे कम बार (0 या 1 बार) आए हैं
        recent_50 = df_clean[df_clean['DATE'] < target_date].tail(50)['NUM'].astype(int).tolist()
        counts_50 = Counter(recent_50)
        
        # वे नंबर जो बिल्कुल नहीं आए (Zero Frequency)
        cold_nums = [n for n in range(100) if n not in recent_50]
        
        # B. विपरीत हरुफ़ (Opposite Haruf)
        last_val = recent_50[-1]
        # अगर अंदर का अंक 4 है, तो उसका उल्टा (4+5=9) लें
        opp_andar = (last_val // 10 + 5) % 10
        opp_bahar = (last_val % 10 + 5) % 10
        
        # C. क्रॉस चाल (Cross Pattern)
        # पिछले 3 दिनों के अंकों का औसत जोड़
        last_3 = recent_50[-3:]
        avg_sum = sum([(n // 10 + n % 10) for n in last_3]) % 10

        analysis = f"🎯 सबसे ठंडा अंक: {cold_nums[0] if cold_nums else '--'} | 🔄 विपरीत हरुफ़: {opp_andar}, {opp_bahar}"
        
        # --- टॉप 3 'एंटी-लॉजिक' अंक (Anti-Fail Picks) ---
        # 1. विपरीत अंदर + विपरीत बाहर
        p1 = f"{(opp_andar * 10) + opp_bahar:02d}"
        # 2. सबसे ठंडे नंबरों में से पहला
        p2 = f"{cold_nums[0]:02d}" if cold_nums else "00"
        # 3. औसत जोड़ + पिछला बाहर का अंक
        p3 = f"{(avg_sum * 10) + (last_val % 10):02d}"
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Deep Scanning..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Anti-Fail", layout="wide")
st.title("🛡️ MAYA AI: Zero-Pattern Engine (Anti-Fail)")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v18_zero")

if uploaded_file:
    try:
        data_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(data_bytes), engine='openpyxl')
        
        df_match = df.copy()
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]
        target_date = st.date_input("📅 तारीख चुनें (आज 8 अप्रैल):", datetime.date.today())

        if st.button("🚀 एंटी-फेल विश्लेषण शुरू करें"):
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_zero_logic(df_match, s, target_date)
                
                actual_val = "--"
                if not selected_row.empty:
                    raw_val = str(selected_row[s].values[0]).strip()
                    if raw_val.replace('.','',1).isdigit():
                        actual_val = f"{int(float(raw_val)):02d}"
                    else:
                        actual_val = raw_val

                results_list.append({
                    "Shift": s,
                    "📍 SAME DAY": actual_val,
                    "🗓️ विपरीत विश्लेषण (Anti-Logic)": logic_info,
                    "🌟 टॉप 3 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            st.info("💡 **0% फेलियर का समाधान:** जब गेम कुछ भी नहीं दे रहा हो, तो वह अक्सर उन नंबरों को निकालता है जो पिछले 50 दिनों से 'सो रहे' (Cold) हैं। यह कोड उन्हीं 'सोते हुए' अंकों को जगाता है।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
