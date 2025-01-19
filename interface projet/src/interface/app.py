# src/interface/app.py
import streamlit as st
import os
from ..services.ocr_service import OCRService
from ..services.analysis_service import AnalysisService
from ..services.gemini_service import GeminiService

class MedicalAnalysisApp:
    def __init__(self, ocr_service: OCRService, analysis_service: AnalysisService, gemini_service: GeminiService):
        self.ocr_service = ocr_service
        self.analysis_service = analysis_service
        self.gemini_service = gemini_service

    def run(self):
        st.title("Analyse d'examens médicaux")
        st.write("Téléchargez un document et analysez son contenu.")

        # Upload de fichier
        uploaded_file = st.file_uploader(
            "Téléchargez un document à analyser",
            type=["png", "jpg", "jpeg", "pdf", "txt", "docx"]
        )

        # Colonnes pour les boutons
        col1, col2, col3 = st.columns(3)

        # Variable pour stocker le texte extrait
        if "extracted_text" not in st.session_state:
            st.session_state.extracted_text = ""

        # Bouton d'extraction
        with col1:
            if st.button("Extraire le texte"):
                if not uploaded_file:
                    st.error("Veuillez télécharger un document.")
                else:
                    with st.spinner("Traitement en cours..."):
                        try:
                            # Sauvegarde temporaire du fichier
                            temp_dir = "temp"
                            os.makedirs(temp_dir, exist_ok=True)
                            file_path = os.path.join(temp_dir, uploaded_file.name)

                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.read())

                            # Extraction OCR
                            result = self.ocr_service.process_document(file_path)
                            st.session_state.extracted_text = result.get("extraction", {}).get("result_text", "Aucun texte extrait.")
                            st.success("Texte extrait avec succès !")

                            # Nettoyage du fichier temporaire
                            os.remove(file_path)
                        except Exception as e:
                            st.error(f"Erreur lors de l'extraction : {str(e)}")

        # Zone de texte éditable
        st.text_area("Texte extrait", value=st.session_state.extracted_text, height=300, key="text_area")

        # Bouton d'organisation
        with col2:
            if st.button("Organiser"):
                if not st.session_state.text_area:
                    st.error("Aucun texte à organiser.")
                else:
                    with st.spinner("Organisation en cours..."):
                        try:
                            result = self.gemini_service.structure_text(st.session_state.text_area)
                            if result["success"]:
                                st.success("Texte organisé avec succès !")
                                st.markdown(result["structured_text"])
                            else:
                                st.error(result["error"])
                        except Exception as e:
                            st.error(f"Erreur : {str(e)}")

        # Bouton d'analyse
        with col3:
            if st.button("Analyser"):
                if not st.session_state.text_area:
                    st.error("Aucun texte à analyser.")
                else:
                    with st.spinner("Analyse en cours..."):
                        try:
                            result = self.analysis_service.analyze_text(st.session_state.text_area)
                            if result["success"]:
                                st.success("Analyse effectuée avec succès !")
                                st.markdown(result["analysis"])
                            else:
                                st.error(result["error"])
                        except Exception as e:
                            st.error(f"Erreur : {str(e)}")