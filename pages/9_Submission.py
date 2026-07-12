import streamlit as st
from sidebar import render_sidebar

# from utils.session_tracker import track_session
# track_session()


st.set_page_config(
    page_title="Contact Us",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

# ─── Feedback form ────────────────────────────────────────────────────────
st.markdown("""
<style>
 /* 1) Centered title with10px top margin */
  h2.custom-title {
    text-align: center !important;
    margin-top: 0px !important;
    color: #29004c;
  }
</style>
""", unsafe_allow_html=True)

# --- Centered, spaced title ---
st.markdown(
    '<h2 class="custom-title">'
    'SUBMISSION FORM'
    '</h2>',
    unsafe_allow_html=True
)

st.markdown("""
<style>
/* Add spacing between fields */
form label {
    display: block;
    margin-top: 0px;
    margin-bottom: 0px;
    font-weight: bold;
}

form input[type="text"],
form input[type="email"],
form textarea {
    width: 100%;
    padding: 0px;
    border-radius: 5px;
    border: 1px solid #ccc;
    margin-bottom: 0px; 
}

/* File upload spacing */
form input[type="file"] {
    margin-top: 3px;
}

/* Submit button styling */
form button {
    margin-top: 0px;
    background-color: #9e9ac8; /* purple */
    color: #000000;
    padding: 2px 4px;
    border-radius: 5px;
    font-size: 1.2em;
    cursor: pointer;
}

form button:hover {
    background-color: #6a51a3;
}
</style>

<form action="https://formsubmit.co/vtran23@wisc.edu" method="POST" enctype="multipart/form-data">
  <label for="name">Full Name *</label><br>
  <input type="text" name="name" required style="width:100%; padding:5px;"><br><br>

  <label for="title">Title/Position (optional)</label><br>
  <input type="text" name="title" style="width:100%; padding:5px;"><br><br>

  <label for="institution">Institution/Organization *</label><br>
  <input type="text" name="institution" required style="width:100%; padding:5px;"><br><br>

  <label for="email">Email Address *</label><br>
  <input type="email" name="email" required style="width:100%; padding:5px;"><br><br>

  <label for="message">Your Message/Feedback *</label><br>
  <textarea name="message" required rows="6" style="width:100%; padding:5px;"></textarea><br><br>

  <label for="attachment">Attach a file (optional)</label><br>
  <input type="file" name="attachment"><br><br>

  <!-- Centered primary-style submit button -->
  <div style="text-align:center;">
    <button type="submit" style="padding:5px 5px;">
      SUBMIT
    </button>
  </div>
</form>
""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; font-size: 14px; color: #2a2541;">
  <em>Last update: Jul 2026</em>
</div>
""", unsafe_allow_html=True)
