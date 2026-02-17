"""PDFReflow.ai — Streamlit entry point."""

import streamlit as st
from core.converter import convert_pdf_to_epub
from web.storage import save_upload, get_output_path

st.set_page_config(page_title="PDFReflow.ai", page_icon="📖")

st.title("PDFReflow.ai")
st.subheader("Turn scanned PDFs into perfect Kindle EPUBs")

uploaded = st.file_uploader("Upload your scanned PDF", type="pdf")
col_type = st.radio("Layout", ["Single column", "Two columns"])

if uploaded and st.button("Convert — $3"):
    pdf_path = save_upload(uploaded)
    with st.spinner("Converting... (usually 2-5 min)"):
        epub_path = convert_pdf_to_epub(pdf_path, col_type)
    with open(epub_path, "rb") as f:
        st.download_button("Download EPUB", f, file_name="converted.epub")
