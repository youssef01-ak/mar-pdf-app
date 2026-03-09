import streamlit as st
import pdfplumber
import pandas as pd
import io

# Set up the layout and title for Mariam
st.set_page_config(page_title="Mariam's App", layout="wide")
st.title("🌸 Mariam's App: PDF to Excel Extractor")
st.write("Welcome, Mariam! Upload a PDF to extract its tables, view the full data, and search for specific names.")

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
            
            # 4. Show the Full Extracted Data First
            st.subheader("Extracted Data")
            st.dataframe(df, use_container_width=True)
            
            # --- 5. SEARCH BAR (Just after showing the data) ---
            st.subheader("🔍 Search by Name")
            search_query = st.text_input("Type a name to search the table:")
            
            # Filter the DataFrame if Mariam types something
            if search_query:
                # Scans all columns for the specific name, ignoring capitalization
                mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
                filtered_df = df[mask]
                st.write(f"**Found {len(filtered_df)} matching rows for '{search_query}'.**")
                
                # Show the filtered results
                st.dataframe(filtered_df, use_container_width=True)
            else:
                # If the search bar is empty, prepare to download the full table
                filtered_df = df
            
            # 6. Prepare EXCEL for Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Mariams Data')
            
            # Download Button (Saves the searched data, or full data if no search was made)
            st.download_button(
                label="📥 Download Excel File",
                data=buffer.getvalue(),
                file_name="Mariams_Extracted_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No tables could be found in this PDF.")
            
    except Exception as e:
        st.error(f"An error occurred during extraction: {e}")
