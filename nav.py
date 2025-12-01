import streamlit as st

pages = {
    "Main": [
        st.Page("app.py", title="Land Pollution Predictor"),
        st.Page("phone.py", title="Eco Waste Advisor"),
        st.Page("phone2.py", title="Food Ecofriendly Advisor"),
        ],
}

pg = st.navigation(pages)
pg.run()