import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. नेबर और सम इंजन (Neighbor & Sum Logic) ---
def get_neighbor_logic(df, s_name, target_date):
    try:
        # डेटा क्लीनिंग
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 10:
            return "Data Kam", "N/A"

        # A. पिछले 24 घंटे की ताज़ा चाल
        recent_all = df_clean[df_clean['DATE'] < target_date].tail(5)['NUM'].astype(int).tolist()
        if not recent_all: return "No Data", "N/A"
        
        last_val = recent_all[-1]
        
        # B. नेबर लॉजिक (Neighbor Logic: +1, -1)
        # अक्सर नंबर पिछले अंक के ठीक आगे या पीछे का आता है
        n1 = (last_val + 1) % 100
        n2 = (last_val - 1) % 100
        
        # C. जोड़ (Digital Sum) का रोटेशन
        d_sum = (last_val // 10 + last_val % 10) % 10
        # जोड़ के साथ बाहर का हरुफ़ जोड़ना
        sum_pick = (d_sum * 10) + (last_val % 10)

        # D. राशि/मिरर (Mirror)
        mirror = (last_val + 50) % 100

        analysis = f"🎯 पिछला अंक: {last_val:02d} | ➕ जोड़ चाल: {d_sum} | 🪞 मिरर: {mirror:02d}"
        
        # --- टॉप 3 मास्टर प्रेडिक्शन (Neighbor Focus) ---
        p1 = f"{mirror:02d}"  # राशि सबसे पहले
        p2 = f"{n1:02d}"      # पड़ोसी अंक (+1)
        p3 = f"{sum_pick:02d}" # जोड़ की चाल
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Analyzing Pulse..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Neighbor", layout="wide")
st.title("🛡️ MAYA AI: Neighbor & Sum Tracker")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v16_neighbor")

if uploaded_file:
    try:
        data_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(data_bytes), engine='openpyxl')
        
        # तारीख मिलान
        df_match = df.copy()
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]
        target_date = st.date_input("📅 तारीख चुनें (8 अप्रैल 2026):", datetime.date.today())

        if st.button("🚀 नेबर स्कैन शुरू करें"):
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_neighbor_logic(df_match, s, target_date)
                
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
                    "🗓️ ताज़ा चाल (Neighbor)": logic_info,
                    "🌟 टॉप 3 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            st.info("💡 **टिप:** जब गेम 100% फेल हो रहा हो, तो नंबर अक्सर पिछले अंक के बिल्कुल बगल वाला (+1/-1) या उसकी राशि (Mirror) में आता है।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("एक्सेल फ़ाइल अपलोड करें।")
    
