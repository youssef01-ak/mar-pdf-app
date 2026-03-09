import streamlit as st
import pdfplumber
import pandas as pd
import io

# 1. Page Configuration
st.set_page_config(page_title="Mariam's Flower App", layout="wide", page_icon="🌸")

# 2. Add custom CSS to force the uploader box to be pink and text black
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');

    .stApp {
        background: linear-gradient(135deg, #FFB6C1, #E6E6FA, #FFB6C1) !important;
        font-family: 'Quicksand', sans-serif;
    }

    /* NUCLEAR OPTION - force every possible uploader selector */
    [data-testid="stFileUploadDropzone"],
    [data-testid="stFileUploadDropzone"] > div,
    section[data-testid="stFileUploadDropzone"],
    .stFileUploader > div,
    .uploadedFile,
    div[class*="uploadDropzone"],
    div[class*="FileUpload"] {
        background-color: rgba(255, 182, 193, 0.7) !important;
        background: rgba(255, 182, 193, 0.7) !important;
        border: 2px dashed #FF69B4 !important;
        border-radius: 16px !important;
        color: #5a0030 !important;
    }

    /* Force ALL text inside uploader pink/dark */
    [data-testid="stFileUploadDropzone"] *,
    [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] small {
        color: #5a0030 !important;
        background: transparent !important;
    }

    /* Force icon color */
    [data-testid="stFileUploadDropzone"] svg,
    [data-testid="stFileUploadDropzone"] svg path {
        fill: #FF1493 !important;
        stroke: #FF1493 !important;
        color: #FF1493 !important;
    }

    /* Browse files button */
    [data-testid="stFileUploadDropzone"] button,
    [data-testid="stBaseButton-secondary"] {
        background-color: rgba(255,105,180,0.4) !important;
        color: #5a0030 !important;
        border: 1px solid #FF69B4 !important;
        border-radius: 8px !important;
    }

    h1, h2, h3, p, label { color: #5a0030 !important; }

    /* WALKING CAT */
    .cat-walk-container {
        position: relative;
        width: 100%;
        height: 40px;
        margin-bottom: -12px;
        overflow: hidden;
        z-index: 9999;
        pointer-events: none;
    }
    .walking-cat {
        position: absolute;
        font-size: 2rem;
        bottom: 0px;
        animation: walkAcross 12s linear infinite;
    }
    @keyframes walkAcross {
        0%   { left: -60px;  transform: scaleX(1);  }
        49%  { left: 103%;   transform: scaleX(1);  }
        50%  { left: 103%;   transform: scaleX(-1); }
        100% { left: -60px;  transform: scaleX(-1); }
    }
    .walking-cat span {
        display: inline-block;
        animation: wobble 0.4s ease-in-out infinite alternate;
    }
    @keyframes wobble {
        0%   { transform: translateY(0px); }
        100% { transform: translateY(-4px); }
    }
    </style>

    <div class="cat-walk-container">
      <div class="walking-cat"><span>🐱</span></div>
    </div>
    """,
    unsafe_allow_html=True
)
# App Content
st.title("🌸 Mariam's App: PDF to Excel Extractor")
st.write("Welcome, Mariam! 🌿 Upload your pharmacy studies PDF to instantly extract tables and search through data.")

# 3. File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.info("Extracting tables... Please wait.")
    
    all_data = []
    
    try:
        # 4. Extract Data
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_data.extend(table)
                    
        # 5. Process Data
        if all_data:
            # Create the DataFrame
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            st.success("Extraction complete! 💐")
            
            # 6. Show the Full Extracted Data
            st.subheader("📋 Full Extracted Table")
            st.dataframe(df, use_container_width=True)
            
            # 7. SEARCH BAR
            st.subheader("🔍 Search by Name or Ingredient")
            search_query = st.text_input("Type here to search (e.g., 'Paracetamol'):")
            
            # Filter the DataFrame
            if search_query:
                mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
                filtered_df = df[mask]
                st.write(f"**Found {len(filtered_df)} matching rows for '{search_query}'.**")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                filtered_df = df
            
            # 8. Prepare EXCEL for Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Mariams Data')
            
            # Download Button
            st.download_button(
                label="📥 Download Search Results as Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name="Mariams_Study_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No tables could be found in this PDF. Please check if it's a scanned image.")
            
    except Exception as e:
        st.error(f"An error occurred during extraction. Error details: {e}")
