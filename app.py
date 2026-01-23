import streamlit as st
import pandas as pd

# 1. 網頁基礎設定與黑金模式 CSS
st.set_page_config(page_title="PRO 數據分析終端", layout="wide")

st.markdown("""
    <style>
    /* 全域深色背景 */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* 看板數字樣式與顏色 */
    [data-testid="stMetricValue"] { font-size: 52px !important; font-weight: 800 !important; }
    
    /* 第一格：重點布局 - 螢光金 */
    [data-testid="column"]:nth-of-type(1) [data-testid="stMetricValue"] { color: #FFD700 !important; text-shadow: 2px 2px 4px #000; }
    
    /* 第二格：注碼建議 - 鮮紅色 */
    [data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] { color: #FF3131 !important; text-shadow: 2px 2px 4px #000; }
    
    /* 第三格：目前盤勢 - 亮藍色 */
    [data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] { color: #00E5FF !important; text-shadow: 2px 2px 4px #000; }
    
    /* 表格與滾動條樣式 */
    .stDataFrame { border: 1px solid #30363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與統計 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 近期勝率統計 (近10手參考)
    if len(st.session_state.history) >= 10:
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        st.metric("📊 近 10 手中軸命中率", f"{win_c * 10}%")
    
    if st.button("🗑️ 清空數據"):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯：Excel 超級公式轉化 ---
def analyze(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # 物理基礎分
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 矩陣連動
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 鄰居與熱度補償
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 20
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主畫面看板 ---
if st.session_state.history:
    df_res = analyze(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc
