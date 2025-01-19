# src/services/analysis_service.py
from typing import Dict
import torch
from langchain.llms import Ollama
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import logging

class AnalysisService:
    def __init__(self, model_path: str):
        try:
            # Initialisation du LLM via Ollama
            self.llm = Ollama(model="mistral")
            
            # Chargement de votre embedding local
            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_path,
                model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
            )
            
            # Chargement de la base de connaissances vectorielle
            self.vector_store = FAISS.load_local(
                "chemin/vers/votre/base_vectorielle",
                self.embeddings
            )
            
            # Configuration du prompt pour l'analyse médicale
            self.prompt_template = PromptTemplate(
                template="""En tant qu'assistant médical, analysez les résultats d'analyses sanguines suivants.
                Utilisez le contexte fourni pour interpréter les valeurs et fournir une analyse détaillée.

                Contexte: {context}
                
                Résultats à analyser: {question}

                Veuillez fournir:
                1. Une validation des valeurs par rapport aux normes
                2. Une identification des anomalies éventuelles
                3. Une interprétation clinique
                4. Des recommandations si nécessaire

                Analyse:""",
                input_variables=["context", "question"]
            )
            
            # Configuration de la chaîne RAG
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}
                ),
                chain_type_kwargs={
                    "prompt": self.prompt_template
                }
            )
            
            logging.info("Service d'analyse initialisé avec succès")
            
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation du service d'analyse: {str(e)}")
            raise

    def analyze_text(self, text: str) -> Dict:
        """
        Analyse le texte des résultats médicaux en utilisant le système RAG.
        """
        try:
            if not text.strip():
                return {
                    "success": False,
                    "error": "Le texte à analyser est vide"
                }
            
            # Prétraitement du texte si nécessaire
            processed_text = self._preprocess_text(text)
            
            # Exécution de l'analyse RAG
            analysis_result = self.qa_chain.run(processed_text)
            
            # Post-traitement de la réponse
            formatted_result = self._format_analysis(analysis_result)
            
            return {
                "success": True,
                "analysis": formatted_result
            }
            
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse: {str(e)}")
            return {
                "success": False,
                "error": f"Erreur lors de l'analyse: {str(e)}"
            }

    def _preprocess_text(self, text: str) -> str:
        """
        Prétraite le texte avant l'analyse.
        """
        # Nettoyage basique du texte
        text = text.strip()
        text = text.replace('\n\n', '\n')
        # Ajoutez d'autres étapes de prétraitement si nécessaire
        return text

    def _format_analysis(self, raw_analysis: str) -> str:
        """
        Formate le résultat de l'analyse pour l'affichage.
        """
        # Vous pouvez personnaliser le formatage ici
        formatted_analysis = raw_analysis.strip()
        
        # Ajout de markdown pour une meilleure présentation
        sections = formatted_analysis.split('\n')
        formatted_sections = []
        
        for section in sections:
            if any(section.startswith(str(i)) for i in range(1, 5)):
                # C'est un titre de section
                formatted_sections.append(f"### {section}")
            else:
                formatted_sections.append(section)
        
        return "\n\n".join(formatted_sections)