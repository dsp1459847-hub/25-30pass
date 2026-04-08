import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. एंटी-पैटर्न इंजन (Anti-Pattern Logic) ---
def get_anti_logic(df, s_name, target_date):
    try:
        # डेटा क्लीनिंग (B=Index 1, s_name=Shift)
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 10:
            return "Data Kam", "N/A"

        # A. ताज़ा चाल (Current Neighbor)
        recent_all = df_clean[df_clean['DATE'] < target_date].tail(5)['NUM'].astype(int).tolist()
        if not recent_all: return "No Data", "N/A"
        
        last_val = recent_all[-1]
        
        # B. 'काट' और 'पड़ोसी' (Neighbor & Cutting)
        # पिछले अंक का अगला (+1) और पिछला (-1)
        n_plus = (last_val + 1) % 100
        n_minus = (last_val - 1) % 100
        
        # C. विपरीत हरुफ़ (Opposite Haruf)
        # अगर 42 आया है, तो 4 की राशि 9 और 2 की राशि 7 (97)
        opp_val = ((last_val // 10 + 5) % 10 * 10) + (last_val % 10 + 5) % 10

        analysis = f"🎯 पिछला अंक: {last_val:02d} | 📈 पड़ोसी: {n_plus:02d} | 🔀 विपरीत: {opp_val:02d}"
        
        # --- टॉप 3 'एंटी-फेल' अंक ---
        p1 = f"{opp_val:02d}" # विपरीत (Mirror Family)
        p2 = f"{n_plus:02d}"  # अगला पड़ोसी
        p3 = f"{n_minus:02d}" # पिछला पड़ोसी
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Analyzing..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Anti-Fail", layout="wide")
st.title("🛡️ MAYA AI: Anti-Pattern & Neighbor Logic")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v19_antifail")

if uploaded_file:
    try:
        data_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(data_bytes), engine='openpyxl')
        
        # तारीख मिलान (B Column)
        df_match = df.copy()
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]
        target_date = st.date_input("📅 तारीख चुनें (आज 8 अप्रैल):", datetime.date.today())

        if st.button("🚀 एंटी-फेल स्कैन शुरू करें"):
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_anti_logic(df_match, s, target_date)
                
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
                    "🗓️ विपरीत चाल (Neighbor)": logic_info,
                    "🌟 टॉप 3 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            st.info("💡 **क्यों फेल हो रहा है?** जब गेम रैंडम हो, तो वह 'हॉट' नंबरों के बजाय 'पड़ोसी' (+1/-1) या 'विपरीत' (Mirror) अंकों को पकड़ता है। यह कोड उन्हीं को फिल्टर करता है।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
