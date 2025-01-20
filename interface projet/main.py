from src.services.ocr_service import OCRService
from src.services.analysis_service import AnalysisService
from src.services.gemini_service import GeminiService
from src.services.report_service import ReportService  # Importing ReportService
from src.interface.app import MedicalAnalysisApp
from src.utils.config import Config

def main():
    # Chargement des configurations
    config = Config()

    # Initialisation des services
    ocr_service = OCRService(
        api_key=config.LLMWHISPERER_API_KEY,
        base_url=config.LLMWHISPERER_BASE_URL
    )
    analysis_service = AnalysisService(model_path=config.MODEL_PATH)
    gemini_service = GeminiService(api_key=config.GEMINI_API_KEY)
    
    # Initialisation du service de rapport
    report_service = ReportService(
        logo_path=r"C:\Users\pc\Desktop\interface projet\img\logo.png",  # Assurez-vous de spécifier le bon chemin pour le logo
        company_name="Textra_Health Analyser",
        footer_text="Rapport médical généré par Textra_Health"
    )

    # Lancement de l'application
    app = MedicalAnalysisApp(ocr_service, analysis_service, gemini_service, report_service)
    app.run()

if __name__ == "__main__":
    main()
