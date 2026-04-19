import streamlit as st
from PIL import Image
import os
import base64
from sidebar import render_sidebar

from utils.session_tracker import track_session
track_session()


st.set_page_config(
    page_title="Contact Us",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

col1, col2 = st.columns([1, 3], gap="medium")
with col1:
    headshot = os.path.join("Assets", "Img", "PIHeadshot.jpg")
    if os.path.exists(headshot):
        st.image(headshot, use_container_width=True)
    else:
        st.error(f"Profile image not found at:\n{headshot}")

with col2:
    st.markdown("""
    <div style="line-height:1.0;">
      <h2 style="margin:0 0 0.25rem 0;">Lingjun Li, Ph.D.</h2>
      <p style="margin:0 0 1rem 0;"><strong>Charles Melbourne Johnson Distinguished Chair in Pharmaceutical Sciences</strong></p>
      <p style="margin:0 0 1rem 0;"><strong>Vilas Distinguished Achievement Professor of Pharmaceutical Sciences and Chemistry</strong></p>
      <p style="margin:0 0 1rem 0;">School of Pharmacy and Department of Chemistry</p>
      <p style="margin:0 0 1rem 0;">University of Wisconsin – Madison</p>
      <p style="margin:0 0 1rem 0;">Madison, WI 53705, USA</p>
      <p style="margin:0 0 1rem 0;"><strong>Phone:</strong> +1 (608) 265-8491</p>
      <p style="margin:0;"><strong>Email:</strong> <a href="mailto:lingjun.li@wisc.edu">lingjun.li@wisc.edu</a></p>
    </div>
    """, unsafe_allow_html=True)


# ─── Opportunities ────────────────────────────────────────────────────────
st.markdown("### OPPORTUNITIES")
st.markdown("""
<div style="text-align: justify; text-justify: inter-word;">
  <p style="margin-bottom: 0.8em;">
    Join our research efforts! We are continuously expanding this database and welcome contributions from students and postdoctoral fellows with fellowships or scholarships.
  </p>
  <p style="margin-bottom: 0.8em;">
    If you’re interested in advancing neuropeptide research or initiating collaborations, please reach out to Prof. Li at <a href="mailto:lingjun.li@wisc.edu">lingjun.li@wisc.edu</a>.
  </p>
  <p style="margin-bottom: 0.8em;">
    If you want to submit new data to cNPDB, report an error, request new features and suggestions, or have any trouble accessing this database, please fill out the Submission Form under the <i>Submission</i> page.
  </p>
</div>
""", unsafe_allow_html=True)

# ─── Publications Grid ───────────────────────────────────────────────────
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
        "img": "Assets/Publication_TOC/DecodingNeuropeptideComplexity.jpeg",
        "title": "Decoding Neuropeptide Complexity: Advancing Neurobiological Insights from Invertebrates to Vertebrates through Evolutionary Perspectives",
        "summary": (
            "The complex vertebrate neural networks poses significant challenges for neuropeptide functional studies. Invertebrate models "
            "offer simplified neural circuits for uncovering fundamental biological principles and their relevance to vertebrate systems."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acschemneuro.5c00053"
    },
    {
        "img": "Assets/Publication_TOC/Gaoyuan AmericanLobster TOC.jpeg",
        "title": "Neuropeptidomics of the American Lobster",
        "summary": (
            "Leveraging the recently sequenced high-quality draft genome of the American lobster, "
            "our study sought to profile the neuropeptidome of this model organism. "
            "We identified 24 neuropeptide precursors and 101 unique mature neuropeptides."
        ),
        "link": "https://pubs.acs.org/doi/10.1021/jasms.4c00192"
    },
     {
        "img": "Assets/Publication_TOC/UpdatedGuideNeuropeptideProcess.jpeg",
        "title": "An Updated Guide to the Identification, Quantitation, and Imaging of the Crustacean Neuropeptidome",
        "summary": (
            "A general workflow and detailed multi-faceted approaches for MS-based neuropeptidomic analysis of crustacean tissue samples and circulating fluids."
        ),
        "link": "https://link.springer.com/protocol/10.1007/978-1-0716-3646-6_14"
    },
    {
        "img": "Assets/Publication_TOC/Endogenius TOC.png",
        "title": "EndoGenius: Optimized Neuropeptide Identification from Mass Spectrometry Datasets",
        "summary": (
            "EndoGenius leverages optimized peptide–spectrum matching, an expansive motif database, "
            "and a novel scoring algorithm to broaden neuropeptidome coverage and minimize re-identification."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acs.jproteome.3c00758"
    },
    {
        "img": "Assets/Publication_TOC/Quantitative MS.png",
        "title": "Quantitative neuropeptide analysis by mass spectrometry: advancing methodologies for biological discovery",
        "summary": (
            "This review highlights how strategies in label-free and label-based quantitation, tandem MS "
            "acquisition, and mass spectrometry imaging provide unprecedented sensitivity and throughput for capturing the landscape of neuropeptides and their PTMs."
        ),
        "link": "https://pubs.rsc.org/en/content/articlelanding/2025/cb/d5cb00082c"
    },
    {
        "img": "Assets/Publication_TOC/AcuteCocaine.jpeg",
        "title": "Cocaine-Induced Remodeling of the Rat Brain Peptidome: Quantitative MS Reveals Anatomically Specific Patterns of Cocaine-Regulated Peptide Changes",
        "summary": (
            "Mass spectrometry (MS) methods were employed to characterize acute cocaine-induced peptidomic changes in the rat brain, "
            "paving the way for developing new therapies to treat substance use disorders and related psychiatric conditions."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acschemneuro.4c00327"
    },
    {
        "img": "Assets/Publication_TOC/PTSD.jpeg",
        "title": "Global Neuropeptidome Profiling in Response to Predator Stress in Rat: Implications for Post-Traumatic Stress Disorder",
        "summary": (
            "Mass spectrometry (MS)-based qualitative and quantitative analytical strategies to determine peptidomic alterations in rats exposed to "
            "predator odor (an ethologically relevant analogue of trauma-like stress)"
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/jasms.3c00027"
    },
    {
        "img": "Assets/Publication_TOC/GlycosylationBlueCrab.jpeg",
        "title": "Enrichment and fragmentation approaches for enhanced detection and characterization of endogenous glycosylated neuropeptides",
        "summary": (
            "The use of hydrophilic interaction liquid chromatography (HILIC) enrichment and different fragmentation methods to probe the "
            "expression of glycosylated neuropeptides in blue crab, Callinectes sapidus"
        ),
        "link": "https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/abs/10.1002/pmic.202100375"
    },
    {
        "img": "Assets/Publication_TOC/FeedingHemolymphDIA.jpeg",
        "title": "MS profiling and quantitation of changes in circulating hormones secreted over time in C.borealis hemolymph due to feeding behavior",
        "summary": (
            "A data-independent acquisition (DIA) MS method was implemented to profile neuropeptides at different stages of the feeding process,"
            " including hemolymph from crabs that were unfed, or 0 min, 15 min, 1 h, and 2 h post-feeding"
        ),
        "link": "https://link.springer.com/article/10.1007/s00216-021-03479-1"
    },
    {
        "img": "Assets/Publication_TOC/SexualDimorphismNP.jpeg",
        "title": "Exploring the Sexual Dimorphism of Crustacean Neuropeptide Expression Using Callinectes sapidus as a Model Organism",
        "summary": (
            "Studying the variation of neuropeptidomic profiles between males and females in a crustacean model organism "
            "by using high-resolution mass spectrometry with two complementary ionization sources and quantitative chemical labeling"
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acs.jproteome.1c00023"
    },
    {
        "img": "Assets/Publication_TOC/CopperToxicity.jpeg",
        "title": "Mass Spectrometric Profiling of Neuropeptides in Response to Copper Toxicity via Isobaric Tagging",
        "summary": (
            "This study incorporates custom N,N-dimethyl leucine isobaric tags to characterize the neuropeptidomic changes after "
            "different time points (1, 2, and 4 h) of copper exposure in a model organism, blue crab, Callinectes sapidus."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acs.chemrestox.0c00521"
    },
    {
        "img": "Assets/Publication_TOC/FeedingHemolymph.jpeg",
        "title": "Mass Spectrometry Quantification, Localization, and Discovery of Feeding-Related Neuropeptides in Cancer borealis",
        "summary": (
            "A multifaceted mass spectrometry (MS) method to identify neuropeptides that differentiate the unfed and fed states."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acschemneuro.1c00007"
    },
    {
        "img": "Assets/Publication_TOC/Hypoxia.jpeg",
        "title": "Mass Spectrometric Profiling of Neuropeptides in Callinectes sapidus during Hypoxia Stress",
        "summary": (
            "Beyond being a neurological model organism, crustaceans are regularly exposed to hypoxia (low O2 levels). "
             "This study revealed that neuropeptides play a critical role in how crustaceans adapt due to hypoxic stress."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acschemneuro.0c00439"
    },
    {
        "img": "Assets/Publication_TOC/oxoniumiontriggeredEThCD.jpeg",
        "title": "Signature-Ion-Triggered MS Approach Enabled Discovery of N- and O-Linked Glycosylated Neuropeptides in the Crustacean Nervous System",
        "summary": (
            "The hybrid oxonium ion-triggered EThcD approach, coupling a shotgun method for neuropeptide discovery and targeted strategy for glycosylation characterization, "
            "enables the first report on glycosylated neuropeptides in crustaceans and the discovery of additional neuropeptides simultaneously."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acs.jproteome.9b00525"
    },
    {
        "img": "Assets/Publication_TOC/pHStress.jpeg",
        "title": "Multifaceted Mass Spectrometric Investigation of Neuropeptide Changes in Atlantic Blue Crab, Callinectes sapidus, in Response to Low pH Stress",
        "summary": (
            "To understand the modulatory function of neuropeptides in crustaceans when encountering drops in pH level, we developed and implemented a multifaceted "
            "mass spectrometric platform to investigate the global neuropeptide changes in response to water acidification in the Atlantic blue crab."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acs.jproteome.9b00026"
    },
    {
        "img": "Assets/Publication_TOC/HabenularNuclei.jpeg",
        "title": "Neuropeptidomics of the Rat Habenular Nuclei",
        "summary": (
            "Conserved across vertebrates, the habenular nuclei are a pair of small symmetrical structures in the epithalamus. "
            " These subnuclei are associated with different physiological processes and disorders, such as depression, nicotine addiction, and encoding aversive stimuli or omitting expected rewarding stimuli."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acs.jproteome.7b00811"
    },
    {
        "img": "Assets/Publication_TOC/Feeding2crab.jpeg",
        "title": "A Multifaceted Mass Spectrometric Method to Probe Feeding Related Neuropeptide Changes in Callinectes sapidus and Carcinus maenas",
        "summary": (
            "We reported a comparative neuropeptidomic analysis of the brain and pericardial organ in response to feeding in two well-studied "
            "crustacean physiology model organisms, Callinectes sapidus and Carcinus maenas, using mass spectrometry techniques."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1007/s13361-017-1888-4"
    },
    {
        "img": "Assets/Publication_TOC/LobsterDevelopmental.jpeg",
        "title": "Relative Quantitation of Neuropeptides at Multiple Developmental Stages of the American Lobster Using N,N-Dimethyl Leucine Isobaric Tandem Mass Tags",
        "summary": (
            "With reduced cost and higher labeling efficiency, we employed custom-developed N,N-dimethyl leucine (DiLeu) 4-plex isobaric tandem mass tags "
            "for the relative quantitation of neuropeptides in brain tissue of American lobster Homarus americanus at multiple developmental stages."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/acschemneuro.7b00521"
    },
    {
        "img": "Assets/Publication_TOC/FeedingRat.jpg",
        "title": "Quantitative MS Reveals Food Intake-Induced Neuropeptide Level Changes in Rat Brain: Functional Assessment of Neuropeptides as Feeding Regulators",
        "summary": (
            "To monitor neuropeptidomic changes in response to food intake in the rat nucleus accumbens (NAc), we employed "
            "cryostat dissection, heat stabilization, neuropeptide extraction and label-free quantitative neuropeptidomics via LC-MS platform."
        ),
        "link": "https://www.sciencedirect.com/science/article/pii/S1535947620323276"
    },
    {
        "img": "Assets/Publication_TOC/Temperature.jpeg",
        "title": "Quantitative Neuropeptidomics Study of the Effects of Temperature Change in the Crab Cancer borealis",
        "summary": (
            "We employed a MS-based approach to investigate the neuropeptide changes associated with "
            "acute temperature elevation in three neural tissues from the Jonah crab Cancer borealis. "
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/pr500742q"
    },
    {
        "img": "Assets/Publication_TOC/DIAMicrodialysis.jpeg",
        "title": "Data-Independent MS/MS Quantification of Neuropeptides for Determination of Putative Feeding-Related Neurohormones in Microdialysate",
        "summary": (
            "An untargeted DIA MSE quantification method using Skyline software for multiplexed, discovery-driven "
            "relative quantification of the crab Cancer borealis neuropeptidome was possible in microdialysates from 8 replicate feeding experiments"
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/cn500253u"
    },
    {
        "img": "Assets/Publication_TOC/AffinityMicrodialysis.jpeg",
        "title": "Mass Spectrometric Detection of Neuropeptides Using Affinity-Enhanced Microdialysis with Antibody-Coated Magnetic Nanoparticles",
        "summary": (
            "A variety of affinity agents have been investigated for Affinity-enhanced microdialysis (AE-MD) of neuropeptides in vitro and in vivo,  "
            "including particles with C18 surface functionality and antibody-coated particles."
        ),
        "link": "https://pubs.acs.org/doi/full/10.1021/ac302403e?casa_token=ftr79hnHFdUAAAAA%3AO0hUliSWMkexOmTorrV7pj9HAPIIvABMww14dKH5loTsXJSSyvaRyUzMiqZMzrKkRyd1QCkM6pm0C7k"
    },
]

st.markdown("### PI’s MAIN PUBLICATIONS ON NEUROPEPTIDES")

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
                    padding: 15px;
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
                    height: 85px;
                    overflow: hidden;
                    margin-bottom: 0px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                  ">
                    <h3 style="
                        color: #29004c;
                        margin: 10px 0 0 0;
                        text-align: center;
                        font-size: 1em;
                        line-height: 1.2;
                    ">{p["title"]}</h3>
                  </div>
                  
                  <div style="
                     flex: 1;
                      color: #555;
                      font-size: 0.9em;
                      line-height: 1.4;
                      margin: 5px 0 5px 0;
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

# ─── Footer ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; font-size: 14px; color: #2a2541;">
  <em>Last update: Apr 2026</em>
</div>
""", unsafe_allow_html=True)
