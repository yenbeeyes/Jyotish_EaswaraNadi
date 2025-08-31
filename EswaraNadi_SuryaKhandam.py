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
except Exception as e:
    st.error(f"Failed to load CSV: {e}")
    st.stop()

# Load Surya verse translations
DEFAULT_VERSES_CSV = r"C:\EswaraNadi\Verses\Surya\Surya.csv"

@st.cache_data
def load_verses(csv_path):
    try:
        return pd.read_csv(csv_path, encoding='utf-8')
    except Exception as e:
        st.error(f"Failed to load Surya verses: {e}")
        return pd.DataFrame()

verses_df = load_verses(DEFAULT_VERSES_CSV)

# Sidebar verse display option
verse_option = st.sidebar.radio("📝 Verse Display", ["TamilVerse", "EnglishTranslation"], index=0)

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
            with st.expander(f"📊 Chart No: {int(row['ChartNo'])}"):
                st.markdown(
                    f"**Sun:** {safe(row['Sun'])} | "
                    f"**Moon:** {safe(row['Moon'])} | "
                    f"**Mars:** {safe(row['Mars'])}"
                )
                st.markdown(
                    f"**Mercury:** {safe(row['Mercury'])} | "
                    f"**Jupiter:** {safe(row['Jupiter'])} | "
                    f"**Venus:** {safe(row['Venus'])}"
                )
                st.markdown(
                    f"**Saturn:** {safe(row['Saturn'])} | "
                    f"**Rahu:** {safe(row['Rahu'])} | "
                    f"**Ketu:** {safe(row['Ketu'])}"
                )

                if pd.notna(row["ImagePath"]):
                    try:
                        st.image(row["ImagePath"], use_container_width=True)
                    except:
                        st.info("📁 Image not available.")

# Display verse if available
verse_no = int(row["VerseNo"])
verses_df["VerseNo"] = verses_df["VerseNo"].astype(int)  # Ensure type match
verse_row = verses_df[verses_df["VerseNo"] == verse_no]

if not verse_row.empty and verse_option in verse_row.columns:
    st.markdown(f"**{verse_option}:**")
    st.write(verse_row.iloc[0][verse_option])
else:
    st.info("📜 Verse not available for this chart.")
                st.markdown("**Result:**")
                st.write(row.get("Result", "—"))

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
            with st.expander(f"📊 Chart No: {int(row['ChartNo'])}"):
                st.markdown(
                    f"**Sun:** {safe(row['Sun'])} | "
                    f"**Moon:** {safe(row['Moon'])} | "
                    f"**Mars:** {safe(row['Mars'])}"
                )
                st.markdown(
                    f"**Mercury:** {safe(row['Mercury'])} | "
                    f"**Jupiter:** {safe(row['Jupiter'])} | "
                    f"**Venus:** {safe(row['Venus'])}"
                )
                st.markdown(
                    f"**Saturn:** {safe(row['Saturn'])} | "
                    f"**Rahu:** {safe(row['Rahu'])} | "
                    f"**Ketu:** {safe(row['Ketu'])}"
                )

                if pd.notna(row["ImagePath"]):
                    try:
                        st.image(row["ImagePath"], use_container_width=True)
                    except:
                        st.info("📁 Image not available.")

# Display verse if available
chart_no = int(row["ChartNo"])
verses_df["ChartNo"] = verses_df["ChartNo"].astype(int)  # Ensure matching type
verse_row = verses_df[verses_df["ChartNo"] == chart_no]

if not verse_row.empty and verse_option in verse_row.columns:
    st.markdown(f"**{verse_option}:**")
    st.write(verse_row.iloc[0][verse_option])
else:
    st.info(f"📜 Verse not available for ChartNo {chart_no}.")
    
                st.markdown("**Result:**")
                st.write(row.get("Result", "—"))
                st.write(f"Looking for VerseNo: {verse_no}")

                st.write(verse_row)
