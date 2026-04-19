import streamlit as st
from sidebar import render_sidebar
import base64
import os
import streamlit.components.v1 as components

from utils.session_tracker import track_session
track_session()

st.set_page_config(
    page_title="Related Databases",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

# --- Section 1: Table of External Databases ---
st.markdown("""
<style>
 /* 1) Centered title with10px top margin */
  h2.custom-title {
    text-align: center !important;
    margin-top: 0px !important;
    color: #29004c;
  }

  /* 2) Wrapper with border and rounded corners */
  .table-wrapper {
    border: 0.5px solid #29004c;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 0;
    margin-bottom: 0;
    display: block;
  }

  /* 3) Inner table */
  .related-table table {
    width: 100%;
    border-collapse: collapse;     
    margin-bottom: 0 !important;
    border: none;
  }

  /* 4) Cell padding */
  .related-table th,
  .related-table td {
  padding: 10px;
  }

  /* 5) Header row styling */
  .related-table th {
    background-color: #9e9ac8;
    text-align: center;
    font-weight: bold;
    border: 2px solid #29004c;
  }

  /* 6) Vertical separators between header cells */
  .related-table th + th {
    border: 2px solid #29004c;
  }

  /* 7) Vertical separators between body cells */
  .related-table td + td {
    border: 2px solid #29004c;
  }

  /* Add Left Border to First Column */
  .related-table td:first-child,
  .related-table th:first-child {
  border-left: 2px solid #29004c;
  }


  /* 8) Horizontal separators between rows */
  .related-table tr + tr {
    border: 2px solid #29004c;
    padding: 10px;
  }

  /* 9) Link styling */
  .related-table a {
    color: #29004c;
    text-decoration: none;
    font-weight: bold;
  }
  .related-table a:hover {
    text-decoration: underline;
  }
/* Add this new rule to center the Year Published column */
  .related-table td:nth-child(2),
  .related-table th:nth-child(2) {
    text-align: center !important;
  }
  
</style>
""", unsafe_allow_html=True)

# --- Centered, spaced title ---
st.markdown(
    '<h2 class="custom-title">'
    'ACCESSIBLE NEUROPEPTIDE DATABASES'
    '</h2>',
    unsafe_allow_html=True
)

# --- Your table HTML unchanged except for class name ---
st.markdown("""
<div class="table-wrapper">
    <div class="related-table">
      <table>
        <thead>
          <tr>
            <th>Website</th>
            <th>Year Published</th>
            <th>Database Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="http://stagbeetle.animal.uiuc.edu/cgi-bin/neuropred.py" target="_blank">NeuroPred</a></td>
            <td>2006</td>
            <td>NeuroPred contains genome-derived neuropeptides precursors for many invertebrates and vertebrates</td>
          </tr>
          <tr>
            <td><a href="http://neuropeptides.nl" target="_blank">neuropeptides.nl</a></td>
            <td>2010</td>
            <td>A curated collection of neuropeptide genes, precursor proteins, and processed peptide information, including links to genomic and 
            transcriptomic databases, structural data, and brain expression details</td>
          </tr>
          <tr>
            <td><a href="https://academic.oup.com/bioinformatics/article/27/19/2772/230751?login=false" target="_blank">NeuroPedia</a></td>
            <td>2011</td>
            <td>A neuropeptide encyclopedia of peptide sequences (including genomic and taxonomic information) and spectral libraries of identified MS/MS spectra of homolog neuropeptides from multiple species</td>
          </tr>
          <tr>
            <td><a href="http://www.isyslab.info/NeuroPepV2/home.jsp" target="_blank">NeuroPep</a></td>
            <td>2015, 2023</td>
            <td>NeuroPep holds 5949 non-redundant neuropeptide entries originating from 493 organisms belonging to 65 neuropeptide families.</td>
          </tr>
          <tr>
            <td><a href="https://neurostresspep.eu/diner/insectneuropeptides" target="_blank">DINeR</a></td>
            <td>2017</td>
            <td>A tailored database for insect neuropeptide research</td>
          </tr>
        </tbody>
      </table>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Section 2: resources for neuropeptide research ---
st.markdown(
    '<h2 class="custom-title">'
    'RESOURCES FOR NEUROPEPTIDE RESEARCH'
    '</h2>',
    unsafe_allow_html=True
)

# --- inject custom CSS for TOC images ---
st.markdown("""
<style>
/* White background block for TOC images */
.resource-item .toc-container {
    background-color: white;
    padding: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 190px; /* Fixed height for TOC container */
    margin-bottom: 0px;
}
</style>
""", unsafe_allow_html=True)

# --- helper to load an image as base64 ---
def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- your paper data ---
papers = [
    {
        "img": os.path.join("Assets", "Publication_TOC", "Endogenius TOC.png"),
        "title": "Endogenius",
        "summary": (
            "EndoGenius is designed specifically for "
            "neuropeptide identifications from mass spectra by leveraging optimized peptide–spectrum "
            "matching approaches, an expansive motif database, and a novel scoring algorithm to "
            "achieve broader representation of the neuropeptidome and minimize reidentification."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acs.jproteome.3c00758",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "MotifQuest TOC.jpeg"),
        "title": "MotifQuest",
        "summary": (
            "MotifQuest, our novel motif database generation algorithm, is designed to work in partnership "
            "with EndoGenius – a program optimized for database searching of endogenous peptides – and is "
            "powered by a motif database to capitalize on biological context for confident identifications."
        ),
        "link": "https://pubs.acs.org/doi/10.1021/jasms.4c00192",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "Crustacean DIA dataset.jpg"),
        "title": "Crustacean DIA Spectral Library",
        "summary": (
            "With spectral libraries serving as a means to interpret DIA-MS output spectra, "
            "and Cancer borealis as a model of choice for neuropeptide analysis, we performed the first spectral library mapping of crustacean neuropeptides. "
            "The library is comprised of 333 unique neuropeptides."
        ),
        "link": "https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/pmic.202300285",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "HyPep.jpeg"),
        "title": "HyPep",
        "summary": (
            "HyPep utilizes sequence homology searching for peptide identification."
            "HyPep aligns de novo sequenced peptides, generated through PEAKS software, with neuropeptide database sequences and identifies neuropeptides based on the alignment score."
        ),
        "link": "https://pubs.acs.org/doi/abs/10.1021/acs.jproteome.2c00597",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "PRESnovo.jpeg"),
        "title": "PRESnovo",
        "summary": (
            "PRESnovo (prescreening precursors prior to de novo sequencing) is designed to predict the neuropeptide motif from a MS/MS spectrum"
            " to improve accuracy and sensitivity of neuropeptide identification"
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/jasms.0c00013",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "NeuropredPLM.jpeg"),
        "title": "NeuroPred-PLM",
        "summary": (
            "A machine learning-based tool that predicts whether a peptide is a neuropeptide using protein language model "
            "embeddings and convolutional neural networks. Available as a Python package and through a web interface for easy use."
        ),
        "link": "https://academic.oup.com/bib/article/24/2/bbad077/7073964",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "SignalP6.jpeg"),
        "title": "SignalP - 6.0",
        "summary": (
            "A deep learning-based tool that predicts the presence and cleavage sites of signal peptides in protein sequences. "
            "It helps identify peptides likely to be secreted, making it especially useful for discovering and filtering neuropeptide prohormone "
            "precursors from whole-proteome datasets."
        ),
        "link": "https://www.nature.com/articles/s41587-021-01156-3",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "BLAST.png"),
        "title": "BLAST",
        "summary": (
            "Compare a peptide sequence against a vast database of known proteins. This helps identify homologous or functionally similar sequences " 
            "across species, providing insights into evolutionary conservation or potential functions of novel peptides."
        ),
        "link": "https://blast.ncbi.nlm.nih.gov/Blast.cgi",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "ClustalOmega.jpeg"),
        "title": "Clustal Omega",
        "summary": (
            "A tool for multiple sequence alignment. It helps align candidate peptides with known neuropeptides across species to find functional similarities, "
            "conserved motifs, patterns, or evolutionary relationships."
        ),
        "link": "https://doi.org/10.1002/pro.3290",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "AlphaFold3.jpg"),
        "title": "AlphaFold3",
        "summary": (
            "Structure predictions for proteins and peptides based on their amino acid sequence. AlphaFold can help visualize the 3D structure of "
            "neuropeptides or their prohormone precursors, offering insights into functional domains, receptor binding, or PTM sites."
        ),
        "link": "https://www.nature.com/articles/s41586-024-07487-w",
    },
    {
        "img": os.path.join("Assets", "Publication_TOC", "ESMFold.png"),
        "title": "ESMFold",
        "summary": (
            "Fast, end-to-end protein structure prediction model developed by Meta AI, based on large-scale transformer language models trained on protein sequences."
            "ESMFold predicts 3D structures directly from single sequences, making it significantly faster and suitable for large-scale or real-time applications "
            "with limited evolutionary data."
        ),
        "link": "https://www.science.org/doi/abs/10.1126/science.ade2574",
    },
   ]

# create three equal columns
# create three equal columns
from math import ceil

# display papers in rows of 3
num_columns = 3
num_rows = ceil(len(papers) / num_columns)

for row_index in range(num_rows):
    cols = st.columns(num_columns, gap="medium")
    for col_index in range(num_columns):
        paper_index = row_index * num_columns + col_index
        if paper_index < len(papers):
            p = papers[paper_index]
            b64 = img_b64(p["img"])
            with cols[col_index]:
                st.markdown(f"""
                <div style="
                    background-color: #9e9ac8;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    min-height: 490px;
                ">
                  <div class="resource-item">
                    <div class="toc-container">
                      <img src="data:image/png;base64,{b64}"
                           style="max-height:100%; width:auto; object-fit:contain; border-radius:5px;" />
                    </div>
                  </div>

                  <div style="
                    height: 50px;
                    overflow: hidden;
                    margin-bottom: 0px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                  ">
                    <h3 style="
                        color: #29004c;
                        margin: 0 0 0 0;
                        text-align: center;
                        font-size: 1.15em;
                        line-height: 1.2;
                    ">{p["title"]}</h3>
                  </div>
                  
                  <div style="
                     flex: 1;
                      color: #555;
                      font-size: 0.9em;
                      line-height: 1.4;
                      margin: 0 0 0 0;
                      overflow: auto;
                      text-align: left;
                  ">
                    {p["summary"]}
                  </div>

                  <div style="
                      height: 45px;
                      flex-shrink: 0;
                      display: flex;
                      justify-content: center;
                      align-items: center;
                  ">
                    <a href="{p["link"]}" target="_blank" style="
                        background-color: #29004c;
                        color: white;
                        text-decoration: none;
                        padding: 8px 16px;
                        border-radius: 5px;
                        font-size: 0.9em;
                    ">Read More</a>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; font-size:14px; color:#2a2541;">
  <em>Last update: Apr 2026</em>
</div>
""", unsafe_allow_html=True)

