import streamlit as st
import pdfplumber
import pandas as pd
import io

# 1. Custom Function for Girly Background and Flower Title
def add_girly_theme():
    st.markdown(
        f"""
        <style>
        /* Applies a girly pastel gradient to the entire app */
        .stApp {{
            background: linear-gradient(135deg, #FFB6C1, #E6E6FA, #FFB6C1); /* Pink to Lilac gradient */
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        
        /* Creates the solid white container so tables are easy to read */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.95); /* 95% solid white */
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            margin-top: 2rem;
            margin-bottom: 2rem;
        }}
        
        /* FORCES ALL TEXT TO BE BLACK */
        h1, h2, h3, h4, p, label, div, span, li {{
            color: black !important;
        }}
        
        /* Highlights the file uploader box in a soft pink */
        .stFileUploader {{
            border: 2px dashed #FF69B4 !important; /* Pink border */
            border-radius: 5px;
            padding: 10px;
            background-color: #f9f9f9 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 2. Page Configuration (using a flower icon here too)
st.set_page_config(page_title="Mariam's Flower App", layout="wide", page_icon="🌸")

# 3. Apply the custom theme (no photo required)
add_girly_theme()

# App Content with added flower icon
st.title("🌸 Mariam's App: PDF to Excel Extractor")
st.write("Welcome, Mariam! 🌿 Upload your pharmacy studies PDF to instantly extract tables and search through data.")

# 4. File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.info("Extracting tables... Please wait.")
    
    all_data = []
    
    try:
        # 5. Extract Data
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_data.extend(table)
                    
        # 6. Process Data
        if all_data:
            # Create the DataFrame
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            st.success("Extraction complete! 💐")
            
            # 7. Show the Full Extracted Data
            st.subheader("📋 Full Extracted Table")
            st.dataframe(df, use_container_width=True)
            
            # 8. SEARCH BAR
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
            
            # 9. Prepare EXCEL for Download
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
        st.error(f"An error occurred during extraction. Make sure the PDF layout is supported. Error details: {e}")
