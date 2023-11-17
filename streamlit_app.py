import streamlit as st
import PyPDF2
import random
import json
import time
from RAG import doc_generate, sim_search, spacy_chunking
from tempfile import NamedTemporaryFile
import langchain

from langchain.document_loaders import PyPDFLoader

def generate_and_display(question, pdf_loader, original_text):
    generation = doc_generate(question, pdf_loader)
    st.sidebar.markdown(f"**Full statement: {question}**")
    if generation.citations:
        cite_info = generation.citations[0]
        cite_start = cite_info['start']
        cite_end = cite_info['end']
        displayed_text = generation.text[:cite_start] + '[' + generation.text[cite_start:cite_end] + '](#cite0)' + generation.text[cite_end:]
        referenced_doc = None
        for doc in generation.documents:
            if doc['id'] == cite_info['document_ids'][0]:
                referenced_doc = doc['snippet']
                break
        if referenced_doc:
            st.warning("Click on link to find references.")
            chunk = str(sim_search(generation.text[cite_start:cite_end], spacy_chunking(referenced_doc)))
            # st.sidebar.markdown(chunk, unsafe_allow_html=True)
            st.write(highlight_term(original_text, chunk), unsafe_allow_html=True)

    else:
        displayed_text = generation.text
        st.write(original_text)
    st.sidebar.markdown(displayed_text, unsafe_allow_html=True)

def load_questions():
    # read questions from common_questions.json
    with open('common_questions.json', 'r') as f:
        questions = list(json.load(f)['labels'].values())
        descriptions = [question['short_description'] for question in questions]
        full_questions = [question['hypothesis'] for question in questions]
        return descriptions, full_questions

def load_sample_questions(num=3):
    # read questions from common_questions.json
    with open('common_questions.json', 'r') as f:
        questions = list(json.load(f)['labels'].values())
        selected_questions = [0, 1, 2]
        if "question_sample" not in st.session_state:
            st.session_state.question_sample = random.sample(range(len(questions)), 3)
        # randomly select 3 questions
        selected_questions = st.session_state.question_sample
        descriptions = [questions[question_idx]['short_description'] for question_idx in selected_questions]
        full_questions = [questions[question_idx]['hypothesis'] for question_idx in selected_questions]
        return descriptions, full_questions

def highlight_term(text, term):
    """Highlights the term within the text and add id for reference."""
    highlighted_text = text.replace(term, f"<span id='cite0' style='background-color:yellow;'>{term}</span>", 1)
    return highlighted_text

def main():
    st.title('kNowDA: know your NDAs before you sign them')
    full_descriptions, full_questions = load_questions()

    # Instructions for user
    st.write('We provide references to the relevant clauses in your NDA to address your concerns.')

    # File uploader allows user to add their own PDF
    uploaded_file = st.file_uploader('Upload your input PDF file', type=['pdf'])

    time.sleep(1)
    if uploaded_file is not None:
        # Check the file's extension
        if uploaded_file.name.endswith('.pdf'):
            # Extract text from PDF file
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            with NamedTemporaryFile(delete=False) as f:
                f.write(uploaded_file.getbuffer())
                pdf_loader = PyPDFLoader(f.name)
            pages = []
            for page in range(len(pdf_reader.pages)):
                pages.append(pdf_reader.pages[page].extract_text())
            text = ' '.join(pages)
            user_text = st.sidebar.text_area("Enter your question here:")

            if st.sidebar.button("Submit"):
                matched_question = sim_search(user_text, full_questions)
                # st.sidebar.write("Matched question:", matched_question)
                if not matched_question:
                    generate_and_display(user_text, pdf_loader, text)
                else:
                    st.sidebar.write("Matched statement:", matched_question)
                    generate_and_display(matched_question, pdf_loader, text)

            # Display questions in Streamlit sidebar
            # Create checkboxes in the sidebar for each text example
            descriptions, questions = load_sample_questions()
            questions_dict = dict(zip(descriptions, questions))
            option = st.sidebar.radio("Or, some suggestions based on your document:", descriptions)

            if option != "":
                generate_and_display(questions_dict[option], pdf_loader, text)

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
