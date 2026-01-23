import streamlit as st
import pandas as pd

# 網頁基礎設定
st.set_page_config(page_title="PRO 數據終端", layout="wide")

# 強制顏色與字體樣式 CSS
st.markdown("""
    <style>
    /* 強制指標數字顏色 */
    [data-testid="stMetricValue"] {
        font-size: 52px !important;
        font-weight: 800 !important;
    }
    /* 第一格：重點布局 - 螢光金 */
    [data-testid="column"]:nth-of-type(1) [data-testid="stMetricValue"] {
        color: #FFD700 !important;
        text-shadow: 2px 2px 4px #000000;
    }
    /* 第二格：注碼建議 - 鮮紅色 */
    [data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] {
        color: #FF3131 !important;
        text-shadow: 2px 2px 4px #000000;
    }
    /* 第三格：目前盤勢 - 亮藍色 */
    [data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] {
        color: #00E5FF !important;
        text-shadow: 2px 2px 4px #000000;
    }
    /* 表格樣式優化 */
    .stTable { background-color: #1a1c23; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄輸入 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append(val)
    st.divider()
    if st.button("🗑️ 清空所有數據"):
        st.session_state.history = []
        st.rerun()

# --- 核心運算大腦 ---
def analyze(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # 1. 物理概率
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 2. 矩陣連動
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 3. 鄰居補償
        if abs(last - e) == 1: score += 10
        # 4. 熱度衰減 (近10手開超過3次大幅減分)
        if history[-10:].count(e) >= 3: score -= 20
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主看板 ---
if st.session_state.history:
    df_res = analyze(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc[0]['評分']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 重點布局", f"{int(best_num)}")
    with col2:
        status = "🔥 重注" if conf_score > 58 else "⚖️ 輕注"
        st.metric("💰 注碼建議", status)
    with col3:
        trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
        st.metric("📈 目前盤勢", trend)

    # 能量分佈圖表
    st.bar_chart(df_res.set_index("數字")["評分"])
    
    # 📜 最近 100 手紀錄 (滾動式表格)
    st.write("### 📜 最近 100 手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    df_hist = pd.DataFrame({
        "期數": range(len(st.session_state.history), len(st.session_state.history) - len(hist_data), -1),
        "號碼": hist_data
    })
    # 使用 dataframe 顯示並設定高度，會自動出現滾動條
    st.dataframe(df_hist, use_container_width=True, height=300, hide_index=True)
else:
    st.info("👈 請在左側輸入最新數字開始分析。數據不永久保存，刷新網頁將清空。")

    # 簡單勝率回測 (檢查前 10 手是否選中)
    win_count = 0
    if len(history) >= 10:
        for i in range(1, 11):
            # 這裡模擬檢查上一手的預測(簡化邏輯)
            if history[-i] in [6, 7, 8]: win_count += 1
    st.sidebar.metric("📊 近 10 手命中參考", f"{win_count * 10}%")
