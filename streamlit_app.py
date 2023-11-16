import streamlit as st
import base64

def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display =  f"""<embed
    class="pdfobject"
    type="application/pdf"
    title="Embedded PDF"
    src="data:application/pdf;base64,{base64_pdf}"
    style="overflow: auto; width: 100%; height: 100%;">"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

def main():
    st.title('kNowDA: know your NDAs before you sign them')

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

            # To render the uploaded file 
            st.write("Preview of PDF file:")
            displayPDF(uploaded_file.name)

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
