# src/services/gemini_service.py
import google.generativeai as genai
from typing import Dict

class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.configure()

    def configure(self):
        genai.configure(api_key=self.api_key)

    def structure_text(self, text: str) -> Dict:
        """Appelle l'API Gemini pour structurer le texte."""
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = """structure ce texte d'analyse médicale on veux le donner a un medecin pour l'interpreter il doit etre clair, n'ajouter aucun remarque ou informations.

            
            Texte des analyses:"""
            
            query = f"{prompt}\n\n{str(text)}"
            response = model.generate_content(query)
            
            return {
                "success": True,
                "structured_text": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur de structuration : {str(e)}"
            }