import streamlit as st
from sidebar import render_sidebar
import textwrap

# from utils.session_tracker import track_session
# track_session()


st.set_page_config(
    page_title="FAQ",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

# Helper to render one card
def render_card(faq):
    html = f"""
    <div style="
        background-color: #9e9ac8;
        border-radius: 10px;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        padding: 20px;
        display: flex;
        flex-direction: column;
        min-height: 400px;
        min-width: 330px;
    ">
      <!-- underline fixed at 50px down -->
      <div style="
          position: absolute;
          top: 100px;
          left: 80px;
          right: 0px;
          border-bottom: 3px solid black;
      "></div>

      <!-- Header -->
      <div style="
          display: flex;
          align-items: flex-start;
          gap: 10px;
          min-height: 70px;
          margin-top: 0;            /* no extra top margin */
      ">
        <div style="
            font-size: 55px;
            font-weight: bold;
            color: black;
            flex-shrink: 0;
        ">{faq['num']}</div>
        <div style="flex:1;">
          <!-- remove this inner border-bottom -->
          <div style="
              font-size: 22px;
              font-weight: bold;
              color: black;
              margin: 0;
              line-height: 25px;
          ">{faq['question']}</div>
        </div>
      </div>
      <!-- Answer -->
      <div style="
          position: absolute;
          top: 90px;
          flex: 1;
          font-size: 17px;
          line-height: 22px;
          color: #333;
          text-align: justify;
          text-justify: inter-word;
          overflow-y: auto;
          min-height: 0;
      ">
        {faq['answer'].replace('\n', '<br>')}
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- Helper: Render section of FAQs ---
def render_faq_section(section_title, faq_list):
    st.markdown(f'<h2 class="custom-title">{section_title}</h2>', unsafe_allow_html=True)
    for i in range(0, len(faq_list), 3):
        row = faq_list[i:i+3]
        cols = st.columns(3, gap="large")
        for col, faq in zip(cols, row):
            with col:
                render_card(faq)
        if i + 3 < len(faq_list):
            st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

general_faqs = [
    {
    "num": "01",
        "question": "Who can use cNPDB?",
        "answer": textwrap.dedent("""
            Researchers, students, neuroscientists, chemists, bioinformaticians, and drug discovery professionals should find cNPDB useful in many endeavors.
        """)
    },
    {
        "num": "02",
        "question": "How often is the database updated?",
        "answer": textwrap.dedent("""
            The database is maintained and updated yearly. Additionally, any new submissions/requests from the community will be addressed promtly upon receipt. 
        """)
    },
    {
    "num": "03",
        "question": "How to submit data, request new features, or report an error?",
        "answer": textwrap.dedent("""
            Please fill out the Feedback Form in the <i>Contact Us</i> page. For collaborations or urgent request, please contact Prof. Li directly at lingjun.li@wisc.edu.
        """)
    },
]

bio_faqs = [
    {
        "num": "01",
        "question": "What is the definition of neuropeptide?",
        "answer": textwrap.dedent("""
            While there are many controversial definitions, we consider a neuropeptide to be included in this database if it has the following characteristics:
            1. Must be synthesized and released by a neuron;
            2. Endogenous, small protein-like molecule composed of short chains of amino acids that function as signaling molecules in the nervous system;
            3. Derived from neuropeptide prohormones/precursors.
        """)
    },
]

search_faqs = [
    {
        "num": "01",
        "question": "How do I search for neuropeptides of interest in the cNPDB?",
        "answer": textwrap.dedent("""
            The Database Search Engine on the left allows users to search by specific sequence, family, organism, and other neuropepties. 
            Visit the <i>Tutorials</i> page for detailed instructions on how to use the search engine and download the results.
        """)
    },
    {
        "num": "02",
        "question": "What format of peptide sequence should I input?",
        "answer": textwrap.dedent("""
            Please input plain amino acid sequence without any PTMs. For example, AGHFMRFamide should be input as AGHFMRF.
        """)
    },
    {
        "num": "03",
        "question": "What do the physicochemical indexes represent?",
        "answer": textwrap.dedent("""
            For detailed explanations of each peptide property index, please visit the <i>Glossary</i> page under the <b>Tools</b> section.
        """)
    },
    {
    "num": "04",
        "question": "What do the terms “de novo,” “MS/MS,” and “predicted” mean?",
        "answer": textwrap.dedent("""
            These terms reflect the type of evidence supporting each neuropeptide in the database.
            1. <i>De novo</i>: Tentatively identified directly from MS/MS data once without prior reference.
            2. MS/MS: Confirmed by matching experimental MS/MS data to known neuropeptides in curated databases.
            3. Predicted: Inferred from bioinformatics tools like transcriptomics or gene annotation, without experimental validation.
        """)
    },
    {
    "num": "05",
        "question": "Can I download the whole database?",
        "answer": textwrap.dedent("""
            Yes! Just simply set the settings on the left side to be full ranges and don't input any strict criteria on the right settings. 
            Then hit the "Check all" and "Download FASTA File" buttons to download the whole cNPDB database.
        """)
    },
]

tool_faqs = [
    {
        "num": "01",
        "question": "What types of alignment are available?",
        "answer": textwrap.dedent("""
            1. Global Alignment aligns sequences from end to end (best for full-length comparisons).
            2. Local Alignment finds the most similar region within two sequences (useful for partial matches).
        """)
    },
    {
    "num": "02",
            "question": "What do the alignment settings mean?",
            "answer": textwrap.dedent("""
                For detailed explanations, visit the <i>Glossary</i> page under the <b>Tools</b> section. 
                Tip: Smaller or more negative gap penalties allow longer gaps.
        """)
    },
    {
    "num": "03",
            "question": "Can I align two sequences manually?",
            "answer": textwrap.dedent("""
                Yes! Paste your Query Sequence and Target Sequence to perform a direct pairwise alignment.
        """)
    },
    {
        "num": "04",
        "question": "Can I align my sequence against the cNPDB database?",
        "answer": textwrap.dedent("""
           Absolutely. Check the option "Align against the cNPDB database" to scan your peptide against all known sequences in the database and return the best matches.
        """)
    },
    {
        "num": "05",
        "question": "Can I download the search results?",
        "answer": textwrap.dedent("""
            Yes. Simply click on the "Download Alignment Results" buttons after perfoming your search to download the results in txt file.
        """)
    },
    # {
    #     "num": "05",
    #     "question": "What do the BLAST settings mean?",
    #     "answer": textwrap.dedent("""
    #         For detailed explanations, visit the <i>Glossary</i> page under the <b>Tools</b> section. 
    #     """)
    # },
    # {
    #     "num": "06",
    #     "question": "What is the difference between BLOSUM and PAM matrices?",
    #     "answer": textwrap.dedent("""
    #         Both are substitution matrices used to score alignments based on evolutionary similarity:
    #         1. BLOSUM (BLOcks SUbstitution Matrix): Based on observed substitutions in conserved protein regions.
    #         2. PAM (Point Accepted Mutation): Based on predicted mutations over evolutionary time.
    #     """)
    # },
    # {
    #     "num": "07",
    #     "question": "Which scoring matrix should I choose?",
    #     "answer": textwrap.dedent("""
    #         It's based on how closely related your sequences are.
    #         1. BLOSUM80: Closely related peptide sequences
    #         2. BLOSUM62: General use (default in many bioinformatics tools)
    #         3. BLOSUM45: More distantly related sequences
    #         4. PAM30: Short peptide alignments with high sensitivity
    #         5. PAM70: Moderately divergent sequences
    #     """)
    # },
]

# --- RENDER ALL SECTIONS ---
render_faq_section("GENERAL WEBSITE", general_faqs)
render_faq_section("BIOLOGICAL PERSPECTIVES", bio_faqs)
render_faq_section("SEARCH ENGINE", search_faqs)
render_faq_section("TOOLS", tool_faqs)

# footers
st.markdown("""
<div style="text-align: center; font-size:14px; color:#2a2541;">
  <em>Last update: Jul 2026</em>
</div>
""", unsafe_allow_html=True)

