import streamlit as st
import pdfplumber
import pandas as pd
import io

# Set up a wider layout for better table viewing
st.set_page_config(page_title="PDF to Excel Extractor", layout="wide")
st.title("📄 PDF to Excel Extractor")
st.write("Upload a PDF, preview it interactively, and download a fully searchable Excel file.")

# 1. File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.info("Extracting tables... Please wait.")
    
    all_data = []
    
    try:
        # 2. Extract Data
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_data.extend(table)
                    
        # 3. Process Data
        if all_data:
            # Create the DataFrame
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            st.success("Extraction complete!")
            
            # 4. Interactive Preview
            # st.dataframe natively allows users to click, scroll, and search inside the app!
            st.subheader("Interactive Data Preview")
            st.dataframe(df, use_container_width=True)
            
            # 5. Prepare EXCEL for Download
            # We use a memory buffer so we don't have to save a physical file to your hard drive first
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Extracted Data')
            
            # Download Button for the Excel file
            st.download_button(
                label="📥 Download as Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name="extracted_tables.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No tables could be found in this PDF.")
            
    except Exception as e:
        st.error(f"An error occurred during extraction: {e}")
