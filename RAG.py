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
from typing import List

os.environ['COHERE_API_KEY'] = "zlOymXPbRHyujsgkjerXJZXFVtq1aGHUOq96pXvQ"
co = cohere.Client('zlOymXPbRHyujsgkjerXJZXFVtq1aGHUOq96pXvQ')

def pdf_to_chunks(loader: PyPDFLoader):
    # loader = PyPDFLoader(filename)
    pages = loader.load_and_split()
    chunked_pages = []
    for page in pages:
        chunked_page_content = page.page_content.split('\n\n')
        for chunk in chunked_page_content:
            chunked_pages.append(Document(page_content=chunk, metadata=page.metadata))
    return chunked_pages

def doc_generate(question, pdf_loader):
    docs = [dict(chunk) for chunk in pdf_to_chunks(pdf_loader)]
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

def spacy_chunking(doc: str):
    import spacy
    # check if spacy model is installed
    try:
        nlp = spacy.load('en_core_web_sm')
    except:
        os.system('python -m spacy download en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')

    chunks = nlp(doc)
    # print(chunks.sents)

    return list(chunks.sents)

def sim_search(query: str, collection: List[str]):
    embedding = CohereEmbeddings()
    gen_sent_embedding = embedding.embed_query(query)
    chunk_embeddings = embedding.embed_documents([str(text) for text in collection])
    similarities = np.dot(gen_sent_embedding/np.linalg.norm(gen_sent_embedding), np.array(chunk_embeddings/np.linalg.norm(chunk_embeddings)).T)
    max_idx = np.argmax(similarities)
    if similarities[max_idx] > 0.8:
        return collection[max_idx]
    else:
        return None

if __name__ == '__main__':
    question = "Receiving Party shall destroy or return some Confidential Information upon the termination of Agreement."
    doc_name = "01_Bosch-Automotive-Service-Solutions-Mutual-Non-Disclosure-Agreement-7-12-17.pdf"
    print(doc_generate(question, doc_name))