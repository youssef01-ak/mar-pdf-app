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
        background: linear-gradient(135deg, #FFB6C1, #E6E6FA, #FFB6C1);
        background-attachment: fixed;
        background-size: cover;
        font-family: 'Quicksand', sans-serif;
    }

    /* PINK TRANSPARENT UPLOADER */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(255, 182, 193, 0.45) !important;
        border: 2px dashed #FF69B4 !important;
        border-radius: 16px !important;
        backdrop-filter: blur(8px) !important;
        position: relative !important;
        overflow: visible !important;
        transition: background 0.3s ease !important;
    }

    [data-testid="stFileUploadDropzone"]:hover {
        background: rgba(255, 105, 180, 0.35) !important;
    }

    [data-testid="stFileUploadDropzone"] * {
        color: #5a0030 !important;
    }

    [data-testid="stFileUploadDropzone"] svg {
        fill: #FF1493 !important;
    }

    [data-testid="stFileUploadDropzone"] button {
        background-color: rgba(255,105,180,0.3) !important;
        color: #5a0030 !important;
        border: 1px solid #FF69B4 !important;
        border-radius: 8px !important;
    }

    [data-testid="stFileUploadDropzone"] button:hover {
        background-color: #FF69B4 !important;
        color: white !important;
    }

    /* CAT CONTAINER — sits on top of the uploader */
    .cat-wrapper {
        position: relative;
        width: 100%;
    }

    .jumping-cat {
        position: absolute;
        top: -60px;
        right: 30px;
        font-size: 2.4rem;
        animation: catJump 1.2s ease-in-out infinite;
        z-index: 9999;
        filter: drop-shadow(0 4px 6px rgba(255,20,147,0.3));
        pointer-events: none;
        user-select: none;
    }

    @keyframes catJump {
        0%   { transform: translateY(0px) rotate(-5deg); }
        30%  { transform: translateY(-28px) rotate(5deg); }
        50%  { transform: translateY(-38px) rotate(0deg); }
        70%  { transform: translateY(-28px) rotate(-3deg); }
        100% { transform: translateY(0px) rotate(-5deg); }
    }

    /* DATAFRAME */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        background-color: rgba(255, 240, 245, 0.7) !important;
        border-radius: 12px !important;
    }

    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span {
        color: black !important;
    }

    h1, h2, h3, p {
        color: #5a0030 !important;
    }
    </style>

    <!-- Jumping cat riding above the uploader -->
    <div style="position:relative; height:0;">
      <div class="jumping-cat">🐱</div>
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
