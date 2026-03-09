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
    /* Gradient background for the whole page */
    .stApp {
        background: linear-gradient(135deg, #FFB6C1, #E6E6FA, #FFB6C1); /* Pink to Lilac */
        background-attachment: fixed;
        background-size: cover;
    }
    
    /* TARGET THE INNER UPLOAD DROPZONE TO BE PINK */
    [data-testid="stFileUploadDropzone"] {
        background-color: #FFB6C1 !important; /* Soft pink background */
        border: 2px dashed #FF1493 !important; /* Deeper pink border */
        border-radius: 10px;
    }

    /* FORCE ALL TEXT INSIDE THE UPLOADER TO BE BLACK */
    [data-testid="stFileUploadDropzone"] * {
        color: black !important;
    }

    /* FORCE THE CLOUD ICON TO BE BLACK */
    [data-testid="stFileUploadDropzone"] svg {
        fill: black !important;
        color: black !important;
    }

    /* FIX THE "BROWSE FILES" BUTTON */
    [data-testid="stFileUploadDropzone"] button {
        background-color: transparent !important;
        color: black !important;
        border: 1px solid black !important;
    }
    [data-testid="stFileUploadDropzone"] button:hover {
        background-color: #FF69B4 !important; /* Hot pink when hovering */
        color: white !important;
        border: 1px solid #FF69B4 !important;
    }

    /* Target the data table that appears later */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        background-color: #FFF0F5 !important; /* Very light pink/white background for data */
    }
    
    /* Target text elements within the dataframe to ensure black text */
    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span, [data-testid="stDataFrame"] a {
        color: black !important;
    }
    
    /* Ensure main headers are black */
    h1, h2, h3, p {
        color: black !important;
    }
    </style>
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
