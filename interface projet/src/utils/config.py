import os
from dataclasses import dataclass

@dataclass
class Config:
    LLMWHISPERER_API_KEY: str = os.getenv("LLMWHISPERER_API_KEY", "l9Bf7DJMpENmHGrabWV6pKfR3V2isKv2VL4O-bKiuQQ")
    LLMWHISPERER_BASE_URL: str = "https://llmwhisperer-api.us-central.unstract.com/api/v2"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyBLIWloBCWxyx9krj4QqJi6NntilE_snmA")
    MODEL_PATH: str = "chemin/vers/votre/modele"
    

