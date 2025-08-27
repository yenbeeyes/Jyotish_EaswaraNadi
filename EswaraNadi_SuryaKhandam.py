
import streamlit as st
import pandas as pd
import pyodbc
import io
from PIL import Image

# === CONFIGURATION ===
use_sql_login = False  # Set to True if using SQL username/password login

# === CONNECTION STRINGS ===
if use_sql_login:
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=YENBEEYES;"
        "Database=Jyotish;"
        "UID=your_sql_username;"
        "PWD=your_sql_password;"
        "Encrypt=no;"
    )
else:
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=YENBEEYES;"
        "Database=Jyotish;"
        "Trusted_Connection=yes;"
        "Encrypt=no;"
    )

# === CONNECT ===
try:
    conn = pyodbc.connect(conn_str)
except Exception as e:
    st.error(f"❌ Database connection failed: {e}")
    st.stop()

# === Load Data with SQL ORDER BY CASE ===
try:
    df = pd.read_sql("""
        SELECT *
        FROM dbo.EswaraNadi 
        ORDER BY
          CASE Lagna
            WHEN 'Aries' THEN 1
            WHEN 'Taurus' THEN 2
            WHEN 'Gemini' THEN 3
            WHEN 'Cancer' THEN 4
            WHEN 'Leo' THEN 5
            WHEN 'Virgo' THEN 6
            WHEN 'Libra' THEN 7
            WHEN 'Scorpio' THEN 8
            WHEN 'Sagittarius' THEN 9
            WHEN 'Capricorn' THEN 10
            WHEN 'Aquarius' THEN 11
            WHEN 'Pisces' THEN 12
            ELSE 13
          END,
          ChartNo
    """, conn)
except Exception as e:
    st.error(f"❌ Failed to load table 'Jyotish': {e}")
    st.stop()

# === Ordered Lagnas ===
ordered_lagnas = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# === UI ===
st.title("Eswara Nadi - Surya Khandam")
mode = st.sidebar.radio("Select View Mode", ["By Lagna", "ALL Jyotish"])

if mode == "By Lagna":
    selected_lagna = st.selectbox("Select Lagna", ordered_lagnas)
    st.subheader(f"Lagna: {selected_lagna}")
    keyword = st.text_input("Search keyword in Result (optional)").strip()
    filtered_df = df[df["Lagna"] == selected_lagna]

    if keyword:
        filtered_df = filtered_df[filtered_df["Result"].str.contains(keyword, case=False, na=False)]

    for _, row in filtered_df.iterrows():
        st.markdown(f"### Chart No: {row['ChartNo']}")
        st.markdown(f"**Sun:** {row['Sun']} | **Moon:** {row['Moon']} | **Mars:** {row['Mars']}")
        st.markdown(f"**Mercury:** {row['Mercury']} | **Jupiter:** {row['Jupiter']} | **Venus:** {row['Venus']}")
        st.markdown(f"**Saturn:** {row['Saturn']} | **Rahu:** {row['Rahu']} | **Ketu:** {row['Ketu']}")
        if row['ChartImage']:
            try:
                img = Image.open(io.BytesIO(row['ChartImage']))
                st.image(img, use_container_width=True)
            except:
                st.warning("⚠️ Unable to load image.")
        st.markdown("**Result:**")
        st.write(row['Result'])
        st.markdown("---")

elif mode == "ALL Charts":
    if "chart_index" not in st.session_state:
        st.session_state.chart_index = 0

    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("Previous") and st.session_state.chart_index > 0:
            st.session_state.chart_index -= 1
    with col2:
        if st.button("Next") and st.session_state.chart_index < len(ordered_lagnas) - 1:
            st.session_state.chart_index += 1

    current_lagna = ordered_lagnas[st.session_state.chart_index]
    st.subheader(f"Lagna: {current_lagna}")
    current_df = df[df["Lagna"] == current_lagna]

    for _, row in current_df.iterrows():
        st.markdown(f"### Chart No: {row['ChartNo']}")
        st.markdown(f"**Sun:** {row['Sun']} | **Moon:** {row['Moon']} | **Mars:** {row['Mars']}")
        st.markdown(f"**Mercury:** {row['Mercury']} | **Jupiter:** {row['Jupiter']} | **Venus:** {row['Venus']}")
        st.markdown(f"**Saturn:** {row['Saturn']} | **Rahu:** {row['Rahu']} | **Ketu:** {row['Ketu']}")
        if row['ChartImage']:
            try:
                img = Image.open(io.BytesIO(row['ChartImage']))
                st.image(img, use_container_width=True)
            except:
                st.warning("⚠️ Unable to load image.")
        st.markdown("**Result:**")
        st.write(row['Result'])
        st.markdown("---")
