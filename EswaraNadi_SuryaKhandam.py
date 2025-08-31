import streamlit as st
import pandas as pd

# Configure page
st.set_page_config(page_title="Eswara Nadi - Surya Khandam", layout="wide")

# Welcome header
st.markdown("## 🕉️ Eswara Nadi - Surya Khandam")
st.markdown(
    """
    Welcome to the digitized archive of the **Surya Khandam** section of the *Eswara Nadi*.  
    Explore ancient planetary configurations, astrological predictions, and original chart images —  
    organized by **Lagna** for each native.  
    ---
    """
)

# Load data
csv_file = "EswaraNadi_AllLagnas_with_ImagePath.csv"
try:
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.strip()  # Clean column names
except Exception as e:
    st.error(f"Failed to load CSV: {e}")
    st.stop()

# Lagna order
ordered_lagnas = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Sidebar mode switch
mode = st.sidebar.radio("📋 View Mode", ["By Lagna", "ALL Charts"])
st.sidebar.markdown("---")
st.sidebar.markdown("📬 [Submit Feedback](https://docs.google.com/forms/d/e/1FAIpQLSeSUwk-YoFoLkORQnO5l7C92_Xrg1yAULhQPg7EgdpTLLcN6A/viewform)")

# Utility function to clean NaN values
def safe(val):
    return "" if pd.isna(val) or str(val).lower() == "nan" else str(val)
filtered_df = df[
    df["Lagna"].fillna("").astype(str).str.strip().str.capitalize() == selected_lagna
]


# Display logic
def display_chart(row):
    with st.expander(f"📊 Chart No: {int(row['ChartNo'])}"):
        st.markdown(f"**Sun:** {row['Sun']} | **Moon:** {row['Moon']} | **Mars:** {row['Mars']}")
        st.markdown(f"**Mercury:** {row['Mercury']} | **Jupiter:** {row['Jupiter']} | **Venus:** {row['Venus']}")
        st.markdown(f"**Saturn:** {row['Saturn']} | **Rahu:** {row['Rahu']} | **Ketu:** {row['Ketu']}")
        
        if pd.notna(row.get("ImagePath", None)):
            try:
                st.image(row["ImagePath"], use_container_width=True)
            except:
                st.info("📁 Image not available.")
        
        st.markdown("**📝 Result:**")
        st.write(row.get("Result", "—"))

        # Tamil verse and English translation
        if pd.notna(row.get("TamilVerse", None)):
            st.markdown("**🗣️ Tamil Verse:**")
            st.markdown(f"<div style='font-family: Latha, Tamil MN, serif; font-size: 16px;'>{row['TamilVerse']}</div>", unsafe_allow_html=True)

        if pd.notna(row.get("EnglishTranslation", None)):
            st.markdown("**🌐 English Translation:**")
            st.write(row["EnglishTranslation"])

# Mode: By Lagna
if mode == "By Lagna":
    selected_lagna = st.selectbox("Select Lagna", ordered_lagnas)
    st.subheader(f"🔯 Lagna: {selected_lagna}")
    keyword = st.text_input("🔎 Search keyword in Result (optional)").strip()

    filtered_df = df[df["Lagna"].str.strip().str.capitalize() == selected_lagna]
    if keyword:
        filtered_df = filtered_df[filtered_df["Result"].str.contains(keyword, case=False, na=False)]

    if filtered_df.empty:
        st.warning("No results found.")
    else:
        for _, row in filtered_df.iterrows():
            display_chart(row)

# Mode: ALL Charts
elif mode == "ALL Charts":
    if "chart_index" not in st.session_state:
        st.session_state.chart_index = 0

    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("⬅️ Previous") and st.session_state.chart_index > 0:
            st.session_state.chart_index -= 1
    with col2:
        if st.button("Next ➡️") and st.session_state.chart_index < len(ordered_lagnas) - 1:
            st.session_state.chart_index += 1

    current_lagna = ordered_lagnas[st.session_state.chart_index]
    st.subheader(f"🔯 Lagna: {current_lagna}")
    current_df = df[df["Lagna"].str.strip().str.capitalize() == current_lagna]

    if current_df.empty:
        st.warning("No charts found.")
    else:
        for _, row in current_df.iterrows():
            display_chart(row)