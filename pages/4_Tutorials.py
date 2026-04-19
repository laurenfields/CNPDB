import streamlit as st
from sidebar import render_sidebar
import os
import base64

from utils.session_tracker import track_session
track_session()


st.set_page_config(
    page_title="Tutorials",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

st.markdown("""
<h3 style="margin-top: 10px; margin-bottom: 10px;">
1. How to navigate cNPDB website
</h3>
""", unsafe_allow_html=True)
video_path = os.path.join("Assets", "Statistics", "cNPDB_General_Compressed.mp4")
if os.path.exists(video_path):
    video_bytes = open(video_path, "rb").read()
    video_base64 = base64.b64encode(video_bytes).decode()

    st.markdown(f"""
        <div style="width: 700px; height: 400px; margin: 0 auto; display: flex; justify-content: center; align-items: center;">
            <video width="700" height="400" controls>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error(f"Video not found at {video_path}")


st.markdown("""
<h3 style="margin-top: 10px; margin-bottom: 10px;">
2. How to use Database Search Engine to search for your desired peptides and download FASTA file
</h3>
""", unsafe_allow_html=True)
video_path = os.path.join("Assets", "Statistics", "cNPDB_NP Database search_Compressed.mp4")
if os.path.exists(video_path):
    video_bytes = open(video_path, "rb").read()
    video_base64 = base64.b64encode(video_bytes).decode()

    st.markdown(f"""
        <div style="width: 700px; height: 400px; margin: 0 auto; display: flex; justify-content: center; align-items: center;">
            <video width="700" height="400" controls>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error(f"Video not found at {video_path}")


st.markdown("""
<div style="text-align: center; font-size:14px; color:#2a2541;">
  <em>Last update: Apr 2026</em>
</div>
""", unsafe_allow_html=True)

