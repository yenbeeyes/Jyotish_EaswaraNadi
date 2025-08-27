import streamlit as st
import pandas as pd

# App title
st.set_page_config(page_title="Eswara Nadi - Surya Khandam", layout="wide")
st.title("🕉️ Eswara Nadi - Surya Khandam")

# Try loading data
csv_file = "EswaraNadi_AllLagnas_with_ImagePath.csv"
try:
    df = pd.read_csv(csv_file)
except Exception as e:
    st.error(f"Failed to load CSV: {e}")
    st.stop()

# Define ordered Lagnas
ordered_lagnas = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Sidebar options
mode = st.sidebar.radio("📋 View Mode", ["By Lagna", "ALL Charts"])

if mode == "By Lagna":
    selected_lagna = st.selectbox("Select Lagna", ordered_lagnas)
    st.subheader(f"🔯 Lagna: {selected_lagna}")
    keyword = st.text_input("🔎 Search keyword in Result (optional)").strip()

    filtered_df = df[df["Lagna"].str.strip().str.capitalize() == selected_lagna]

    if keyword:
        filtered_df = filtered_df[filtered_df["Result"].str.contains(keyword, case=False, na=False)]

    if filtered_df.empty:
        st.warning("No results found for this Lagna with the given keyword.")
    else:
        for _, row in filtered_df.iterrows():
            st.markdown(f"### 📊 Chart No: {int(row['ChartNo'])}")
            st.markdown(f"**Sun:** {row['Sun']} | **Moon:** {row['Moon']} | **Mars:** {row['Mars']}")
            st.markdown(f"**Mercury:** {row['Mercury']} | **Jupiter:** {row['Jupiter']} | **Venus:** {row['Venus']}")
            st.markdown(f"**Saturn:** {row['Saturn']} | **Rahu:** {row['Rahu']} | **Ketu:** {row['Ketu']}")
            if pd.notna(row["ImagePath"]):
                st.image(row["ImagePath"], use_container_width=True)
            st.markdown("**Result:**")
            st.write(row["Result"])
            st.markdown("---")

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
        st.warning("No charts found for this Lagna.")
    else:
        for _, row in current_df.iterrows():
            st.markdown(f"### 📊 Chart No: {int(row['ChartNo'])}")
            st.markdown(f"**Sun:** {row['Sun']} | **Moon:** {row['Moon']} | **Mars:** {row['Mars']}")
            st.markdown(f"**Mercury:** {row['Mercury']} | **Jupiter:** {row['Jupiter']} | **Venus:** {row['Venus']}")
            st.markdown(f"**Saturn:** {row['Saturn']} | **Rahu:** {row['Rahu']} | **Ketu:** {row['Ketu']}")
            if pd.notna(row["ImagePath"]):
                st.image(row["ImagePath"], use_container_width=True)
            st.markdown("**Result:**")
            st.write(row["Result"])
            st.markdown("---")