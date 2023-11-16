import streamlit as st
import PyPDF2
import random
import json
from RAG import doc_generate, sim_search

def load_questions():
    # read questions from common_questions.json

    with open('common_questions.json', 'r') as f:
        questions = list(json.load(f)['labels'].values())
        selected_questions = [0, 1, 2]
        if "question_sample" not in st.session_state:
            st.session_state.question_sample = [random.sample(range(len(questions)), 3)]
        # randomly select 3 questions
        selected_questions = st.session_state.question_sample
        descriptions = [questions[question_idx]['short_description'] for question_idx in selected_questions]
        full_questions = [questions[question_idx]['hypothesis'] for question_idx in selected_questions]
        return descriptions, full_questions
        st.sidebar.write('Relevant Questions:')
        for question_idx in selected_questions:
            st.sidebar.checkbox(questions[question_idx]['short_description'], )

def highlight_term(text, term):
    """Highlights the term within the text."""
    highlighted_text = text.replace(term, f"<span style='background-color:yellow;'>{term}</span>")
    return highlighted_text

def main():
    st.title('kNowDA: know your NDAs before you sign them')

    # Instructions for user
    st.write('Upload a PDF file.')

    # File uploader allows user to add their own PDF
    uploaded_file = st.file_uploader('Upload your input PDF file', type=['pdf'])

    if uploaded_file is not None:
        # Check the file's extension
        if uploaded_file.name.endswith('.pdf'):
            # st.write("filename:", uploaded_file.name)
            # st.write("filetype:", uploaded_file.type)
            # st.write("filesize:", uploaded_file.size)
            
            # To render the uploaded file 
            # st.write("Preview of PDF file:")
            # with open(uploaded_file.name, "rb") as f:
            #     import base64
            #     base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            #     pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
            #     st.write(pdf_display, unsafe_allow_html=True)

            # Display questions in Streamlit sidebar
            # Create checkboxes in the sidebar for each text example
            descriptions, questions = load_questions()
            questions_dict = dict(zip(descriptions, questions))
            option = st.sidebar.radio("Topics based on your document:", descriptions)

            # Extract text from PDF file
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page].extract_text()

            if option != "":
                generation = doc_generate(questions_dict[option], uploaded_file.name)
                st.sidebar.markdown(f"**Clause: {questions_dict[option]}**")
                # st.sidebar.write('Relevant Documents:')
                if generation.citations:
                    cite_info = generation.citations[0]
                    cite_start = cite_info['start']
                    cite_end = cite_info['end']
                    displayed_text = generation.text[:cite_start] + '*' + generation.text[cite_start:cite_end] + '*' + generation.text[cite_end:]
                    referenced_doc = None
                    for doc in generation.documents:
                        if doc['id'] == cite_info['document_ids'][0]:
                            referenced_doc = doc['snippet']
                            break
                    if referenced_doc:
                        st.warning("Scroll to find exact reference in the document in highlighted text below.")
                        chunk = str(sim_search(generation.text[cite_start:cite_end], referenced_doc))
                        # st.sidebar.markdown(chunk, unsafe_allow_html=True)
                        st.markdown(highlight_term(text, chunk), unsafe_allow_html=True)

                else:
                    displayed_text = generation.text
                    st.write(text)
                st.sidebar.markdown(displayed_text, unsafe_allow_html=True)
                # cite_doc = cite_info['document_ids'][0]
                # for i in generation.documents:
                #     if i['id'] == cite_doc:
                #         cite_snippet = i['snippet'][cite_start:cite_end]
                #         st.sidebar.write(cite_snippet)
                #         break

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
