"""
Test Pattern Filtering Effectiveness

Tests the filtering rules implemented in PatternManager.create_pattern()
to validate they actually remove bad patterns while keeping good ones.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.utils.supabase_client import get_supabase


def apply_filtering_rules(text: str) -> bool:
    """
    Apply the same filtering rules as PatternManager.create_pattern()

    Returns:
        True if pattern should be KEPT, False if FILTERED OUT
    """
    text_clean = text.strip()

    # 1. 너무 짧은 패턴
    if len(text_clean) < 8:
        return False

    # 2. 대명사만 시작하는 패턴 필터링
    if any(text_clean.startswith(word) for word in ['우리', '이들', '그들', '이것', '그것']):
        return False

    # 3. 당위문 필터링
    if any(word in text_clean for word in ['해야 한다', '해야한다', '하자', '드리자']):
        return False

    return True


def main():
    print("\n" + "="*80)
    print("Pattern Filtering Effectiveness Test")
    print("="*80 + "\n")

    supabase = get_supabase()

    # Get sample perceptions (first 50)
    result = supabase.table('layered_perceptions').select(
        'explicit_claims, implicit_assumptions, deep_beliefs'
    ).limit(50).execute()

    perceptions = result.data

    print(f"테스트 샘플: {len(perceptions)}개 perception\n")

    # Extract all surface layer items (explicit_claims)
    surface_items = []
    for p in perceptions:
        claims = p.get('explicit_claims', [])
        surface_items.extend(claims)

    print(f"총 표면층 아이템: {len(surface_items)}개\n")

    # Apply filtering
    kept = []
    filtered = []

    for item in surface_items:
        if apply_filtering_rules(item):
            kept.append(item)
        else:
            filtered.append(item)

    print(f"{'='*80}")
    print(f"필터링 결과")
    print(f"{'='*80}\n")

    print(f"✅ 유지된 패턴: {len(kept)}개 ({len(kept)/len(surface_items)*100:.1f}%)")
    print(f"❌ 걸러진 패턴: {len(filtered)}개 ({len(filtered)/len(surface_items)*100:.1f}%)\n")

    # Show filtered patterns
    print(f"{'='*80}")
    print(f"걸러진 패턴 샘플 (처음 20개)")
    print(f"{'='*80}\n")

    for i, item in enumerate(filtered[:20], 1):
        # Identify why it was filtered
        reason = []
        if len(item.strip()) < 8:
            reason.append("길이 < 8")
        if any(item.strip().startswith(word) for word in ['우리', '이들', '그들', '이것', '그것']):
            reason.append("대명사 시작")
        if any(word in item for word in ['해야 한다', '해야한다', '하자', '드리자']):
            reason.append("당위문")

        print(f"{i}. [{', '.join(reason)}] {item}")

    print(f"\n{'='*80}")
    print(f"유지된 패턴 샘플 (처음 20개)")
    print(f"{'='*80}\n")

    for i, item in enumerate(kept[:20], 1):
        print(f"{i}. {item}")

    # Manual review prompt
    print(f"\n{'='*80}")
    print(f"수동 검증")
    print(f"{'='*80}\n")

    print("위 결과를 보고 판단하세요:")
    print("1. 걸러진 패턴들이 실제로 무의미한가?")
    print("2. 유지된 패턴들이 의미있는가?")
    print("3. 좋은 패턴이 걸러지거나, 나쁜 패턴이 유지되지는 않았는가?\n")

    # Statistics by filter type
    print(f"{'='*80}")
    print(f"필터링 이유별 통계")
    print(f"{'='*80}\n")

    filter_stats = {
        '길이 < 8': 0,
        '대명사 시작': 0,
        '당위문': 0
    }

    for item in filtered:
        if len(item.strip()) < 8:
            filter_stats['길이 < 8'] += 1
        if any(item.strip().startswith(word) for word in ['우리', '이들', '그들', '이것', '그것']):
            filter_stats['대명사 시작'] += 1
        if any(word in item for word in ['해야 한다', '해야한다', '하자', '드리자']):
            filter_stats['당위문'] += 1

    for reason, count in filter_stats.items():
        print(f"{reason}: {count}개")

    print("\n" + "="*80)
    print("테스트 완료")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
