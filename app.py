import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. डेड ज़ोन इंजन (Missing Digit Logic) ---
def get_dead_zone_logic(df, s_name, target_date):
    try:
        # डेटा क्लीनिंग
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 15:
            return "Data Kam", "N/A"

        # A. गायब अंकों की पहचान (Missing Digits)
        # पिछले 10 दिनों में जो नंबर बिल्कुल नहीं आए
        recent_10 = df_clean[df_clean['DATE'] < target_date].tail(10)['NUM'].astype(int).tolist()
        
        # B. हरुफ़ फ्रीक्वेंसी (Haruf Frequency)
        all_andar = [n // 10 for n in recent_10]
        all_bahar = [n % 10 for n in recent_10]
        
        # वे हरुफ़ जो पिछले 3 दिनों से 'गायब' (Missing) हैं
        missing_andar = [d for d in range(10) if d not in all_andar[-3:]]
        missing_bahar = [d for d in range(10) if d not in all_bahar[-3:]]
        
        # C. नेबर राशि (Neighbor Mirror)
        last_val = recent_10[-1]
        mirror = (last_val + 50) % 100

        analysis = f"🎯 गायब अंदर: {missing_andar[:2]} | 🎯 गायब बाहर: {missing_bahar[:2]} | 🪞 मिरर: {mirror:02d}"
        
        # --- टॉप 3 अनछुए अंक (Dead Zone Picks) ---
        # 1. गायब अंदर + गायब बाहर का मेल
        p1 = f"{(missing_andar[0] * 10) + missing_bahar[0]:02d}" if missing_andar and missing_bahar else "00"
        # 2. पिछले अंक का मिरर (राशि)
        p2 = f"{mirror:02d}"
        # 3. पिछले अंक की 'पलटी' + 1 (Next Pulse)
        p3 = f"{( (last_val % 10) * 10 + (last_val // 10) + 1 ) % 100:02d}"
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Scanning Dead Zone..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI DeadZone", layout="wide")
st.title("🚫 MAYA AI: Dead Zone & Missing Digit")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v17_deadzone")

if uploaded_file:
    try:
        data_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(data_bytes), engine='openpyxl')
        
        # तारीख मिलान (B Column)
        df_match = df.copy()
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]
        target_date = st.date_input("📅 तारीख चुनें (8 अप्रैल 2026):", datetime.date.today())

        if st.button("🚀 डेड-ज़ोन स्कैन शुरू करें"):
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_dead_zone_logic(df_match, s, target_date)
                
                # SAME DAY RESULT
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
                    "🗓️ गायब अंक विश्लेषण": logic_info,
                    "🌟 टॉप 3 अनछुए अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            st.info("💡 **डेड ज़ोन क्या है?** जब गेम फेल होता है, तो वह उन अंकों को पकड़ता है जो पिछले 3-4 दिनों से बिल्कुल नहीं आए। यह कोड उन्हीं 'गायब' अंकों को ढूँढता है।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
