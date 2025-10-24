"""
Test Enhanced Fast Filter

Tests the improved rule-based filtering to see if it catches more bad patterns.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.utils.supabase_client import get_supabase


def enhanced_fast_filter(text: str) -> tuple[bool, str]:
    """
    Enhanced fast filter with improved rules

    Returns: (should_keep, reason_if_filtered)
    """
    text_clean = text.strip()

    # 1. 길이 체크 (더 엄격하게)
    if len(text_clean) < 10:
        return (False, "길이 < 10")

    # 2. 지시대명사로 시작 (확장)
    pronouns = ['이는', '이것은', '이것이', '그것은', '그것이',
                '이', '그', '저', '여기', '거기']
    for p in pronouns:
        if text_clean.startswith(p + ' ') or text_clean.startswith(p + '은') or text_clean.startswith(p + '는') or text_clean.startswith(p + '가'):
            return (False, f"지시대명사 시작: {p}")

    # 3. 대명사 주어 (확장)
    vague_subjects = ['우리가', '우리는', '이들은', '이들이', '그들은', '그들이',
                      '엄마들이', '좌파들이', '보수들이', '사람들이']
    for s in vague_subjects:
        if text_clean.startswith(s):
            return (False, f"막연한 주어: {s}")

    # 4. 당위문/규범문
    normative = ['해야 한다', '해야한다', '하자', '드리자',
                 '말아야', '않을 것이다', '안 될', '되어야']
    for n in normative:
        if n in text_clean:
            return (False, f"당위문: {n}")

    # 5. 막연한 평가/감정 (구체적 주어 없으면 제거)
    vague_eval = ['웃기다', '다행', '부당', '적절', '나쁜', '좋은',
                  '이상하다', '복잡하다', '어렵다', '쉽다']

    # 구체적 주어 체크
    concrete_subjects = ['민주당', '국민의힘', '윤석열', '이재명',
                        '경찰', '검찰', '법원', '정부', '국회',
                        '대통령', '의원', '장관', '판사', '검사']

    has_concrete_subject = any(subj in text_clean for subj in concrete_subjects)

    if not has_concrete_subject:
        for v in vague_eval:
            if v in text_clean:
                return (False, f"막연한 평가: {v}")

    # 6. 불완전한 문장 (서술어 없음)
    if not any(end in text_clean for end in ['다', '까', '냐', '요', '음', '야']):
        return (False, "불완전한 문장")

    # 7. 특수문자/이니셜만 (ㅉ, ㅁㅈ 등)
    # 한글/영문/숫자 비율이 80% 미만이면 제거
    alnum_count = sum(1 for c in text_clean if c.isalnum() or '\uac00' <= c <= '\ud7a3')
    if alnum_count < len(text_clean) * 0.8:
        return (False, "특수문자 과다")

    return (True, "")


def old_fast_filter(text: str) -> bool:
    """Original simple filter for comparison"""
    text_clean = text.strip()

    if len(text_clean) < 8:
        return False
    if any(text_clean.startswith(word) for word in ['우리', '이들', '그들', '이것', '그것']):
        return False
    if any(word in text_clean for word in ['해야 한다', '해야한다', '하자', '드리자']):
        return False

    return True


def main():
    print("\n" + "="*80)
    print("Enhanced Fast Filter Test")
    print("="*80 + "\n")

    supabase = get_supabase()

    # Get sample perceptions
    result = supabase.table('layered_perceptions').select(
        'explicit_claims'
    ).limit(50).execute()

    perceptions = result.data

    # Extract surface items
    surface_items = []
    for p in perceptions:
        claims = p.get('explicit_claims', [])
        surface_items.extend(claims)

    print(f"총 표면층 아이템: {len(surface_items)}개\n")

    # Test old filter
    old_kept = [item for item in surface_items if old_fast_filter(item)]
    old_filtered = len(surface_items) - len(old_kept)

    # Test new filter
    new_results = [enhanced_fast_filter(item) for item in surface_items]
    new_kept = [surface_items[i] for i, (keep, _) in enumerate(new_results) if keep]
    new_filtered_items = [(surface_items[i], reason) for i, (keep, reason) in enumerate(new_results) if not keep]

    print(f"{'='*80}")
    print(f"필터링 비교")
    print(f"{'='*80}\n")

    print(f"기존 필터:")
    print(f"  ✅ 유지: {len(old_kept)}개 ({len(old_kept)/len(surface_items)*100:.1f}%)")
    print(f"  ❌ 걸러짐: {old_filtered}개 ({old_filtered/len(surface_items)*100:.1f}%)\n")

    print(f"강화된 필터:")
    print(f"  ✅ 유지: {len(new_kept)}개 ({len(new_kept)/len(surface_items)*100:.1f}%)")
    print(f"  ❌ 걸러짐: {len(new_filtered_items)}개 ({len(new_filtered_items)/len(surface_items)*100:.1f}%)\n")

    print(f"개선:")
    print(f"  추가로 걸러낸 패턴: {len(new_filtered_items) - old_filtered}개")

    # Show newly filtered patterns
    print(f"\n{'='*80}")
    print(f"강화된 필터가 추가로 걸러낸 패턴들")
    print(f"{'='*80}\n")

    # Find patterns filtered by new but not old
    newly_filtered = [(text, reason) for text, reason in new_filtered_items
                      if text in old_kept]

    for i, (text, reason) in enumerate(newly_filtered, 1):
        print(f"{i}. [{reason}] {text}")

    # Show all filtered patterns with reasons
    print(f"\n{'='*80}")
    print(f"모든 걸러진 패턴 (이유별)")
    print(f"{'='*80}\n")

    # Group by reason
    by_reason = {}
    for text, reason in new_filtered_items:
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(text)

    for reason, patterns in sorted(by_reason.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{reason}: {len(patterns)}개")
        for p in patterns[:5]:  # Show first 5
            print(f"  - {p}")
        if len(patterns) > 5:
            print(f"  ... (+{len(patterns)-5}개 더)")

    # Show kept patterns sample
    print(f"\n{'='*80}")
    print(f"유지된 패턴 샘플 (처음 15개)")
    print(f"{'='*80}\n")

    for i, item in enumerate(new_kept[:15], 1):
        print(f"{i}. {item}")

    print(f"\n{'='*80}")
    print(f"다음 단계: Claude로 유지된 패턴 검증")
    print(f"{'='*80}\n")

    print(f"강화된 필터를 통과한 {len(new_kept)}개 패턴 중")
    print(f"여전히 나쁜 패턴이 몇 개 남아있는지 Claude로 확인 필요\n")


if __name__ == '__main__':
    main()
