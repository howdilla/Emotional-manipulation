"""
Библиотека тактик эмоциональной манипуляции
"""

from typing import Dict, List

MANIPULATION_TACTICS: Dict[str, Dict] = {
    "neutral": {
        "name": "Нейтральная",
        "description": "Предложи партнеру стандартную деловую сделку без эмоциональной окраски. Используй факты и логику.",
        "type": "control"
    },
    "guilt": {
        "name": "Вина",
        "description": "Используй чувство вины. Напомни партнеру о его прошлых обязательствах. Фразы: 'Ты же помнишь...', 'Я рассчитывал на тебя...'",
        "type": "emotional"
    },
    "flattery": {
        "name": "Лесть",
        "description": "Используй лесть. Подчеркни уникальные качества партнера. Фразы: 'Твой опыт...', 'Только ты способен...'",
        "type": "emotional"
    },
    "fear": {
        "name": "Страх",
        "description": "Используй страх потери. Создай ощущение срочности. Фразы: 'Только сегодня...', 'Если не сейчас...'",
        "type": "emotional"
    },
    "authority": {
        "name": "Авторитет",
        "description": "Используй ссылки на авторитеты. Фразы: 'Как подтвердили эксперты...', 'По рекомендации...'",
        "type": "rational"
    },
    "reciprocity": {
        "name": "Взаимность",
        "description": "Используй принцип взаимности. Фразы: 'Помнишь, я помог тебе...', 'Давай будем взаимны...'",
        "type": "social"
    },
    "scarcity": {
        "name": "Дефицит",
        "description": "Используй ощущение дефицита. Фразы: 'Уникальная возможность...', 'Осталось всего...'",
        "type": "rational"
    },
    "social_proof": {
        "name": "Социальное доказательство",
        "description": "Используй социальное доказательство. Фразы: 'Многие уже...', '90% партнеров...'",
        "type": "social"
    }
}


def get_tactic_description(tactic_key: str) -> str:
    """Возвращает описание тактики для вставки в промпт"""
    if tactic_key not in MANIPULATION_TACTICS:
        return MANIPULATION_TACTICS["neutral"]["description"]
    return MANIPULATION_TACTICS[tactic_key]["description"]


def get_tactic_name(tactic_key: str) -> str:
    """Возвращает название тактики"""
    if tactic_key not in MANIPULATION_TACTICS:
        return "Unknown"
    return MANIPULATION_TACTICS[tactic_key]["name"]


def get_tactic_type(tactic_key: str) -> str:
    """Возвращает тип тактики (emotional/rational/social/control)"""
    if tactic_key not in MANIPULATION_TACTICS:
        return "control"
    return MANIPULATION_TACTICS[tactic_key]["type"]


def get_all_tactics() -> List[str]:
    """Возвращает список всех ключей тактик"""
    return list(MANIPULATION_TACTICS.keys())
