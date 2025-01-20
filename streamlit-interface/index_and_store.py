import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import torch
import logging

logging.basicConfig(level=logging.INFO)

def load_documents(data_path: str):
    """
    Charge les documents depuis un dossier ou un fichier JSON.
    """
    documents = []

    if os.path.isdir(data_path):
        # Charger tous les fichiers dans un dossier
        for file_name in os.listdir(data_path):
            file_path = os.path.join(data_path, file_name)
            if file_path.endswith(".txt"):  # Exemple pour les fichiers texte
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    documents.append(Document(page_content=text))
            elif file_path.endswith(".json"):  # Exemple pour les fichiers JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):  # Liste de documents JSON
                        for item in data:
                            if "text" in item:
                                documents.append(Document(page_content=item["text"]))
                    elif isinstance(data, dict) and "text" in data:  # Un document unique
                        documents.append(Document(page_content=data["text"]))
    elif os.path.isfile(data_path):
        if data_path.endswith(".txt"):
            with open(data_path, 'r', encoding='utf-8') as f:
                text = f.read()
                documents.append(Document(page_content=text))
        elif data_path.endswith(".json"):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if "text" in item:
                            documents.append(Document(page_content=item["text"]))
                elif isinstance(data, dict) and "text" in data:
                    documents.append(Document(page_content=data["text"]))

    return documents

def create_and_store_vector_store(data_path: str, model_path: str, output_path: str):
    """
    Crée une base vectorielle à partir des documents et la sauvegarde localement.
    """
    try:
        logging.info("Chargement du modèle d'embedding...")
        embeddings = HuggingFaceEmbeddings(
            model_name=model_path,
            model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
        )
        
        logging.info("Chargement des documents...")
        documents = load_documents(data_path)
        if not documents:
            raise ValueError("Aucun document chargé.")
        
        logging.info(f"{len(documents)} documents chargés. Division en chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        split_docs = text_splitter.split_documents(documents)
        logging.info(f"{len(split_docs)} chunks générés après division.")
        
        logging.info("Création de la base vectorielle...")
        vector_store = FAISS.from_documents(split_docs, embeddings)
        
        logging.info(f"Sauvegarde de la base vectorielle dans {output_path}...")
        vector_store.save_local(output_path)
        logging.info("Base vectorielle sauvegardée avec succès.")
    
    except Exception as e:
        logging.error(f"Erreur lors de la création de la base vectorielle: {e}")
        raise

if __name__ == "__main__":
    # Définissez les chemins
    DATA_PATH = r"C:\Users\pc\Desktop\projet metier masrour\Textra-Health\interface projet\data"  # Dossier ou fichier contenant les données
    MODEL_PATH = "ilyass20/multilingual-e5-large-MedAnalyser"   # Modèle d'embedding Hugging Face
    OUTPUT_PATH = r"C:\Users\pc\Desktop\projet metier masrour\Textra-Health\interface projet"  # Dossier de sauvegarde

    create_and_store_vector_store(DATA_PATH, MODEL_PATH, OUTPUT_PATH)
