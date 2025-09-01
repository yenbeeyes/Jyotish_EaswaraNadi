import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(page_title="Eswara Nadi - Surya Khandam", layout="wide")

# Header
st.markdown("## 🕉️ Eswara Nadi - Surya Khandam")
st.markdown("""
Welcome to the digitized archive of the **Surya Khandam** section of the *Eswara Nadi*.  
Explore ancient planetary configurations, astrological predictions, and original chart images —  
organized by **Lagna** as given by Agasthiyar.  
---
""")

# File paths
# File paths
CHART_CSV = "EswaraNadi_AllLagnasCSV.csv"
VERSE_CSV = "Surya.csv"
BASE_IMAGE_FOLDER = r"Jyotish_EaswaraNadi/images"

# Load chart data
@st.cache_data
def load_chart_data(path):
    df = pd.read_csv(path, encoding='utf-8')
    df["VerseID"] = df["VerseID"].astype(str).str.strip()
    df["Lagna"] = df["Lagna"].astype(str).str.strip().str.capitalize()
    df["ImagePath"] = df["ImagePath"].astype(str).str.strip()
    return df

# Load verse data
@st.cache_data
def load_verse_data(path):
    df = pd.read_csv(path, encoding='utf-8')
    df["VerseID"] = df["VerseID"].astype(str).str.strip()
    return df

# Load datasets
try:
    df = load_chart_data(CHART_CSV)
    verses_df = load_verse_data(VERSE_CSV)
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# Utility
def safe(val):
    return "" if pd.isna(val) or str(val).lower() == "nan" else str(val)

# Sidebar controls
verse_option = st.sidebar.radio("📝 Verse Display", ["Side-by-Side"], index=0)
mode = st.sidebar.radio("📋 View Mode", ["By Lagna", "ALL Charts"])
edit_mode = st.sidebar.checkbox("✏️ Enable Verse Editing")
st.sidebar.markdown("---")
st.sidebar.markdown("📬 [Submit Feedback](https://docs.google.com/forms/d/e/1FAIpQLSeSUwk-YoFoLkORQnO5l7C92_Xrg1yAULhQPg7EgdpTLLcN6A/viewform)")

# Lagna order
ordered_lagnas = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Display verse block with editor
def display_verse_block(verse_id, editable=False):
    verse_row = verses_df[verses_df["VerseID"] == verse_id]
    if not verse_row.empty:
        tamil = safe(verse_row.iloc[0].get("TamilVerse", ""))
        english = safe(verse_row.iloc[0].get("EnglishTranslation", ""))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📝 Tamil Verse**")
            st.write(tamil)
        with col2:
            st.markdown("**📘 English Translation**")
            st.write(english)

        if editable:
            st.markdown("### ✏️ Edit Verse")
            new_tamil = st.text_area("Tamil Verse", value=tamil, key=f"tamil_{verse_id}")
            new_english = st.text_area("English Translation", value=english, key=f"english_{verse_id}")
            if st.button(f"💾 Save Verse {verse_id}"):
                verses_df.loc[verses_df["VerseID"] == verse_id, "TamilVerse"] = new_tamil
                verses_df.loc[verses_df["VerseID"] == verse_id, "EnglishTranslation"] = new_english
                verses_df.to_csv(VERSE_CSV, index=False, encoding='utf-8')
                st.success(f"✅ Verse `{verse_id}` updated successfully.")
    else:
        st.info(f"📜 Verse not available for `{verse_id}`.")

# Mode: By Lagna
if mode == "By Lagna":
    selected_lagna = st.selectbox("Select Lagna", ordered_lagnas, key="lagna_select")
    st.subheader(f"🔯 Lagna: {selected_lagna}")
    keyword = st.text_input("🔎 Search keyword in Result (optional)", key="keyword_input").strip()

    filtered_df = df[df["Lagna"] == selected_lagna]
    if keyword:
        filtered_df = filtered_df[filtered_df["Result"].str.contains(keyword, case=False, na=False)]

    if filtered_df.empty:
        st.warning("No results found.")
    else:
        for _, row in filtered_df.iterrows():
            with st.expander(f"📊 {row['Lagna']} Lagna — Chart ID: {row['VerseID']}"):
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

                verse_id = str(row["VerseID"]).strip()
                filename = verse_id.replace("-", "_") + ".jpg"
                image_path = os.path.join(BASE_IMAGE_FOLDER, filename)

                if os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)
                else:
                    st.info("📁 Image not available.")
                st.caption(f"🖼️ ImagePath: `{image_path}`")
                display_verse_block(row["VerseID"], editable=edit_mode)
                st.markdown("**Result:**")
                st.write(safe(row["Result"]))

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
    current_df = df[df["Lagna"] == current_lagna]

    if current_df.empty:
        st.warning("No charts found.")
    else:
        for _, row in current_df.iterrows():
            with st.expander(f"📊 {row['Lagna']} Lagna — Chart ID: {row['VerseID']}"):
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

                image_path = safe(row["ImagePath"])
                if image_path and os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)
                else:
                    st.info("📁 Image not available.")
                st.caption(f"🖼️ ImagePath: `{image_path}`")

                display_verse_block(row["VerseID"], editable=edit_mode)
                st.markdown("**Result:**")
                st.write(safe(row["Result"]))