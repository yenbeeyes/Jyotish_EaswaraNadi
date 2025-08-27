
import streamlit as st
import pandas as pd

# Load data from CSV
df = pd.read_csv("EswaraNadi_AllLagnas_with_ImagePath.csv")

# Ordered Lagnas
ordered_lagnas = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# App title
st.title("Eswara Nadi - Surya Khandam")

# View mode selection
mode = st.sidebar.radio("Select View Mode", ["By Lagna", "ALL Charts"])

if mode == "By Lagna":
    selected_lagna = st.selectbox("Select Lagna", ordered_lagnas)
    st.subheader(f"Lagna: {selected_lagna}")
    keyword = st.text_input("Search keyword in Result (optional)").strip()

    filtered_df = df[df["Lagna"].str.strip().str.capitalize() == selected_lagna]

    if keyword:
        filtered_df = filtered_df[filtered_df["Result"].str.contains(keyword, case=False, na=False)]

    for _, row in filtered_df.iterrows():
        st.markdown(f"### Chart No: {row['ChartNo']}")
        st.markdown(f"**Sun:** {row['Sun']} | **Moon:** {row['Moon']} | **Mars:** {row['Mars']}")
        st.markdown(f"**Mercury:** {row['Mercury']} | **Jupiter:** {row['Jupiter']} | **Venus:** {row['Venus']}")
        st.markdown(f"**Saturn:** {row['Saturn']} | **Rahu:** {row['Rahu']} | **Ketu:** {row['Ketu']}")
        st.image(row['ImagePath'], use_container_width=True)
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
    current_df = df[df["Lagna"].str.strip().str.capitalize() == current_lagna]

    for _, row in current_df.iterrows():
        st.markdown(f"### Chart No: {row['ChartNo']}")
        st.markdown(f"**Sun:** {row['Sun']} | **Moon:** {row['Moon']} | **Mars:** {row['Mars']}")
        st.markdown(f"**Mercury:** {row['Mercury']} | **Jupiter:** {row['Jupiter']} | **Venus:** {row['Venus']}")
        st.markdown(f"**Saturn:** {row['Saturn']} | **Rahu:** {row['Rahu']} | **Ketu:** {row['Ketu']}")
        st.image(row['ImagePath'], use_container_width=True)
        st.markdown("**Result:**")
        st.write(row['Result'])
        st.markdown("---")
