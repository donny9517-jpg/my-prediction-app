import streamlit as st
import pandas as pd
import numpy as np

# 1. 基礎設定
st.set_page_config(page_title="PRO 終端", layout="centered")
st.title("📊 PRO 專業數據終端 (全能版)")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 🔍 自動修正數據格式 (防止 TypeError) ---
clean_h = []
for i in st.session_state.history:
    if isinstance(i, tuple): clean_h.append(i)
    else: clean_h.append((i, False))
st.session_state.history = clean_h

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("號碼", 2, 12, 7)
    is_d = st.checkbox("⚠️ 對子 (如 3-3)")
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append((val, is_d))
        st.rerun()
    st.divider()
    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (極簡加固版) ---
def analyze_data(history):
    if not history: return None, 1.0
    last_v, last_d = history[-1]
    h_vals = [x[0] for x in history]
    res = []
    p_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    risk = 1.0
    if len(h_vals) >= 5 and np.std(h_vals[-5:]) > 2.5: risk = 0.6
    
    for e in range(2, 13):
        s = (p_map[e] / 36) * 100
        if e == 7: s += 5.0
        if last_v in [6,7,8] and e in [6,7,8]: s += 18.0
        if last_v in [4,8,10] and e in [4,8,10]: s += 14.0
        if last_d:
            if e in [2,3,11,12]: s += 12.0
            if e == last_v: s += 15.0
        try:
            o = h_vals[::-1].index(e)
            s += min(o * 0.5, 10.0)
        except: s += 10.0
        res.append({"數字": e, "評分": round(s * risk, 2)})
    return pd.DataFrame(res), risk

# --- 主畫面顯示 (圖表與紀錄) ---
if st.session_state.history:
    df, cur_risk = analyze_data(st.session_state.history)
    df_res = df.sort_values("評分", ascending=False)
    
    t3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測")
    c1, c2, c3 = st.columns(3)
    c1.metric("首選", t3[0]); c2.metric("輔助", t3[1]); c3.metric("防守", t3[2])

    best_s = df_res.iloc[0]['評分']
    p = 0.35 + (best_s / 100.0) * 0.25
    kf = (1.0 * p - (1.0 - p)) / 1.0
    st.metric("💰 建議注碼", f"${int(1000 * max(0, kf) * 0.5)}")

    st.divider()
    st.bar_chart(df.sort_values("數字").set_index("數字")["評分"])
    
    with st.expander("📜 歷史紀錄"):
        st.write([f"{x[0]} {'(對
