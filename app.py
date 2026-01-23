import streamlit as st
import pandas as pd

# 1. 網頁設定與 App 化樣式
st.set_page_config(page_title="PRO 數據分析預測終端", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入、命中率與【強化版變盤預警】 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數據並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 【強化版勝率與警示邏輯】
    st.subheader("📈 勝率回測 (近10手)")
    if len(st.session_state.history) >= 10:
        win_count = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_count * 10
        st.metric("中軸命中率", f"{win_rate}%")
        
        # 顯示警示訊息
        if win_rate >= 70:
            st.success("🔥 目前規律極強，建議重注")
        elif win_rate <= 20:
            st.error("🚨 緊急預警：命中極低，建議停止！")
        elif win_rate <= 40:
            st.warning("⚠️ 預警：盤勢極度混亂 (30%-40%)")
            
        # 偵測單雙跳位變盤
        last_5 = st.session_state.history[-5:]
        if all(x % 2 != 0 for x in last_5): st.error("⚠️ 警告：連續 5 手單號！")
        elif all(x % 2 == 0 for x in last_5): st.error("⚠️ 警告：連續 5 手雙號！")
    else:
        st.info("請輸入 10 手數據計算勝率")

    st.divider()
    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯函數 ---
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
        if history[-10:].count(e) >= 3: score -= 22
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_res = analyze_data(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc[0]['評分']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🎯 **重點布局**")
        st.header(f"{int(best_num)}")
    with col2:
        st.success("💰 **注碼建議**")
        if conf_score > 65: st.error("### 💥 強烈重注")
        elif conf_score > 55: st.success("### 🏹 穩健布局")
        else: st.info("### 🛡️ 試探輕注")
    with col3:
        st.warning("📈 **目前盤勢**")
        trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
        st.header(trend)

    st.bar_chart(df_res.set_index("數字")["評分"])
    
    st.write("### 📜 最近 100 手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    df_hist = pd.DataFrame({
        "期序": range(len(st.session_state.history), len(st.session_state.history) - len(hist_data), -1),
        "號碼": hist_data
    })
    st.dataframe(df_hist, use_container_width=True, height=350, hide_index=True)
