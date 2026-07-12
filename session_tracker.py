import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# REPLACE THIS with your actual Google Analytics Measurement ID
# ============================================================
GA_MEASUREMENT_ID = "G-PJWSYXYGEM"


def track_session():
    """Inject Google Analytics once per session. Zero cost on reruns."""

    # If already injected this session, do nothing
    if st.session_state.get("_ga_injected", False):
        return

    # Inject GA script once — runs in the browser, not in Python
    components.html(
        f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{ dataLayer.push(arguments); }}
            gtag('js', new Date());
            gtag('config', '{GA_MEASUREMENT_ID}');
        </script>
        """,
        height=0,
    )

    # Mark as done so we never run this again in this session
    st.session_state["_ga_injected"] = True

