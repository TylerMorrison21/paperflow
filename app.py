"""PDFReflow.ai — PDF to EPUB converter."""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from core.converter import convert_pdf_to_epub
from web.storage import save_upload

st.set_page_config(page_title="PDFReflow.ai", page_icon="📖")
st.title("PDFReflow.ai")
st.subheader("Convert any PDF to a Kindle-friendly EPUB")

uploaded = st.file_uploader("Upload a PDF", type="pdf")

if uploaded and st.button("Convert"):
    pdf_path = save_upload(uploaded)
    with st.spinner("Converting… this usually takes 1–3 minutes"):
        epub_path = convert_pdf_to_epub(pdf_path)
    with open(epub_path, "rb") as f:
        st.download_button("Download EPUB", f, file_name="converted.epub", mime="application/epub+zip")
