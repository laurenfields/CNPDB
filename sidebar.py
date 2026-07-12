# sidebar.py
import streamlit as st
from PIL import Image, ImageDraw
import os
import base64
from io import BytesIO

@st.cache_data
def get_logo_base64():
    """Process the logo image once and cache the base64 string."""
    logo_path = os.path.join("Assets", "Img", "Website_Logo_2.png")
    if not os.path.exists(logo_path):
        return None

    logo = Image.open(logo_path).convert("RGBA").resize((160, 160))
    mask = Image.new("L", (160, 160), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 160, 160), fill=255)
    logo.putalpha(mask)

    buffered = BytesIO()
    logo.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def render_sidebar():
    GA_MEASUREMENT_ID = "G-PJWSYXYGEM"
 
    st.markdown(
        f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{ dataLayer.push(arguments); }}
            gtag('js', new Date());
            gtag('config', '{GA_MEASUREMENT_ID}');
        </script>
        """,
        unsafe_allow_html=True,
    )
 
    st.markdown("""
    <style>
        html, body, .stApp {
            height: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        header[data-testid="stHeader"] {
            height: 0 !important;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }

        /* Reset default Streamlit sidebar styles */
        section[data-testid="stSidebar"] {
        background-color: #2a2541 !important;
        padding:0 !important; 
        margin:0 !important;
        height:100vh !important;
        display:flex !important;
        flex-direction:column !important;
        align-items:center !important;
        justify-content:flex-start !important;

        min-width: 330px !important;  
        max-width: 330px !important;
        width: 330px !important;
        }

        /* Fixes ghost search bar and mobile collapse weirdness */
        section[data-testid="stSidebar"] input,
        div[data-testid="collapsedControl"] {
        display: none !important;
        }

        .logo-container {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 0px;
        }
        .logo-border {
            width: 160px;
            height: 160px;
            border: 7px solid #555167;
            border-radius: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            margin: 0 auto;
        }
        .circle-img {
            width: 150px;
            height: 150px;
            border-radius: 100%;
        }
        .nav-container {
            padding: 0 !important;
            margin: 0 !important;
            width: 100%;
        }

        /* New sidebar navigation styles */
        .stPageLink {
            display:block !important;
            text-align:center !important;
            width:100% !important;
            margin:0 !important;
            padding:4px 0 !important;
        }
        .stPageLink a {
            color: white !important;
            font-family: 'Arial', sans-serif !important;
            font-size: 30px !important;
            font-weight: bold !important;
            text-transform: uppercase !important;
            text-align: center !important;
            letter-spacing: 0.5px !important;
            padding: 0px 8px !important;
            margin: 0 !important;
            width: 100% !important;
            display: block !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            text-decoration: none !important;
        }
        .stPageLink a:hover {
            background-color: #3a2d5a !important;
            color: #ffcc00 !important;
            text-decoration: none !important;
            font-weight: bold !important;
        }
    
        .stPageLink a:active {
            background-color: #4a3666 !important;
            font-weight: bold !important;
        }
    
        /* Add separator between nav items */
        .nav-separator {
            height: 0.1px;
            background-color: #555167;
            width: 10%;
            margin: 0 auto;
        }

        /* Ensure the text inside page links is white and centered */
        section[data-testid="stSidebar"] a span {
            color: #dadaeb !important;
            text-align: center !important;
            width: 100% !important;
            display: block !important;
            font-family: 'Arial', sans-serif !important;
            font-size: 30px !important;
            font-weight: bold !important;
        }

    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)

        # Use cached logo instead of reprocessing every time
        img_base64 = get_logo_base64()
        if img_base64:
            st.markdown(f"""
                <div class="logo-border">
                    <img src="data:image/png;base64,{img_base64}" class="circle-img" />
                </div>
            """, unsafe_allow_html=True)
        else:
            logo_path = os.path.join("Assets", "Img", "Website_Logo_2.png")
            st.error(f"Logo image not found at: {logo_path}")
            st.text(f"Working directory: {os.getcwd()}")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        pages = [
            st.page_link("streamlit_app.py", label="Home"),
            st.page_link("pages/1_NP_Database_Search.py", label="Database Search Engine"),
            st.page_link("pages/2_Tools.py", label="Tools"),
            st.page_link("pages/3_Related_Databases.py", label="Related Resources"),
            st.page_link("pages/5_Statistics.py", label="Statistics"),
            st.page_link("pages/4_Tutorials.py", label="Tutorials"),
            st.page_link("pages/6_Glossary.py", label="Glossary"),
            st.page_link("pages/7_FAQ.py", label="Frequently Asked Questions"),
            st.page_link("pages/8_Contact_Us.py", label="Contact Us"),
            st.page_link("pages/9_Submission.py", label="Submission"),
        ]
        st.markdown('</div>', unsafe_allow_html=True)


