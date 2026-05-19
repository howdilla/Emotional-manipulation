import time
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    TIMEOUT,
    RETRY_ATTEMPTS,
    MODEL_CONFIG
)

if not OPENROUTER_API_KEY:
    print("ОШИБКА: OPENROUTER_API_KEY не найден")
    exit(1)

client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
    timeout=TIMEOUT
)


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_exponential(multiplier=1, min=2, max=15))
def call_llm(prompt: str, temperature: float = DEFAULT_TEMPERATURE):
    """
    Отправляет запрос к LLM через OpenRouter API.
    
    Args:
        prompt: текст запроса
        temperature: температура генерации (0.0 - детерминированно)
    
    Returns:
        tuple: (ответ_модели, флаг_успеха, время_выполнения)
    """
    try:
        start_time = time.time()

        response = client.chat.completions.create(
            model=MODEL_CONFIG["id"],
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=DEFAULT_MAX_TOKENS
        )

        elapsed = time.time() - start_time
        result = response.choices[0].message.content.strip()
        return result, True, elapsed

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return "Модель временно недоступна (превышены лимиты)", False, 0
        elif "404" in error_msg:
            return "Модель не найдена", False, 0
        else:
            return f"Ошибка: {error_msg[:150]}", False, 0


def test_connection():
    """Тестирует подключение к API"""
    print("=" * 50)
    print(f"Тест подключения к {MODEL_CONFIG['name']}")
    print("=" * 50)

    response, success, elapsed = call_llm("Ответь одним словом: Привет")

    if success:
        print(f"\nМодель работает! ({elapsed:.2f} сек)")
        print(f"Ответ: {response[:100]}")
        return True
    else:
        print(f"\nОшибка: {response}")
        return False


if __name__ == "__main__":
    test_connection()
