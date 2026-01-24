import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析終端", layout="centered")

st.title("📊 PRO 數據分析預測終端")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與警示 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交並更新預測", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    if len(st.session_state.history) >= 10:
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_c * 10
        st.write(f"📈 中軸命中率: **{win_rate}%**")
        if win_rate <= 30:
            st.error(f"⚠️ 預警：命中率低於30%！")
    
    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [8,9,10] and e in [8,9,10]: score += 15
        if last in [5,7,9] and e in [5,7,9]: score += 12
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22 
        results.append({"數字": e, "評分": score})
    return pd.DataFrame(results).sort_values("數字")

# --- 主畫面顯示 ---
if st.session_state.history:
    df_res = analyze_data(st.session_state.history)
    
    # 🏆 熱門推薦
    top_3 = df_res.sort_values("評分", ascending=False).head(3)
    top_3_list = top_3['數字'].astype(int).tolist()
    
    st.subheader("🏆 熱門推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_3_list[0])
    c2.metric("第二輔助", top_3_list[1])
    c3.metric("第三防守", top_3_list[2])
    
    # ❄️ 冷門提醒
    bottom_2 = df_res.sort_values("評分").head(2)
    st.markdown(f"**❄️ 冷門避雷：** `{bottom_2['數字'].iloc[0]}`, `{bottom_2['數字'].iloc[1]}`")
    st.divider()

    # 📊 升級版彩色 Plotly 圖表
    # 定義顏色：高分為紅，低分為灰藍
    fig = px.bar(df_res, x='數字', y='評分', 
                 color='評分', 
                 color_continuous_scale=['#455a64', '#ffd54f', '#ff5252'], # 灰 -> 黃 -> 紅
                 range_color=[-10, 45],
                 text_auto='.1f')
    
    fig.update_layout(xaxis=dict(tickmode='linear'), coloraxis_showscale=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 注碼與盤勢
    best_score = top_3['評分'].iloc[0]
    if best_score > 65: st.error("💰 注碼建議：💥 強烈重注")
    elif best_score > 55: st.success("💰 注碼建議：🏹 穩健布局")
    else: st.info("💰 注碼建議：🛡️ 試探輕注")
        
    with st.expander("📜 查看 100 手紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👈 請輸入數據開始預測")
