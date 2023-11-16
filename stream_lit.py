import streamlit as st
from io import StringIO
import pandas as pd

def main():
    st.title('File Upload Web Application')

    # Instructions for user
    st.write('Upload a CSV file for analysis.')

    # File uploader allows user to add their own CSV
    uploaded_file = st.file_uploader('Upload your input CSV file', type=['csv'])

    if uploaded_file is not None:
        # Check the file's extension
        if uploaded_file.name.endswith('.csv'):
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
            st.write("filename:", uploaded_file.name)
            st.write("filetype:", uploaded_file.type)
            st.write("filesize:", uploaded_file.size)

            # To convert to a string based IO:
            stringio = StringIO(uploaded_file.getvalue().decode('utf-8'))
            st.write(stringio)

            # To read file as string:
            string_data = stringio.read()
            st.write(string_data)

            # Can be used wherever a "file-like" object is accepted:
            dataframe = pd.read_csv(uploaded_file)
            st.write(dataframe)
        else:
            st.error('Invalid file type: Please upload a CSV file.')

if __name__ == '__main__':
    main()
