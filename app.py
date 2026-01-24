import streamlit as st
import pandas as pd

# 1. 網頁基礎設定 (優化手機窄螢幕)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 強制修正顯示問題：確保文字在任何模式下都清晰
st.markdown("""
    <style>
    h1, h2, h3, p, span, label { color: #1f1f1f !important; }
    .stMetric { background-color: #f0f2f6 !important; padding: 10px; border-radius: 8px; border: 1px solid #d1d5db; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化歷史數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與警示 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數據並更新", use_container_width=True):
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

# --- 核心運算邏輯 (包含 9 號優化) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # 基礎分
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 矩陣連動 (納入 9 號)
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [8,9,10,11] and e in [8,9,10,11]: score += 15
        if last in [5,7,9,11] and e in [5,7,9,11]: score += 12
        # 鄰居與過熱修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22 
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_res = analyze_data(st.session_state.history)
    
    # 🏆 視覺置頂：熱門推薦 Top 3
    top_3 = df_res.head(3)
    top_3_list = top_3['數字'].astype(int).tolist()
    
    st.subheader("🔥 核心推薦 (置頂)")
    c1, c2, c3 = st.columns(3)
    with c1: st.success(f"首選: {top_3_list[0]}")
    with c2: st.info(f"次選: {top_3_list[1]}")
    with c3: st.warning(f"防守: {top_3_list[2]}")
    
    # ❄️ 冷門提醒
    bottom_nums = df_res.sort_values("評分").head(2)['數字'].tolist()
    st.markdown(f"**❄️ 冷門避雷：** `{int(bottom_nums[0])}` , `{int(bottom_nums[1])}`")
    st.divider()

    # 注碼建議
    best_score = df_res.iloc[0]['評分']
    if best_score > 65: st.error("💰 注碼建議：💥 強烈重注")
    elif best_score > 55: st.success("💰 注碼建議：🏹 穩健布局")
    else: st.info("💰 注碼建議：🛡️ 試探輕注")

    # 能量分佈圖 (顯示號碼順序)
    st.write("📊 **能量分布圖**")
    st.bar_chart(df_res.sort_values("數字").set_index("數字")["評分"])
    
    # 100 手紀錄
    with st.expander("📜 查看最近 100 手紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👈 請點擊左上角 [ > ] 展開選單輸入數據")
