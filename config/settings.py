import os
from dotenv import load_dotenv

load_dotenv()

# API ключ OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY не найден в файле .env")

# Настройки API
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 500
TIMEOUT = 90
RETRY_ATTEMPTS = 3

# Список доступных моделей
AVAILABLE_MODELS = {
    "gpt-oss-120b": {
        "id": "openai/gpt-oss-120b:free",
        "name": "GPT-OSS-120B",
        "description": "Открытая модель от OpenAI"
    },
    "gpt-4o": {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o-mini",
        "description": "Флагманская мультимодальная модель OpenAI"
    },
    "deepseek": {
        "id": "deepseek/deepseek-v3.2",
        "name": "DeepSeek V3.2",
        "description": "Мощная открытая модель от DeepSeek"
    },
    "gemini": {
        "id": "google/gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash Lite",
        "description": "Модель от Google"
    },
    "grok": {
        "id": "x-ai/grok-4.1-fast",
        "name": "Grok 4.1 Fast",
        "description": "Модель от xAI"
    }
}

# Текущая модель для эксперимента
CURRENT_MODEL_KEY = "gpt-4o"

MODEL_CONFIG = {
    "id": AVAILABLE_MODELS[CURRENT_MODEL_KEY]["id"],
    "name": AVAILABLE_MODELS[CURRENT_MODEL_KEY]["name"],
    "description": AVAILABLE_MODELS[CURRENT_MODEL_KEY]["description"]
}

# Параметры эксперимента
DEFAULT_EXPERIMENTS_PER_COMBO = 7
DEFAULT_ROUNDS_PER_GAME = 5
REQUEST_DELAY = 2
