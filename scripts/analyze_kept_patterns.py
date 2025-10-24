"""
Analyze Kept Patterns Quality

Uses Claude to evaluate the quality of patterns that PASSED filtering
to see if we're still letting through bad patterns.
"""

import sys
import os
import anthropic
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.utils.supabase_client import get_supabase

claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def apply_filtering_rules(text: str) -> bool:
    """Apply filtering rules"""
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
    print("Kept Patterns Quality Analysis")
    print("="*80 + "\n")

    supabase = get_supabase()

    # Get sample perceptions
    result = supabase.table('layered_perceptions').select(
        'explicit_claims'
    ).limit(50).execute()

    perceptions = result.data

    # Extract surface items and filter
    surface_items = []
    for p in perceptions:
        claims = p.get('explicit_claims', [])
        surface_items.extend(claims)

    kept = [item for item in surface_items if apply_filtering_rules(item)]

    print(f"총 표면층 아이템: {len(surface_items)}개")
    print(f"필터링 통과: {len(kept)}개\n")

    # Use Claude to evaluate kept patterns
    pattern_list = "\n".join([f"{i+1}. {p}" for i, p in enumerate(kept)])

    prompt = f"""당신은 패턴 품질 평가 전문가입니다.

아래는 필터링을 통과한 표면층 패턴들입니다.
각 패턴을 평가하여 **의미없거나 정보가치가 낮은 패턴**을 식별하세요.

패턴 목록:
{pattern_list}

나쁜 패턴의 특징:
1. 주어가 불명확 (누가?)
2. 내용이 모호함 (무엇을?)
3. 너무 짧고 정보가 없음
4. 당위적/규범적 ("~해야", "~하자")
5. 일반론적 ("상황이 복잡하다" 등)

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

    print("="*80)
    print("Claude 평가 결과")
    print("="*80 + "\n")

    print(result_text)

    # Parse JSON
    try:
        # Extract JSON from markdown code blocks if present
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            json_str = result_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = result_text

        result_data = json.loads(json_str)
        bad_patterns = result_data.get('bad_patterns', [])

        print(f"\n{'='*80}")
        print(f"통계")
        print(f"{'='*80}\n")

        print(f"전체 패턴: {len(kept)}개")
        print(f"나쁜 패턴: {len(bad_patterns)}개")
        print(f"나쁜 패턴 비율: {len(bad_patterns)/len(kept)*100:.1f}%\n")

        print(f"{'='*80}")
        print(f"나쁜 패턴 상세")
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
