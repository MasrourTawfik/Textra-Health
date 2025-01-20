import os
from langchain_community.vectorstores import FAISS  # Update for the latest import path
from langchain_community.embeddings import HuggingFaceEmbeddings  # Update for the latest import path

# Path to the directory containing the FAISS index file
faiss_directory = r"C:\Users\pc\Desktop\projet metier masrour\Textra-Health\interface projet"

# Initialize embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Check if FAISS file exists in the directory
faiss_file = os.path.join(faiss_directory, "index.faiss")
if not os.path.exists(faiss_file):
    raise FileNotFoundError(f"FAISS index file not found: {faiss_file}")

# Load FAISS index (pass directory, not full file path)
vector_store = FAISS.load_local(faiss_directory, embeddings, allow_dangerous_deserialization=True)

print("FAISS index loaded successfully.")
