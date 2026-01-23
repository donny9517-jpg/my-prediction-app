import streamlit as st
import pandas as pd

# 1. 網頁基礎設定與 App 化樣式優化
st.set_page_config(page_title="PRO 數據分析預測終端", layout="wide")

# CSS 注入：隱藏頂部選單、App 化介面、確保文字清晰
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #ffffff; }
    
    /* 強制指標大字顯示 */
    .main-metric {
        font-size: 40px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入、命中率與【變盤預警】 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數據並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 【變盤預警邏輯】
    if len(st.session_state.history) >= 5:
        last_5 = st.session_state.history[-5:]
        all_odd = all(x % 2 != 0 for x in last_5)
        all_even = all(x % 2 == 0 for x in last_5)
        if all_odd:
            st.error("⚠️ 變盤預警：連續 5 手單號！")
        elif all_even:
            st.error("⚠️ 變盤預警：連續 5 手雙號！")
    
    # 【勝率回測】
    st.subheader("📈 勝率回測 (近10手)")
    if len(st.session_state.history) >= 10:
        win_count = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_count * 10
        st.metric("中軸命中率", f"{win_rate}%")
        if win_rate >= 70: st.success("🔥 目前規律極強")
    else:
        st.info("請輸入 10 手數據計算勝率")

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
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 矩陣連動
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 鄰居與熱度修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_res = analyze_data(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc[0]['評分']
    
    # 三大看板
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("🎯 **重點布局**")
        st.info(f"### {int(best_num)}")
        
    with col2:
        st.markdown("💰 **注碼建議**")
        # 【三級注碼梯度優化】
        if conf_score > 65:
            st.error(f"### 💥 強烈重注")
        elif conf_score > 55:
            st.success(f"### 🏹 穩健布局")
        else:
            st.info(f"### 🛡️ 試探輕注")
        
    with col3:
        st.markdown("📈 **目前盤勢**")
        trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
        st.warning(f"### {trend}")

    # 能量分佈圖
    st.bar_chart(df_res.set_index("數字")["評分"])
    
    # 紀錄表
    st.write("### 📜 最近 100 手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    df_hist = pd.DataFrame({
        "期序": range(len(st.session_state.history), len(st.session_state.history) - len(hist_data), -1),
        "號碼": hist_data
    })
    st.dataframe(df_hist, use_container_width=True, height=350, hide_index=True)
else:
    st.info("👈 終端已就緒，請開始輸入數據。")
