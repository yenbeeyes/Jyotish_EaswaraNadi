
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
---""")

# File paths
CHART_CSV = "Surya_Khandam/Chandra_Khandam.csv"

@st.cache_data
def load_chart_data(path):
    df = pd.read_csv(path, encoding='utf-8')
    df["VerseID"] = df["VerseID"].astype(str).str.strip()
    df["Lagna"] = df["Lagna"].astype(str).str.strip().str.capitalize()
    df["ImagePath"] = df["ImagePath"].astype(str).str.strip()
    return df

@st.cache_data
def load_verse_data_by_lagna(lagna):
    filename = f"Surya_Khandam/Surya_Verses_{lagna}.csv"
    try:
        df = pd.read_csv(filename, encoding='utf-8')
        df["VerseID"] = df["VerseID"].astype(str).str.strip()
        return df
    except Exception as e:
        st.warning(f"⚠️ Verse file not found for `{lagna}`: {e}")
        return pd.DataFrame()

try:
    df = load_chart_data(CHART_CSV)
except Exception as e:
    st.error(f"❌ Failed to load chart data: {e}")
    st.stop()

def safe(val):
    return "" if pd.isna(val) or str(val).lower() == "nan" else str(val)

mode = st.sidebar.radio("📋 View Mode", ["By Lagna", "ALL Charts"])
edit_mode = st.sidebar.checkbox("✏️ Enable Verse Editing")

ordered_lagnas = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def display_verse_block(verse_id, verses_df, editable=False):
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
                verses_df.to_csv(f"Surya_Khandam/Surya_Verses_{selected_lagna}.csv", index=False, encoding='utf-8')
                st.success(f"✅ Verse `{verse_id}` updated successfully.")
    else:
        st.info(f"📜 Verse not available for `{verse_id}`.")

if mode == "By Lagna":
    selected_lagna = st.selectbox("Select Lagna", ordered_lagnas, key="lagna_select")
    st.subheader(f"🔯 Lagna: {selected_lagna}")
    verses_df = load_verse_data_by_lagna(selected_lagna)
    filtered_df = df[df["Lagna"] == selected_lagna]
    if filtered_df.empty:
        st.warning("No charts found.")
    else:
        for _, row in filtered_df.iterrows():
            with st.expander(f"📊 {row['Lagna']} Lagna — Chart ID: {row['VerseID']}"):
                st.markdown(
                    f"**Sun:** {safe(row['Sun'])} | **Moon:** {safe(row['Moon'])} | **Mars:** {safe(row['Mars'])} | "
                    f"**Mercury:** {safe(row['Mercury'])} | **Jupiter:** {safe(row['Jupiter'])} | **Venus:** {safe(row['Venus'])} | "
                    f"**Saturn:** {safe(row['Saturn'])} | **Rahu:** {safe(row['Rahu'])} | **Ketu:** {safe(row['Ketu'])}"
                )
                image_path = safe(row["ImagePath"])
                if image_path:
                    image_url = image_path.replace(
                        "Surya_Khandam/images/",
                        "https://raw.githubusercontent.com/yenbeeyes/Jyotish_EaswaraNadi/main/Surya_Khandam/images/"
                    )
                    st.image(image_url, use_container_width=True)
                    st.caption(f"🖼️ ImagePath: `{image_url}`")
                else:
                    st.info("📁 Image not available.")
                display_verse_block(row["VerseID"], verses_df, editable=edit_mode)
                st.markdown("**Result:**")
                st.write(safe(row["Result"]))
