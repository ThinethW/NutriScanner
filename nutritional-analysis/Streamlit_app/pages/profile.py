import streamlit as st


def show():
    st.title("👤 User Profile")

    with st.form("profile"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Name", "User")
            age = st.number_input("Age", 18, 100, 25)
            weight = st.number_input("Weight (kg)", 40, 200, 70)

        with col2:
            height = st.number_input("Height (cm)", 100, 250, 170)
            activity = st.selectbox("Activity", ["Sedentary", "Moderate", "Active"])

        if st.form_submit_button("Save"):
            st.success("Profile saved!")