import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁設定：優化 App 質感
st.set_page_config(page_title="PRO 數據分析", layout="centered")

st.markdown("""
    <style>
    /* 隱影頂部導航，增加 App 感 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    /* 讓按鈕在手機上更好按 */
    .stButton>button { width: 100%; height: 3.5em; border-radius: 12px; font-weight: bold; margin-top: 10px; }
    /* 卡片美化 */
    .stMetric { background-color: #f8f9fb !important; padding: 15px; border-radius: 15px; border: 1px solid #eaedf2; }
    h1, h2, h3 { color: #2c3e50 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：進階監控 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出號碼", 2, 12, 7)
    if st.button("提交數字並更新"):
        st.session_state.history.append(val)
    
    st.divider()
    
    if len(st.session_state.history) >= 10:
        # A. 命中率
        last_10 = st.session_state.history[-10:]
        win_c = sum(1 for x in last_10 if x in [6, 7, 8])
        st.metric("📈 中軸命中率", f"{win_c * 10}%")
        
        # B. 偏離度監控 (新增功能)
        avg_val = sum(last_10) / 10
        bias = abs(avg_val - 7)
        if bias > 1.5:
            st.warning(f"⚠️ 偏離警戒：目前重心偏向 {'大' if avg_val > 7 else '小'}號區")
            
        if (win_c * 10) <= 30:
            st.error("🚨 警告：命中率極低，請暫停觀望")
    
    if st.button("🗑️ 清空所有數據"):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (維持原始設定) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3:
            score -= 22 
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面佈局 ---
if st.session_state.history:
    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 核心推薦
    top_3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 熱門推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("首選", top_3[0])
    c2.metric("次選", top_3[1])
    c3.metric("防守", top_3[2])
    
    # ❄️ 冷門避雷
    bot_2 = df_res.tail(2)['數字'].astype(int).tolist()
    st.info(f"❄️ 冷門避雷（勿追）：**{bot_2[0]}** , **{bot_2[1]}**")
    
    st.divider()

    # 📊 趨勢圖
    st.write("📊 **能量分布圖**")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
    
    # 盤勢分析
    best_s = df_res.iloc[0]['評分']
    col_a, col_b = st.columns(2)
    with col_a:
        if best_s > 65: st.error("💰 注碼：💥 強烈重注")
        elif best_s > 55: st.success("💰 注碼：🏹 穩健布局")
        else: st.info("💰 注碼：🛡️ 試探輕注")
    with col_b:
        trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
        st.warning(f"📈 盤勢：{trend}")

    with st.expander("📜 最近 100 手詳細紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 **歡迎使用 PRO 終端**")
    st.write("請展開左側選單輸入號碼開始分析。")
