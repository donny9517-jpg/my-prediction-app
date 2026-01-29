import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據統計分析", layout="centered")

st.title("📊 PRO 數據統計分析終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    total_h = len(st.session_state.history)
    st.write(f"🔢 當前總手數: **{total_h}**")
    
    if total_h >= 1:
        # A. 累積命中率 (6,7,8)
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        cumulative_win_rate = (win_c / total_h) * 100
        st.metric("📈 累積中軸命中", f"{cumulative_win_rate:.1f}%")
        
        # B. 標準差監控 (最近 10 手波動)
        if total_h >= 5:
            std_dev = np.std(st.session_state.history[-10:])
            st.write(f"波動指數 (STD): **{std_dev:.2f}**")
            if std_dev < 1.2: st.info("⚡ 狀態: 極度集中")
            elif std_dev > 2.8: st.warning("⚡ 狀態: 劇烈跳動")

    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    for e in range(2, 13):
        score = (prob_map[e] / 36) * 100
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    # 週期提醒
    curr_len = len(st.session_state.history)
    if curr_len % 36 == 0:
        st.info(f"💡 **週期提醒**: 已達 36 手週期，建議觀察數據回歸情況。")

    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 Top 3 推薦
    top_list = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 熱門預測 Top 3")
    c1, c2, c3 = st.columns(3)
    c1.metric("首選", top_list[0])
    c2.metric("次選", top_list[1])
    c3.metric("防守", top_list[2])
    
    # --- 🔍 統計指標區 ---
    st.divider()
    st.subheader("🕵️ 深度統計監控")
    
    hist_list = st.session_state.history
    
    # 1. 大數 / 小數 比例 (最近 20 手)
    last_scope = hist_list[-20:]
    big_count = sum(1 for x in last_scope if x > 7)
    small_count = sum(1 for x in last_scope if x < 7)
    mid_count = len(last_scope) - big_count - small_count
    
    s1, s2, s3 = st.columns(3)
    s1.write(f"🔴 大號 (8-12): **{big_count}**")
    s2.write(f"⚪ 中軸 (7): **{mid_count}**")
    s3.write(f"🔵 小號 (2-6): **{small_count}**")
    
    # 2. 冷熱度分析 (Frequency Analysis)
    st.write("🔥 **號碼出現次數統計 (全歷史)**")
    freq_data = pd.Series(hist_list).value_counts().reindex(range(2, 13), fill_value=0)
    st.bar_chart(freq_data)

    st.divider()

    # 原有能量圖與建議
    st.write("📊 **即時能量預測評分**")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
    
    best_s = df_res.iloc[0]['評分']
    if best_s > 65: st.error("💰 注碼建議: 💥 強烈重注")
    elif best_s > 55: st.success("💰 注碼建議: 🏹 穩健布局")
    else: st.info("💰 注碼建議: 🛡️ 試探輕注")

    with st.expander("📜 歷史紀錄"):
        st.write(hist_list[-100:][::-1])
else:
    st.info("👋 歡迎使用！請從側邊欄輸入數據。")
