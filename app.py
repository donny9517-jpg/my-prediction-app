import streamlit as st
import pandas as pd

# 1. 網頁基礎設定 (手機版優先佈局)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 移除所有導致白畫面的複雜 CSS，只保留最基本的樣式優化
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    /* 強制字體喺手機任何模式都顯示深色 */
    .stMarkdown, .stMetric, h1, h2, h3 { color: #1a1a1a !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與【強化警示功能】 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數據並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 【強化版：勝率回測與警報系統】
    if len(st.session_state.history) >= 10:
        win_count = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_count * 10
        st.write(f"📈 中軸命中率 (近10手): **{win_rate}%**")
        
        # 30% 或以下預告警示
        if win_rate >= 70:
            st.success("🔥 規律極強：建議重注")
        elif win_rate <= 20:
            st.error("🚨 緊急：命中極低，暫停出手！")
        elif win_rate <= 40:
            st.warning("⚠️ 預警：盤勢混亂 (命中40%或以下)")
            
        # 變盤預警 (連續單雙)
        last_5 = st.session_state.history[-5:]
        if all(x % 2 != 0 for x in last_5): st.error("🚨 變盤：連續 5 手單號")
        elif all(x % 2 == 0 for x in last_5): st.error("🚨 變盤：連續 5 手雙號")
    else:
        st.info("請輸入 10 手數據後顯示命中分析")

    st.divider()
    if st.button("清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯函數 ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # 基礎物理概率
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 矩陣連動加成
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 鄰居震盪與熱度衰減
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主畫面顯示 (優化手機排列) ---
if st.session_state.history:
    df_res = analyze_data(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc[0]['評分']
    
    # 手機版改用垂直卡片排列，確保唔會「隱形」
    st.divider()
    
    st.metric("🎯 重點布局", f"{int(best_num)}")
    
    # 三級注碼建議
    if conf_score > 65:
        st.error("💰 注碼建議：💥 強烈重注")
    elif conf_score > 55:
        st.success("💰 注碼建議：🏹 穩健布局")
    else:
        st.info("💰 注碼建議：🛡️ 試探輕注")
        
    trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
    st.warning(f"📈 目前盤勢：{trend}")
    
    st.divider()

    # 能量分佈圖
    st.bar_chart(df_res.set_index("數字")["評分"])
    
    # 滾動紀錄
    st.write("### 📜 最近 100 手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    df_hist = pd.DataFrame({"號碼": hist_data})
    st.dataframe(df_hist, use_container_width=True, height=300)
else:
    st.info("👈 手機版請點擊左上角『 > 』箭頭打開選單輸入數據")
