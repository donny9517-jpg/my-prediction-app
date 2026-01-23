import streamlit as st
import pandas as pd

# 1. 網頁基礎設定與極致黑金 CSS
st.set_page_config(page_title="PRO 數據分析終端", layout="wide")

st.markdown("""
    <style>
    /* 全域深色背景優化 */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* 看板數字字體加粗與陰影 */
    [data-testid="stMetricValue"] { 
        font-size: 58px !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
    }
    
    /* 第一格：重點布局 - 螢光金 (Gold) */
    [data-testid="column"]:nth-of-type(1) [data-testid="stMetricValue"] { color: #FFD700 !important; }
    
    /* 第二格：注碼建議 - 鮮紅 (Red) */
    [data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] { color: #FF3131 !important; }
    
    /* 第三格：目前盤勢 - 電子藍 (Cyan) */
    [data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] { color: #00E5FF !important; }
    
    /* 表格滾動區域與側邊欄文字優化 */
    .stDataFrame { border: 1px solid #30363d; border-radius: 8px; }
    .css-17l2qt2 { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據（存儲於會話中，不保存至硬碟）
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入、清空與即時命中率 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數據並更新預測", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 側邊欄指標：近 10 手中軸命中率 (6,7,8)
    if len(st.session_state.history) >= 10:
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        st.metric("📈 近 10 手中軸命中率", f"{win_c * 10}%")
    else:
        st.caption("需至少 10 手數據以計算命中率")
    
    st.divider()
