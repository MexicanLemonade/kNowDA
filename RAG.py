import langchain

from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Qdrant
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.text_splitter import SpacyTextSplitter, NLTKTextSplitter, CharacterTextSplitter
from langchain.schema import Document

import cohere
import os
import re
import textract
import numpy as np

os.environ['COHERE_API_KEY'] = "zlOymXPbRHyujsgkjerXJZXFVtq1aGHUOq96pXvQ"
co = cohere.Client('zlOymXPbRHyujsgkjerXJZXFVtq1aGHUOq96pXvQ')

def pdf_to_chunks(filename):
    loader = PyPDFLoader(filename)
    pages = loader.load_and_split()
    chunked_pages = []
    for page in pages:
        chunked_page_content = page.page_content.split('\n\n')
        for chunk in chunked_page_content:
            chunked_pages.append(Document(page_content=chunk, metadata=page.metadata))
    return chunked_pages

def doc_generate(question, doc_name):
    docs = [dict(chunk) for chunk in pdf_to_chunks(doc_name)]
    # print(docs[0].keys())
    response = co.chat(
        chat_history=[
            {"role": "USER", "message": "Take a deep breath and think step by step: Tell me whether the given clause is satisfied within the contract document. If it is satisfied, please provide the evidence in the original contract. If not, please specify if it is not mentioned in the contract, or the contract contradicted the clause, in which case you should also provide the evidence."},
        ],
        message=question,
        #   connectors=[{"id": "web-search"}] # perform web search before answering the question
        documents=[{'snippet': doc['page_content']} for doc in docs]
        , 
        prompt_truncation='AUTO'
    )
    return response

def sim_search(gen_sent, doc):
    # splitter = NLTKTextSplitter()
    # chunks = splitter.split_text(doc)
    # print(len(chunks))
    import spacy
    from spacy.lang.en import English

    sentencizer = spacy.load('en_core_web_sm')


    # text = 'My first birthday was great. My 2. was even better.'

    chunks = sentencizer(doc)
    
    embedding = CohereEmbeddings()
    gen_sent_embedding = embedding.embed_query(gen_sent)
    max_similarity = 0
    max_chunk = chunks[0]
    for chunk in chunks.sents:
        chunk_embedding = embedding.embed_documents([str(chunk)])[0]
        # directly compare the embeddings
        similarity = np.dot(gen_sent_embedding, chunk_embedding)/(np.linalg.norm(gen_sent_embedding)*np.linalg.norm(chunk_embedding))
        if similarity > max_similarity:
            max_similarity = similarity
            max_chunk = chunk
    return max_chunk

if __name__ == '__main__':
    question = "Receiving Party shall destroy or return some Confidential Information upon the termination of Agreement."
    doc_name = "01_Bosch-Automotive-Service-Solutions-Mutual-Non-Disclosure-Agreement-7-12-17.pdf"
    print(doc_generate(question, doc_name))