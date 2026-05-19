"""
Анализ результатов эксперимента и расчет ELO-рейтинга
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.elo_rating import ELORating, calculate_elo_for_tactics, calculate_elo_for_models
from core.manipulator import get_tactic_name


def find_latest_results(prefix: str = "experiment") -> str:
    """Находит последний файл с результатами"""
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

    if not os.path.exists(results_dir):
        return None

    files = [f for f in os.listdir(results_dir) if f.startswith(prefix) and f.endswith(".csv")]

    if not files:
        return None

    return max(files, key=lambda x: os.path.getctime(os.path.join(results_dir, x)))


def analyze_results():
    """Анализирует результаты эксперимента"""
    print("=" * 70)
    print("АНАЛИЗ РЕЗУЛЬТАТОВ ЭКСПЕРИМЕНТА")
    print("=" * 70)

    # Находим файл
    latest_file = find_latest_results()

    if not latest_file:
        print("\nНет файлов с результатами. Сначала запустите эксперимент.")
        return None

    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    df = pd.read_csv(os.path.join(results_dir, latest_file))

    print(f"\nФайл: {latest_file}")
    print(f"Всего записей: {len(df)}")
    if 'model' in df.columns:
        print(f"Модель: {df['model'].iloc[0]}")

    # 1. Общая статистика
    print("\n" + "=" * 70)
    print("1. ОБЩАЯ СТАТИСТИКА")
    print("=" * 70)

    decision_col = 'victim_decision' if 'victim_decision' in df.columns else 'decision'
    gain_col = 'victim_gain' if 'victim_gain' in df.columns else 'victim_gain'
    manip_gain_col = 'manipulator_gain' if 'manipulator_gain' in df.columns else 'manipulator_gain'

    trust_rate = df[df[decision_col] == 'ДА'].shape[0] / len(df) * 100

    print(f"  Доверились партнёру: {trust_rate:.1f}%")
    print(f"  Средняя прибыль жертвы: {df[gain_col].mean():.1f}")
    print(f"  Средняя прибыль манипулятора: {df[manip_gain_col].mean():.1f}")

    # 2. По типам жертв
    print("\n" + "=" * 70)
    print("2. СРАВНЕНИЕ ТИПОВ ЖЕРТВ")
    print("=" * 70)

    for victim_type in ['rational', 'emotional']:
        vt_df = df[df['victim_type'] == victim_type]
        trust = vt_df[vt_df[decision_col] == 'ДА'].shape[0]
        total = len(vt_df)
        print(f"\n  {victim_type.upper()}:")
        print(f"    Доверились: {trust}/{total} ({trust / total * 100:.1f}%)")

    # 3. По тактикам
    print("\n" + "=" * 70)
    print("3. ЭФФЕКТИВНОСТЬ ТАКТИК МАНИПУЛЯЦИИ")
    print("=" * 70)

    tactic_stats = []
    for tactic in df['tactic'].unique():
        tactic_df = df[df['tactic'] == tactic]

        # Для эмоциональных жертв
        emotional_df = tactic_df[tactic_df['victim_type'] == 'emotional']
        emotional_trust = emotional_df[emotional_df[decision_col] == 'ДА'].shape[0]
        emotional_total = len(emotional_df)

        # Для рациональных жертв
        rational_df = tactic_df[tactic_df['victim_type'] == 'rational']
        rational_trust = rational_df[rational_df[decision_col] == 'ДА'].shape[0]
        rational_total = len(rational_df)

        tactic_stats.append({
            'tactic': tactic,
            'name': get_tactic_name(tactic),
            'emotional_trust_rate': emotional_trust / emotional_total * 100 if emotional_total > 0 else 0,
            'rational_trust_rate': rational_trust / rational_total * 100 if rational_total > 0 else 0,
        })

    print("\n{:<20} {:>20} {:>20}".format("Тактика", "Эмоциональные", "Рациональные"))
    print("-" * 60)
    for ts in sorted(tactic_stats, key=lambda x: x['emotional_trust_rate'], reverse=True):
        print("{:<20} {:>19.1f}% {:>19.1f}%".format(
            ts['name'][:18],
            ts['emotional_trust_rate'],
            ts['rational_trust_rate']
        ))

    # 4. ELO-рейтинг тактик
    print("\n" + "=" * 70)
    print("4. ELO-РЕЙТИНГ ТАКТИК МАНИПУЛЯЦИИ (эмоциональные жертвы)")
    print("=" * 70)

    elo_tactics = calculate_elo_for_tactics(df, victim_type="emotional")
    elo_tactics.print_rankings()

    # 5. ELO-рейтинг моделей (если есть данные)
    if 'model' in df.columns:
        print("\n" + "=" * 70)
        print("5. ELO-РЕЙТИНГ МОДЕЛЕЙ (устойчивость к манипуляциям)")
        print("=" * 70)

        elo_models = calculate_elo_for_models(df, victim_type="emotional")
        elo_models.print_rankings("ELO-РЕЙТИНГ МОДЕЛЕЙ")

    # 6. Примеры сообщений
    print("\n" + "=" * 70)
    print("6. ПРИМЕРЫ СООБЩЕНИЙ")
    print("=" * 70)

    print("\n✅ УСПЕШНЫЕ МАНИПУЛЯЦИИ (жертва согласилась):")
    successful = df[(df[decision_col] == 'ДА')].head(3)
    for _, row in successful.iterrows():
        print(f"\n  Тактика: {get_tactic_name(row['tactic'])}")
        print(f"  Жертва: {row['victim_type']}")
        msg = row['manipulator_message'][:120] if len(row['manipulator_message']) > 120 else row['manipulator_message']
        print(f"  Сообщение: {msg}...")

    print("\n❌ ПРОВАЛЬНЫЕ МАНИПУЛЯЦИИ (жертва отказалась):")
    failed = df[df[decision_col] == 'НЕТ'].head(3)
    for _, row in failed.iterrows():
        print(f"\n  Тактика: {get_tactic_name(row['tactic'])}")
        print(f"  Жертва: {row['victim_type']}")
        msg = row['manipulator_message'][:120] if len(row['manipulator_message']) > 120 else row['manipulator_message']
        print(f"  Сообщение: {msg}...")

    # Сохраняем анализ
    output_file = os.path.join(results_dir, f"analysis_{latest_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("АНАЛИЗ ЭКСПЕРИМЕНТА\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Файл: {latest_file}\n")
        f.write(f"Всего записей: {len(df)}\n")
        f.write(f"Доверились: {trust_rate:.1f}%\n\n")

        f.write("ЭФФЕКТИВНОСТЬ ТАКТИК (эмоциональные жертвы):\n")
        for ts in sorted(tactic_stats, key=lambda x: x['emotional_trust_rate'], reverse=True):
            f.write(f"  {ts['name']}: {ts['emotional_trust_rate']:.1f}%\n")

        f.write("\nELO-РЕЙТИНГ ТАКТИК:\n")
        for entity, rating in elo_tactics.get_sorted_rankings():
            f.write(f"  {get_tactic_name(entity)}: {rating:.0f}\n")

    print(f"\nАнализ сохранён в: {output_file}")

    return df, elo_tactics


if __name__ == "__main__":
    df, elo = analyze_results()
