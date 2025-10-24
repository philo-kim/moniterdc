"""
Test Enhanced Fast Filter v2

Fixed version with corrected special character check
"""

import sys
import os
import anthropic

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.utils.supabase_client import get_supabase

claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def enhanced_fast_filter_v2(text: str) -> tuple[bool, str]:
    """
    Enhanced fast filter v2 - fixed special character check

    Returns: (should_keep, reason_if_filtered)
    """
    text_clean = text.strip()

    # 1. 길이 체크
    if len(text_clean) < 10:
        return (False, "길이 < 10")

    # 2. 지시대명사로 시작
    pronouns_start = [
        '이는 ', '이는,', '이것은 ', '이것이 ', '그것은 ', '그것이 ',
        '여기는 ', '거기는 ', '저기는 '
    ]
    for p in pronouns_start:
        if text_clean.startswith(p):
            return (False, f"지시대명사 시작")

    # 지시대명사 단독 (끝에 조사)
    if text_clean.startswith('이 ') or text_clean.startswith('그 ') or text_clean.startswith('저 '):
        # 단, "이 사건", "이 사람" 같은 경우는 허용
        if not any(text_clean.startswith(p) for p in ['이 사건', '이 사람', '이 일', '그 사건', '그 사람']):
            return (False, f"지시대명사 시작")

    # 3. 대명사/막연한 주어로 시작
    vague_subjects = [
        '우리가 ', '우리는 ', '이들은 ', '이들이 ', '그들은 ', '그들이 ',
        '엄마들이 ', '좌파들이 ', '보수들이 ', '사람들이 '
    ]
    for s in vague_subjects:
        if text_clean.startswith(s):
            return (False, f"막연한 주어")

    # 4. 당위문/규범문
    normative = ['해야 한다', '해야한다', '하자', '드리자', '말아야', '되어야']
    for n in normative:
        if n in text_clean:
            return (False, f"당위문")

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
                return (False, f"막연한 평가")

    # 6. 불완전한 문장 (서술어 없음)
    # 한국어 종결어미 체크
    endings = ['다.', '다,', '다"', '다\'', '다!', '다?',
               '까.', '까,', '까?',
               '냐.', '냐,', '냐?',
               '요.', '요,', '요!',
               '음.', '음,']

    # 문장 끝에 종결어미가 있는지 체크
    has_ending = any(text_clean.endswith(end) for end in endings)

    # 또는 '다'로 끝나는지 (마침표 없어도)
    if not has_ending and not text_clean.endswith('다'):
        return (False, "불완전한 문장")

    # 7. 특수문자만 있는 이니셜 (ㅉ, ㅁㅈ 등)
    # 한글 자음만 있는 패턴
    korean_consonants = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    if any(c in korean_consonants for c in text_clean[:3]):
        return (False, "자음 이니셜")

    return (True, "")


def main():
    print("\n" + "="*80)
    print("Enhanced Fast Filter v2 Test (Fixed)")
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

    # Test v2 filter
    v2_results = [enhanced_fast_filter_v2(item) for item in surface_items]
    v2_kept = [surface_items[i] for i, (keep, _) in enumerate(v2_results) if keep]
    v2_filtered_items = [(surface_items[i], reason) for i, (keep, reason) in enumerate(v2_results) if not keep]

    print(f"{'='*80}")
    print(f"V2 필터링 결과")
    print(f"{'='*80}\n")

    print(f"✅ 유지: {len(v2_kept)}개 ({len(v2_kept)/len(surface_items)*100:.1f}%)")
    print(f"❌ 걸러짐: {len(v2_filtered_items)}개 ({len(v2_filtered_items)/len(surface_items)*100:.1f}%)\n")

    # Group by reason
    print(f"{'='*80}")
    print(f"걸러진 패턴 (이유별)")
    print(f"{'='*80}\n")

    by_reason = {}
    for text, reason in v2_filtered_items:
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(text)

    for reason, patterns in sorted(by_reason.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{reason}: {len(patterns)}개")
        for p in patterns:
            print(f"  - {p}")

    # Show kept patterns
    print(f"\n{'='*80}")
    print(f"유지된 패턴 샘플 (처음 20개)")
    print(f"{'='*80}\n")

    for i, item in enumerate(v2_kept[:20], 1):
        print(f"{i}. {item}")

    # Now use Claude to check kept patterns
    print(f"\n{'='*80}")
    print(f"Claude 검증: 유지된 패턴 중 나쁜 패턴 찾기")
    print(f"{'='*80}\n")

    pattern_list = "\n".join([f"{i+1}. {p}" for i, p in enumerate(v2_kept)])

    prompt = f"""당신은 패턴 품질 평가 전문가입니다.

아래는 필터링을 통과한 표면층 패턴들입니다.
각 패턴을 평가하여 **의미없거나 정보가치가 낮은 패턴**을 식별하세요.

패턴 목록:
{pattern_list}

나쁜 패턴의 특징:
1. 주어가 불명확 (누가?)
2. 내용이 모호함 (무엇을?)
3. 너무 짧고 정보가 없음
4. 단순한 평가/감정 ("웃기다", "적절하다")
5. 일반론적 ("흐름이 바뀌고 있다" 등)

각 패턴을 평가하고, **나쁜 패턴**만 JSON 배열로 출력하세요:

{{
  "bad_patterns": [
    {{"id": 번호, "text": "패턴 내용", "reason": "이유"}},
    ...
  ]
}}

좋은 패턴은 출력하지 마세요. 나쁜 패턴만 출력하세요."""

    print("Claude로 품질 평가 중...\n")

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    print(result_text)

    # Parse JSON
    try:
        import json

        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = result_text

        result_data = json.loads(json_str)
        bad_patterns = result_data.get('bad_patterns', [])

        print(f"\n{'='*80}")
        print(f"최종 통계")
        print(f"{'='*80}\n")

        print(f"전체 패턴: {len(surface_items)}개")
        print(f"Fast filter 통과: {len(v2_kept)}개 ({len(v2_kept)/len(surface_items)*100:.1f}%)")
        print(f"Fast filter 제거: {len(v2_filtered_items)}개 ({len(v2_filtered_items)/len(surface_items)*100:.1f}%)")
        print(f"Claude가 찾은 추가 나쁜 패턴: {len(bad_patterns)}개 ({len(bad_patterns)/len(v2_kept)*100:.1f}%)")
        print(f"\n최종 좋은 패턴: {len(v2_kept) - len(bad_patterns)}개")
        print(f"최종 나쁜 패턴: {len(v2_filtered_items) + len(bad_patterns)}개")
        print(f"\n나쁜 패턴 비율: {(len(v2_filtered_items) + len(bad_patterns))/len(surface_items)*100:.1f}%\n")

        if bad_patterns:
            print(f"{'='*80}")
            print(f"Fast filter가 놓친 나쁜 패턴들")
            print(f"{'='*80}\n")

            for bp in bad_patterns:
                print(f"{bp['id']}. {bp['text']}")
                print(f"   이유: {bp['reason']}\n")

    except Exception as e:
        print(f"\n⚠️  JSON 파싱 실패: {str(e)}")

    print("="*80)
    print("분석 완료")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
