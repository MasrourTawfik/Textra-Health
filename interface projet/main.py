from src.services.ocr_service import OCRService
from src.services.analysis_service import AnalysisService
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

    # Lancement de l'application
    app = MedicalAnalysisApp(ocr_service, analysis_service)
    app.run()


if __name__ == "__main__":
    main()
