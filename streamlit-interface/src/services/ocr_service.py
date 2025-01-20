from unstract.llmwhisperer import LLMWhispererClientV2
from typing import Dict, Optional
import os

class OCRService:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.client = LLMWhispererClientV2(
            base_url=base_url or "https://llmwhisperer-api.us-central.unstract.com/api/v2",
            api_key=api_key or os.getenv("LLMWHISPERER_API_KEY")
        )

    def process_document(self, file_path: str) -> Dict:
        try:
            return self.client.whisper(
                file_path=file_path,
                wait_for_completion=True,
                wait_timeout=200
            )
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction OCR: {str(e)}")
