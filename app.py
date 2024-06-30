# Import necessary libraries
import streamlit as st
import langchain as lc
from langchain.document_loaders import LocalDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import os

# Initialize the app
st.title("University Document Retrieval System")

# Load all documents in the folder
folder_path = "documents"  # replace with your folder path if different
documents = []
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf") or filename.endswith(".txt"):  # add other file types if needed
        loader = LocalDocumentLoader(path=os.path.join(folder_path, filename))
        documents.extend(loader.load())

# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
chunks = text_splitter.split_documents(documents)

# Embed the chunks
embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(chunks, embeddings)

# Create a RetrievalQA chain
retrieval_qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=db.as_retriever()
)

# Streamlit user input for the question
question = st.text_input("Ask a question about the university documents:")

# If a question is asked, use the chain to find the answer
if question:
    # Retrieve the top-5 relevant chunks
    retrieved_docs = db.similarity_search(question, k=5)
    # Concatenate the retrieved chunks
    context = " ".join([doc.page_content for doc in retrieved_docs])
    # Create a curated prompt for the LLM
    system_prompt = (
        f"You are a knowledgeable assistant. You have access to a variety of university documents, "
        f"including policies, academic guidelines, schedules, and more. When a user asks a question, "
        f"your task is to provide an accurate and concise answer based on the provided context. "
        f"Make sure your response is clear and directly addresses the user's query.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer in detail:"
    )
    # Get the response from the LLM
    answer = retrieval_qa_chain.llm.generate(system_prompt)
    st.write("Answer:", answer)
