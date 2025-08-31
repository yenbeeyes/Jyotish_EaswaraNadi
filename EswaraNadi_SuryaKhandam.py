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
def getv(row, key, default=""):
    try:
        # row is a pandas Series
        if key in row and pd.notna(row[key]):
            return safe(row[key])
        return default
    except Exception:
        return default


# Display logic
def display_chart(row):
    # Title: guard against NaN / missing ChartNo
    chart_no = getv(row, "ChartNo")
    title = f"📊 Chart No: {chart_no}" if chart_no else "📊 Chart"
    with st.expander(title):
        st.markdown(
            f"**Sun:** {getv(row,'Sun')} | **Moon:** {getv(row,'Moon')} | **Mars:** {getv(row,'Mars')}"
        )
        st.markdown(
            f"**Mercury:** {getv(row,'Mercury')} | **Jupiter:** {getv(row,'Jupiter')} | **Venus:** {getv(row,'Venus')}"
        )
        st.markdown(
            f"**Saturn:** {getv(row,'Saturn')} | **Rahu:** {getv(row,'Rahu')} | **Ketu:** {getv(row,'Ketu')}"
        )

        # Image (only try if a non-empty path is present)
        img_path = getv(row, "ImagePath")
        if img_path:
            try:
                st.image(img_path, use_container_width=True)
            except Exception:
                st.info("📁 Image not available.")
        else:
            st.info("📁 Image not available.")

        # Result
        result_text = getv(row, "Result")
        if result_text:
            st.markdown("**📝 Result:**")
            st.write(result_text)

        # Tamil verse
        ta = getv(row, "TamilVerse")
        if ta:
            st.markdown("**🗣️ Tamil Verse:**")
            st.markdown(
                f"<div style='font-family: Latha, Tamil MN, serif; font-size: 16px;'>{ta}</div>",
                unsafe_allow_html=True,
            )

        # English translation
        en = getv(row, "EnglishTranslation")
        if en:
            st.markdown("**🌐 English Translation:**")
            st.write(en)


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