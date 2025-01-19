import streamlit as st
import os
import atexit
import json
from datetime import datetime
from typing import Optional, Callable
from dataclasses import dataclass
from functools import wraps
from ..services.ocr_service import OCRService
from ..services.analysis_service import AnalysisService
from ..services.gemini_service import GeminiService

# Define the decorator
def handle_operation(operation_name: str):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                with st.spinner(f"{operation_name} en cours..."):
                    return func(*args, **kwargs)
            except Exception as e:
                st.error(f"Erreur lors de {operation_name}: {str(e)}")
                return None
        return wrapper
    return decorator

@dataclass
class AnalysisResult:
    success: bool
    content: dict
    error: Optional[str] = None

class MedicalAnalysisApp:
    def __init__(self, ocr_service: OCRService, analysis_service: AnalysisService, gemini_service: GeminiService):
        self.ocr_service = ocr_service
        self.analysis_service = analysis_service
        self.gemini_service = gemini_service
        self.initialize_session_state()

    def initialize_session_state(self):
        if "history" not in st.session_state:
            st.session_state.history = []
        if "extracted_text" not in st.session_state:
            st.session_state.extracted_text = ""
        if "analysis_results" not in st.session_state:
            st.session_state.analysis_results = None

    @handle_operation("sauvegarde du fichier")
    def save_uploaded_file(self, uploaded_file) -> str:
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path

    def setup_sidebar(self):
        with st.sidebar:
            st.header("Configuration")
            settings = {
                "language": st.selectbox("Langue", ["Français", "English"]),
                "theme": st.selectbox("Thème", ["Clair", "Sombre"]),
                "auto_analyze": st.checkbox("Analyse automatique", value=False)
            }
            
            if st.session_state.history:
                st.subheader("Historique")
                for item in st.session_state.history[-5:]:
                    st.text(f"• {item['timestamp']}: {item['action']}")
        return settings

    @handle_operation("extraction")
    def extract_text(self, file_path: str) -> AnalysisResult:
        result = self.ocr_service.process_document(file_path)
        if result.get("extraction", {}).get("result_text"):
            return AnalysisResult(
                success=True,
                content={"text": result["extraction"]["result_text"]}
            )
        return AnalysisResult(success=False, error="Échec de l'extraction")

    def display_results(self):
        if st.session_state.analysis_results:
            with st.expander("Résultats de l'analyse", expanded=True):
                tab1, tab2, tab3 = st.tabs(["Vue détaillée", "Résumé", "Graphiques"])
                
                with tab1:
                    st.markdown(st.session_state.analysis_results["detailed_analysis"])
                
                with tab2:
                    st.markdown(st.session_state.analysis_results["summary"])
                
                with tab3:
                    if "charts" in st.session_state.analysis_results:
                        for chart in st.session_state.analysis_results["charts"]:
                            st.plotly_chart(chart)

    def run(self):
        st.title("Analyse d'examens médicaux")
        settings = self.setup_sidebar()

        # File upload with validation
        allowed_types = ["png", "jpg", "jpeg", "pdf", "txt", "docx"]
        uploaded_file = st.file_uploader(
            "Téléchargez un document à analyser",
            type=allowed_types,
            help=f"Types de fichiers acceptés: {', '.join(allowed_types)}"
        )

        # Action buttons in columns with improved layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Extraire le texte", use_container_width=True):
                if not uploaded_file:
                    st.error("Veuillez télécharger un document.")
                else:
                    file_path = self.save_uploaded_file(uploaded_file)
                    if file_path:
                        result = self.extract_text(file_path)
                        if result.success:
                            st.session_state.extracted_text = result.content["text"]
                            st.session_state.history.append({
                                "timestamp": datetime.now().strftime("%H:%M:%S"),
                                "action": "Extraction"
                            })
                            st.success("Texte extrait avec succès !")
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass

        # Text area with improved UI
        text_container = st.container()
        with text_container:
            st.session_state.extracted_text = st.text_area(
                "Texte extrait",
                value=st.session_state.extracted_text,
                height=300,
                key="text_area",
                help="Vous pouvez modifier le texte directement ici"
            )

        with col2:
            if st.button("Organiser", use_container_width=True):
                if not st.session_state.text_area:
                    st.error("Aucun texte à organiser.")
                else:
                    result = self.gemini_service.structure_text(st.session_state.text_area)
                    if result["success"]:
                        st.session_state.history.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "action": "Organisation"
                        })
                        st.success("Texte organisé avec succès !")
                        st.markdown(result["structured_text"])

        with col3:
            if st.button("Analyser", use_container_width=True):
                if not st.session_state.text_area:
                    st.error("Aucun texte à analyser.")
                else:
                    result = self.analysis_service.analyze_text(st.session_state.text_area)
                    if result["success"]:
                        st.session_state.analysis_results = result
                        st.session_state.history.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "action": "Analyse"
                        })
                        self.display_results()

        # Add download button for results
        if st.session_state.analysis_results:
            st.download_button(
                label="Télécharger les résultats",
                data=json.dumps(st.session_state.analysis_results, indent=2),
                file_name="analyse_medicale.json",
                mime="application/json"
            )