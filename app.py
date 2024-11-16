import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# Function to extract tables from the PDF
def extract_table_from_pdf(pdf_file, page_number=None):
    tables = []
    with pdfplumber.open(pdf_file) as pdf:
        if page_number:  # Extract from a specific page
            page = pdf.pages[page_number - 1]
            table = page.extract_table()
            if table:
                tables.append(pd.DataFrame(table[1:], columns=table[0]))
        else:  # Extract from all pages
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    tables.append(pd.DataFrame(table[1:], columns=table[0]))

    # Combine all tables into a single DataFrame
    if tables:
        combined_df = pd.concat(tables, ignore_index=True)
        return combined_df
    else:
        return None

# Streamlit UI
st.set_page_config(page_title="Skavch PDF Tabular Data Extractor Engine", page_icon="📊", layout="wide")

# Add an image to the header
st.image("bg1.jpg", use_column_width=True)
st.title("Skavch PDF Tabular Data Extractor Engine")
st.write("Upload a PDF file to extract tables and download the results.")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    st.success("File uploaded successfully!")
    
    # Option to choose specific page or all pages
    with pdfplumber.open(uploaded_file) as pdf:
        num_pages = len(pdf.pages)
    st.write(f"The uploaded PDF has **{num_pages}** pages.")
    page_option = st.radio(
        "Do you want to extract data from:",
        ("All Pages", "A Specific Page")
    )

    page_number = None
    if page_option == "A Specific Page":
        page_number = st.number_input(
            "Enter the page number to extract data from:",
            min_value=1,
            max_value=num_pages,
            value=1,
            step=1
        )

    # Extract tables when the user clicks a button
    if st.button("Extract Tables"):
        extracted_data = extract_table_from_pdf(uploaded_file, page_number)
        if extracted_data is not None:
            st.success("Table extracted successfully!")
            st.write("Here is the extracted data:")
            st.dataframe(extracted_data)

            # Provide download options
            def convert_df_to_bytes(df, file_format='csv'):
                buffer = BytesIO()
                if file_format == 'csv':
                    df.to_csv(buffer, index=False)
                elif file_format == 'excel':
                    df.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)
                return buffer

            csv_data = convert_df_to_bytes(extracted_data, file_format='csv')
            excel_data = convert_df_to_bytes(extracted_data, file_format='excel')

            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="extracted_table.csv",
                mime="text/csv"
            )

            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name="extracted_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No table data found in the selected PDF/page.")
