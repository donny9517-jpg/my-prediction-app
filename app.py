import streamlit as st
import pandas as pd

# 1. 網頁基礎設定 (針對手機螢幕優化)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 強制修正顯示問題：確保文字在任何模式下都清晰
st.markdown("""
    <style>
    h1, h2, h3, p, span, label { color: #1f1f1f !important; }
    .stMetric { background-color: #f8f9fb !important; padding: 15px; border-radius: 12px; border: 1px solid #eaedf2; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：數據輸入 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字並更新預測", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 命中率與 30% 預告警示
    if len(st.session_state.history) >= 10:
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_c * 10
        st.write(f"📈 中軸命中率: **{win_rate}%**")
        if win_rate <= 30:
            st.error("⚠️ 預警：命中率低於30%！")
    
    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 (回復原始設定) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # A. 物理基礎分
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        
        # B. 原始矩陣連動
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        
        # C. 鄰居與過熱修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3:
            score -= 22 
        
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 置頂：熱門推薦 Top 3
    top_3 = df_res.head(3)
