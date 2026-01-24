import streamlit as st
import pandas as pd

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    if len(st.session_state.history) >= 10:
        # 命中率計算
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_c * 10
        st.write(f"📈 中軸命中率: **{win_rate}%**")
        if win_rate <= 30:
            st.error("⚠️ 命中率低於30%！")
    
    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # 物理基礎分
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 矩陣加分
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 鄰居與過熱修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22 
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # Top 3 推薦
    top_3 = df_res.head(3)
    top_list = top_3['數字'].astype(int).tolist()
    
    st.subheader("🏆 熱門推薦")
    st.success(f"首選: {top_list[0]} | 次選: {top_list[1]} | 防守: {top_list[2]}")
    
    # 冷門避雷
    bot_2 = df_res.tail(2)['數字'].astype(int).tolist()
    st.write(f"❄️ 冷門避雷: {bot_2[0]}, {bot_2[1]}")
    
    st.divider()

    # 注碼建議
    best_s = df_res.iloc[0]['評分']
    if best_s > 65: st.error("💰 注碼：💥 強烈重注")
    elif best_s > 55: st.success("💰 注碼：🏹 穩健布局")
    else: st.info("💰 注碼：🛡️ 試探輕注")

    # 圖表 (最簡化版本)
    st.write("📊 能量分布")
    chart_data = df_raw.sort_values("數字").set_index("數字")
    st.bar_chart(chart_data["評分"])
    
    #
