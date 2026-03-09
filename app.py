import streamlit as st
import pdfplumber
import pandas as pd
import io

# 1. Custom Function to add background image and style elements
def add_pharmacy_theme(url):
    st.markdown(
        f"""
        <style>
        /* This applies the background image to the entire app */
        .stApp {{
            background-image: url("{url}");
            background-attachment: fixed;
            background-size: cover;
        }}
        
        /* This makes the central content area easier to read */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.9); /* White with 90% opacity */
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 2rem;
            margin-bottom: 2rem;
        }}
        
        /* Custom green colors for titles to match pharmacy theme */
        h1, h2, h3, h4 {{
            color: #1a531a; /* Dark green */
        }}
        
        /* Make the file uploader stand out slightly */
        .stFileUploader {{
            border: 2px dashed #4CAF50;
            border-radius: 5px;
            padding: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 2. Page Configuration (added a custom pill icon)
st.set_page_config(page_title="Mariam's App", layout="wide", page_icon="💊")

# --- 3. APPLY THE THEME ---
# Mariam can change this URL to any pharmacy photo she prefers.
# I have provided a free-to-use photo of medicines in a pharmacy.
pharmacy_bg_url = "https://images.unsplash.com/photo-1576602976047-174e57a47881?q=80&w=2000"
add_pharmacy_theme(pharmacy_bg_url)

st.title("💊 Mariam's App: PDF to Excel Extractor")
st.write("Welcome, Mariam! Upload your pharmacy studies PDF to instantly extract tables and search through data.")

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
            # Assuming headers are on page 1, row 1
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            st.success("Extraction complete!")
            
            # 7. Show the Full Extracted Data First
            st.subheader("📋 Full Extracted Table")
            st.dataframe(df, use_container_width=True)
            
            # --- 8. SEARCH BAR (Just after showing the data) ---
            st.subheader("🔍 Search by Name or Ingredient")
            search_query = st.text_input("Type here to search (e.g., 'Paracetamol'):")
            
            # Filter the DataFrame if Mariam types something
            if search_query:
                # Scans all columns for the specific keyword, ignoring capitalization
                mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
                filtered_df = df[mask]
                st.write(f"**Found {len(filtered_df)} matching rows for '{search_query}'.**")
                
                # Show the filtered results
                st.dataframe(filtered_df, use_container_width=True)
            else:
                # If the search bar is empty, prepare to download the full table
                filtered_df = df
            
            # 9. Prepare EXCEL for Download
            # (Requires 'xlsxwriter' in requirements.txt)
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
