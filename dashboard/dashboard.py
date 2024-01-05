import streamlit as st

st.set_page_config(
    page_title="Deloton Dashboard",
    page_icon="🚲",
    layout="wide"
)

st.write("# Deloton Bike Analysis🚴")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    Realtime dashboard to give the business visibility on the
    current and recent behaviour of riders.\n

    **👈 Select a page from the sidebar** to see the current or recent rides.
    """)
