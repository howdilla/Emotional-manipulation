import sys
import os
import time
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_client import call_llm
from core.game import RepeatedTrustGame
from core.manipulator import get_tactic_description, get_all_tactics
from config.settings import MODEL_CONFIG, REQUEST_DELAY, DEFAULT_EXPERIMENTS_PER_COMBO, DEFAULT_ROUNDS_PER_GAME


def run_single_game(tactic_key: str, victim_type: str, game_id: int) -> list:
    """
    Проводит одну многократную игру (несколько раундов с одним партнёром)
    """
    print(f"\n{'='*50}")
    print(f"ИГРА #{game_id}: тактика={tactic_key}, жертва={victim_type}, раундов={DEFAULT_ROUNDS_PER_GAME}")
    print(f"{'='*50}")

    game = RepeatedTrustGame(victim_type=victim_type, total_rounds=DEFAULT_ROUNDS_PER_GAME)
    all_rounds_results = []
    tactic_description = get_tactic_description(tactic_key)

    for round_num in range(1, DEFAULT_ROUNDS_PER_GAME + 1):
        print(f"\n  Раунд {round_num}/{DEFAULT_ROUNDS_PER_GAME}")

        manipulator_prompt = game.get_manipulator_prompt(tactic_description, round_num)
        manipulator_message, success_manipulator, time_manipulator = call_llm(manipulator_prompt)

        if not success_manipulator:
            print(f"    Ошибка: манипулятор не ответил - {manipulator_message}")
            break

        print(f"    Манипулятор: {manipulator_message[:100]}...")

        victim_prompt = game.get_victim_prompt(manipulator_message, round_num)
        victim_response, success_victim, time_victim = call_llm(victim_prompt)

        if not success_victim:
            print(f"    Ошибка: жертва не ответила - {victim_response[:100]}")
            break

        print(f"    Ответ жертвы: '{victim_response}'")

        if "ДА" in victim_response.upper():
            decision = "ДА"
        elif "НЕТ" in victim_response.upper():
            decision = "НЕТ"
        else:
            print(f"    Неожиданный ответ жертвы: '{victim_response}', считаем как НЕТ")
            decision = "НЕТ"

        round_result = game.play_round(manipulator_message, decision)

        output_row = {
            "game_id": game_id,
            "experiment_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "model": MODEL_CONFIG["name"],
            "model_id": MODEL_CONFIG["id"],
            "tactic": tactic_key,
            "victim_type": victim_type,
            "total_rounds": DEFAULT_ROUNDS_PER_GAME,
            "round_number": round_num,
            "manipulator_message": manipulator_message,
            "victim_raw_response": victim_response,
            "victim_decision": decision,
            "was_cheated": round_result.get('was_cheated'),
            "manipulator_gain": round_result['manipulator_gain'],
            "victim_gain": round_result['victim_gain'],
            "manipulator_total": round_result['manipulator_total'],
            "victim_total": round_result['victim_total'],
            "trustworthiness": round_result['trustworthiness'],
            "rounds_remaining": round_result['rounds_remaining'],
            "manipulator_time_seconds": round(time_manipulator, 2),
            "victim_time_seconds": round(time_victim, 2),
            "total_time_seconds": round(time_manipulator + time_victim, 2),
            "victim_success": (round_result['victim_gain'] > 0)
        }

        print(f"    Решение: {decision} → Жертва получила: {round_result['victim_gain']}")
        all_rounds_results.append(output_row)

        time.sleep(REQUEST_DELAY)

    return all_rounds_results


def run_experiment():
    """Запускает полный эксперимент со всеми тактиками и типами жертв"""
    print("=" * 70)
    print("ЭКСПЕРИМЕНТ С МНОГОКРАТНЫМИ ИГРАМИ")
    print(f"Модель: {MODEL_CONFIG['name']}")
    print("Мультиагентное моделирование эмоциональных манипуляций")
    print("=" * 70)

    tactics = get_all_tactics()
    print(f"\nТактики ({len(tactics)}): {', '.join(tactics)}")

    victim_types = ["rational", "emotional"]
    games_per_combo = DEFAULT_EXPERIMENTS_PER_COMBO
    rounds_per_game = DEFAULT_ROUNDS_PER_GAME

    total_games = len(tactics) * len(victim_types) * games_per_combo
    total_rounds = total_games * rounds_per_game

    print(f"\nПараметры эксперимента:")
    print(f"   Модель: {MODEL_CONFIG['name']}")
    print(f"   Тактики: {len(tactics)}")
    print(f"   Типы жертв: {victim_types}")
    print(f"   Игр на комбинацию: {games_per_combo}")
    print(f"   Раундов в игре: {rounds_per_game}")
    print(f"   Всего игр: {total_games}")
    print(f"   Всего раундов: {total_rounds}")

    all_results = []
    game_counter = 0
    round_counter = 0
    start_time = time.time()

    for tactic_key in tactics:
        print(f"\n{'='*60}")
        print(f"ТАКТИКА: {tactic_key}")
        print(f"{'='*60}")

        for victim_type in victim_types:
            print(f"\n  Тип жертвы: {victim_type.upper()}")

            for game_num in range(1, games_per_combo + 1):
                game_counter += 1
                game_results = run_single_game(tactic_key, victim_type, game_counter)
                all_results.extend(game_results)
                round_counter += len(game_results)

                elapsed_time = time.time() - start_time
                minutes = int(elapsed_time // 60)
                seconds = int(elapsed_time % 60)

                print(f"\n    ПРОГРЕСС:")
                print(f"       Игр: {game_counter}/{total_games}")
                print(f"       Раундов: {round_counter}/{total_rounds}")
                print(f"       Время: {minutes} мин {seconds} сек")

    if not all_results:
        print("\nНЕТ РЕЗУЛЬТАТОВ для сохранения")
        return None

    df = pd.DataFrame(all_results)

    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)

    experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(results_dir, f"repeated_experiment_{experiment_id}.csv")

    try:
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig', quoting=1, escapechar='\\')
        print(f"\nCSV файл сохранён: {csv_filename}")
    except Exception as e:
        print(f"\nОшибка при сохранении CSV: {e}")
        return None

    print(f"\nВсего сохранено раундов: {len(df)}")
    print(f"Сохранено игр: {df['game_id'].nunique()}")

    trust_count = (df['victim_decision'] == 'ДА').sum()
    trust_rate = trust_count / len(df) * 100
    print(f"Жертва сказала ДА: {trust_count}/{len(df)} ({trust_rate:.1f}%)")

    return df


if __name__ == "__main__":
    print("ЗАПУСК ЭКСПЕРИМЕНТА")
    print("=" * 70)
    run_experiment()
