import streamlit as st
import os
from ..services.ocr_service import OCRService
from ..services.analysis_service import AnalysisService
from ..utils.config import Config


class MedicalAnalysisApp:
    def __init__(self, ocr_service: OCRService, analysis_service: AnalysisService):
        self.ocr_service = ocr_service
        self.analysis_service = analysis_service

    def run(self):
        st.title("Analyse d'examens médicaux")
        st.write("Téléchargez un document et analysez son contenu.")

        # Upload de fichier
        uploaded_file = st.file_uploader(
            "Téléchargez un document à analyser",
            type=["png", "jpg", "jpeg", "pdf", "txt", "docx"]
        )

        # Bouton de traitement
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
                        extracted_text = result.get("extraction", {}).get("result_text", "Aucun texte extrait.")
                        st.success("Texte extrait avec succès !")
                        st.text_area("Texte extrait", value=extracted_text, height=300)

                        # Nettoyage du fichier temporaire
                        os.remove(file_path)

                    except Exception as e:
                        st.error(f"Erreur lors de l'extraction : {str(e)}")

        # Analyse du texte
        if st.button("Analyser le texte extrait"):
            extracted_text = st.session_state.get("extracted_text", "")
            if not extracted_text:
                st.error("Aucun texte disponible pour l'analyse.")
            else:
                with st.spinner("Analyse en cours..."):
                    try:
                        analysis_result = self.analysis_service.analyze_text(extracted_text)
                        if analysis_result["success"]:
                            st.success("Analyse effectuée avec succès !")
                            st.markdown(analysis_result["analysis"])
                        else:
                            st.error(f"Erreur lors de l'analyse : {analysis_result['error']}")
                    except Exception as e:
                        st.error(f"Erreur : {str(e)}")
