import streamlit as st
import pandas as pd

# 1. 網頁基礎設定 (優化手機窄螢幕)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 強制修正顯示：確保文字在任何模式下都清晰，並美化指標卡
st.markdown("""
    <style>
    h1, h2, h3, p, span, label { color: #1f1f1f !important; }
    .stMetric { background-color: #f8f9fb !important; padding: 15px; border-radius: 12px; border: 1px solid #eaedf2; }
    [data-testid="stMetricValue"] { color: #d33682 !important; font-size: 32px !important; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：數據管理 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出號碼", 2, 12, 7)
    if st.button("提交數字並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 命中率與警示
    if len(st.session_state.history) >= 10:
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_c * 10
        st.write(f"📈 中軸命中率 (近10手): **{win_rate}%**")
        if win_rate <= 30:
            st.error("⚠️ 預警：命中率低於 30%！盤勢極亂。")
    
    if st.button("🗑️ 清空所有歷史數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 (保持原始 9 號設定) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # 物理機率
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        
        # 原始連動矩陣
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        
        # 鄰居與過熱修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22 
        
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面佈局 ---
if st.session_state.history:
    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 頂部預測：熱門 Top 3
    top_3 = df_res.head(3)
    top_list = top_3['數字'].astype(int).tolist()
    
    st.subheader("🏆 熱門推薦 (置頂)")
    col1, col2, col3 = st.columns(3)
    col1.metric("首選", top_list[0])
    col2.metric("次選", top_list[1])
    col3.metric("防守", top_list[2])
    
    # ❄️ 新增：冷門避雷 (評分最低的兩個數字)
    bottom_2 = df_res.tail(2)['數字'].astype(int).tolist()
    st.markdown(f"**❄️ 冷門/避雷：** `{bottom_2[0]}` , `{bottom_2[1]}` (目前評分墊底)")
    
    st.divider()

    # 注碼與盤勢看板
    best_score = df_res.iloc[0]['評分']
    c_a, c_b = st.columns(2)
    
    with c_a:
        if best_score > 65: st.error("💰 注碼：💥 強烈重注")
        elif best_score > 55: st.success("💰 注碼：🏹 穩健布局")
        else: st.info("💰 注碼：🛡️ 試探輕注")
    
    with c_b:
        trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
        st.warning(f"📈 盤勢：{trend}")

    # 能量分布圖 (橫軸固定 2-12)
    st.write("📊 **能量分布圖**")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
    
    # 100 手紀錄
    with st.expander("📜 查看最近 100 手詳細紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.warning("👈 請點擊左上角 [ > ] 符號展開選單輸入數據")
    st.info("數據暫存於瀏覽器，刷新頁面會清空。")
