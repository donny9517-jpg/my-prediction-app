import streamlit as st
import pandas as pd

# 1. 網頁設定
st.set_page_config(page_title="PRO 數據分析預測終端", layout="wide")
st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與【簡單勝率回測】 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數據", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 【勝率回測邏輯】
    st.subheader("📈 勝率回測 (近10手)")
    if len(st.session_state.history) >= 10:
        # 計算最近 10 手中有幾多手開出 6, 7, 8 (中軸)
        win_count = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_count * 10
        st.metric("中軸命中率", f"{win_rate}%")
        
        if win_rate >= 70:
            st.success("🔥 目前處於規律期")
        elif win_rate <= 30:
            st.error("⚠️ 目前處於亂序期")
    else:
        st.info("需輸入至少 10 手數據以顯示回測")

    st.divider()
    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯函數 ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # 1. 基礎物理分
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 2. 矩陣連動加成
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 3. 鄰居與過熱修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主畫面顯示 ---
if st.session_state.history:
    # 執行分析
    df_res = analyze_data(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc[0]['評分']
    
    # 頂部三大看板
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🎯 **重點布局**")
        st.header(f"{int(best_num)}")
    with col2:
        st.success("💰 **注碼建議**")
        status = "🔥 重注" if conf_score > 58 else "⚖️ 輕注"
        st.header(status)
    with col3:
        st.warning("📈 **目前盤勢**")
        trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
        st.header(trend)

    # 能量分佈圖
    st.bar_chart(df_res.set_index("數字")["評分"])
    
    # 滾動式 100 手紀錄
    st.write("### 📜 最近 100 手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    df_hist = pd.DataFrame({
        "期序": range(len(st.session_state.history), len(st.session_state.history) - len(hist_data), -1),
        "號碼": hist_data
    })
    st.dataframe(df_hist, use_container_width=True, height=350, hide_index=True)
else:
    st.info("👈 請在左側輸入最新數字開始分析。")
