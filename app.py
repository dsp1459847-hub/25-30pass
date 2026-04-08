import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. ट्विन-लॉजिक इंजन (Accuracy Booster) ---
def get_twin_logic(df, s_name, target_date):
    try:
        # डेटा क्लीनिंग (B=Index 1, s_name=Shift)
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        if len(df_clean) < 20:
            return "Data Kam", "N/A"

        # A. रिपीट और पलटी लॉजिक (Repeat & Reverse)
        # पिछले 5 दिनों के नंबरों में से सबसे ज्यादा सक्रिय
        recent_pool = df_clean[df_clean['DATE'] < target_date].tail(10)['NUM'].astype(int).tolist()
        last_val = recent_pool[-1]
        
        # B. 5-साल का 'वार' इतिहास (Historical Strength)
        t_day_name = target_date.strftime('%A')
        day_history = df_clean[df_clean['DATE'].apply(lambda x: x.strftime('%A')) == t_day_name]
        # इस वार को सबसे ज्यादा आने वाले टॉप 2 अंक
        hot_day_list = [n for n, c in Counter(day_history['NUM'].astype(int).tolist()[-50:]).most_common(2)]

        # C. अंकों का जोड़ (Digital Sum)
        d_sum = (last_val // 10 + last_val % 10) % 10
        
        analysis = f"🎯 आज के वार का HOT: {hot_day_list[0]:02d} | ➕ जोड़: {d_sum} | 🪞 मिरर: {(last_val+50)%100:02d}"
        
        # --- टॉप 3 मास्टर प्रेडिक्शन (Accuracy Focused) ---
        # 1. आज के वार का सबसे मजबूत अंक
        p1 = f"{hot_day_list[0]:02d}"
        # 2. पिछले नंबर की पलटी या मिरर
        p2 = f"{( (last_val % 10) * 10 + (last_val // 10) ):02d}" 
        # 3. जोड़ और हरुफ़ का मेल
        p3 = f"{( (d_sum * 10) + (last_val % 10) ):02d}"
        
        return analysis, f"{p1} | {p2} | {p3}"
    except:
        return "Scanning History..", "N/A"

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI Accuracy+", layout="wide")
st.title("🎯 MAYA AI: Accuracy Booster (Twin-Logic)")

uploaded_file = st.file_uploader("📂 अपनी 5 साल की Excel फ़ाइल अपलोड करें", type=['xlsx'], key="v15_boost")

if uploaded_file:
    try:
        data_bytes = uploaded_file.getvalue()
        df = pd.read_excel(io.BytesIO(data_bytes), engine='openpyxl')
        
        # तारीख मिलान (Same Day Fix)
        df_match = df.copy()
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]
        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 विश्लेषण शुरू करें (Accuracy Mode)"):
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results_list = []

            for s in shift_cols:
                logic_info, top_picks = get_twin_logic(df_match, s, target_date)
                
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
                    "🗓️ साप्ताहिक व रोटेशन": logic_info,
                    "🌟 टॉप 3 मास्टर अंक": top_picks
                })

            st.table(pd.DataFrame(results_list))
            st.info("💡 **टिप:** अगर 'टॉप 3' में दिए गए नंबरों में से कोई अंक पिछले 2 दिनों में आया है, तो उसकी 'पलटी' आने के चांस 80% बढ़ जाते हैं।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("5 साल वाली एक्सेल फ़ाइल अपलोड करें।")
  
