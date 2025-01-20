import streamlit as st
import os
import tempfile
from io import BytesIO
from ..services.ocr_service import OCRService
from ..services.analysis_service import AnalysisService
from ..services.gemini_service import GeminiService
from ..services.report_service import ReportService

class MedicalAnalysisApp:
    def __init__(self, ocr_service: OCRService, analysis_service: AnalysisService, gemini_service: GeminiService, report_service: ReportService):
        self.ocr_service = ocr_service
        self.analysis_service = analysis_service
        self.gemini_service = gemini_service
        self.report_service = report_service

    def run(self):
        st.title("Analyse d'examens médicaux")
        st.write("Téléchargez un document et analysez son contenu.")

        uploaded_file = st.file_uploader(
            "Téléchargez un document à analyser",
            type=["png", "jpg", "jpeg", "pdf", "txt", "docx"]
        )

        col1, col2, col3 = st.columns(3)

        if "extracted_text" not in st.session_state:
            st.session_state.extracted_text = ""

        if "organized_text" not in st.session_state:
            st.session_state.organized_text = ""

        if "analysis_text" not in st.session_state:
            st.session_state.analysis_text = ""

        with col1:
            if st.button("Extraire le texte"):
                if not uploaded_file:
                    st.error("Veuillez télécharger un document.")
                else:
                    with st.spinner("Traitement en cours..."):
                        try:
                            temp_dir = "temp"
                            os.makedirs(temp_dir, exist_ok=True)
                            file_path = os.path.join(temp_dir, uploaded_file.name)

                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.read())

                            result = self.ocr_service.process_document(file_path)
                            st.session_state.extracted_text = result.get("extraction", {}).get("result_text", "Aucun texte extrait.")
                            st.success("Texte extrait avec succès !")

                            os.remove(file_path)
                        except Exception as e:
                            st.error(f"Erreur lors de l'extraction : {str(e)}")

        st.text_area("Texte extrait", value=st.session_state.extracted_text, height=300, key="text_area")

        with col2:
            if st.button("Organiser"):
                if not st.session_state.text_area:
                    st.error("Aucun texte à organiser.")
                else:
                    with st.spinner("Organisation en cours..."):
                        try:
                            result = self.gemini_service.structure_text(st.session_state.text_area)
                            if result["success"]:
                                st.session_state.organized_text = result["structured_text"]
                                st.success("Texte organisé avec succès !")
                                st.markdown(result["structured_text"])
                            else:
                                st.error(result["error"])
                        except Exception as e:
                            st.error(f"Erreur : {str(e)}")

        with col3:
            if st.button("Analyser"):
                if not st.session_state.text_area:
                    st.error("Aucun texte à analyser.")
                else:
                    with st.spinner("Analyse en cours..."):
                        try:
                            result = self.analysis_service.analyze_text(st.session_state.text_area)
                            if result["success"]:
                                st.session_state.analysis_text = result["analysis"]
                                st.success("Analyse effectuée avec succès !")
                                st.markdown(result["analysis"])
                            else:
                                st.error(result["error"])
                        except Exception as e:
                            st.error(f"Erreur : {str(e)}")

        if st.session_state.organized_text and st.session_state.analysis_text:
            if st.button("Générer le rapport"):
                with st.spinner("Génération du rapport en cours..."):
                    try:
                        # Generate the report to a temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file_path = tmp_file.name
                            self.report_service.generate_report(
                                organized_text=st.session_state.organized_text,
                                analysis_text=st.session_state.analysis_text,
                                output_path=tmp_file_path
                            )

                        # Read the temporary file and make it available for download
                        with open(tmp_file_path, "rb") as f:
                            pdf_data = f.read()

                        # Provide the download button
                        st.download_button(
                            label="Télécharger le rapport",
                            data=pdf_data,
                            file_name="rapport_medical.pdf",
                            mime="application/pdf"
                        )

                        st.success("Rapport généré avec succès !")
                    except Exception as e:
                        st.error(f"Erreur lors de la génération du rapport : {str(e)}")
