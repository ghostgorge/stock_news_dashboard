import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="📊 股票分析 + 📰 实时新闻", layout="wide")
st.title("📊 股票分析 + 📰 实时新闻面板")

# 股票输入
ticker = st.text_input("请输入股票代码（如 AAPL、TSLA、GOOG）", value="AAPL")

col1, col2 = st.columns([2, 1])

# ==============================
# 📈 股票历史数据 + 图表分析
# ==============================
with col1:
    st.subheader(f"📈 股票趋势分析：{ticker}")

    stock = yf.Ticker(ticker)

    df = stock.history(period="6mo")  # 6 个月历史
    if df.empty:
        st.error("无法获取股票数据，请确认代码是否正确。")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines', name='收盘价'))
        fig.update_layout(title=f"{ticker} 收盘价走势", xaxis_title="日期", yaxis_title="价格")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("📌 数据摘要")
        st.dataframe(df.tail(5))

# ==============================
# 📰 实时新闻抓取
# ==============================
with col2:
    st.subheader(f"📰 {ticker} 新闻动态")

    def get_news(symbol):
        url = f"https://finance.yahoo.com/quote/{symbol}?p={symbol}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        news_list = []

        for li in soup.find_all("li", {"class": "js-stream-content"}):
            a_tag = li.find("a")
            if a_tag and a_tag.text:
                title = a_tag.text.strip()
                link = "https://finance.yahoo.com" + a_tag["href"]
                news_list.append((title, link))
        return news_list[:5]

    try:
        news = get_news(ticker)
        if news:
            for title, link in news:
                st.markdown(f"- [{title}]({link})")
        else:
            st.info("暂无相关新闻或未获取到内容。")
    except Exception as e:
        st.error(f"获取新闻失败：{e}")
