import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="Claude Code Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.views import (
    overview, token_analysis, tool_analysis,
    user_analysis, predictions, advanced_stats, realtime,
)

PAGES = {
    "Overview": overview,
    "Token & Cost Analysis": token_analysis,
    "Tool & Error Analysis": tool_analysis,
    "User & Session Analysis": user_analysis,
    "Advanced Statistics": advanced_stats,
    "Predictive Analytics": predictions,
    "Real-Time Streaming": realtime,
}

st.sidebar.title("Claude Code Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", list(PAGES.keys()))

st.sidebar.markdown("---")
st.sidebar.caption("Built for Provectus Internship Assignment")
st.sidebar.caption("Data: Synthetic Claude Code Telemetry")

PAGES[page].render()
