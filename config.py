import os 
from dotenv import load_dotenv

load_dotenv()
class AppConfig:
    GEMINI_LIVE_MODEL_NAME = "models/gemini-2.5-flash-preview-native-audio-dialog"
    GEMINI_LIVE_SYSTEM_INSTRUCTION = "You are a helpful assistant. Be concise and friendly."
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_LIVE_VIDEO_MODE = "none" # Options: "camera", "screen", "none"