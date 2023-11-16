import streamlit as st

def main():
    st.title('PDF File Upload Web Application')

    # Instructions for user
    st.write('Upload a PDF file.')

    # File uploader allows user to add their own PDF
    uploaded_file = st.file_uploader('Upload your input PDF file', type=['pdf'])

    if uploaded_file is not None:
        # Check the file's extension
        if uploaded_file.name.endswith('.pdf'):
            st.write("filename:", uploaded_file.name)
            st.write("filetype:", uploaded_file.type)
            st.write("filesize:", uploaded_file.size)

            # To read file as bytes and then display it as a download link:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.write('PDF file is uploaded successfully.')
            st.download_button(
                label="Download PDF",
                data=uploaded_file.getvalue(),
                file_name=uploaded_file.name,
                mime='application/octet-stream'
            )
        else:
            st.error('Invalid file type: Please upload a PDF file.')

if __name__ == '__main__':
    main()
