"""
Test Different Pattern Quality Evaluation Approaches

Tests 3 approaches on real patterns to find the best method:
1. Semantic Distinctiveness - 다른 세계관과의 변별력
2. Worldview Contribution - 세계관 논리 구조에 대한 기여도
3. Information Value - 정보의 구체성과 가치

Each approach is tested with Claude, and results are compared.
"""

import sys
import os
from datetime import datetime
import anthropic

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.utils.supabase_client import get_supabase

# Claude setup
claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def get_sample_patterns(worldview_id: str, layer: str, limit: int = 20):
    """Get sample patterns for testing"""
    supabase = get_supabase()

    result = supabase.table('worldview_patterns').select(
        'id, text, strength, appearance_count'
    ).eq('worldview_id', worldview_id).eq('layer', layer).eq(
        'status', 'active'
    ).order('strength', desc=True).limit(limit).execute()

    return result.data


def approach_1_distinctiveness(patterns, worldview_title):
    """
    접근법 1: 의미적 변별력

    이 패턴이 이 세계관을 다른 세계관과 구별하는데 기여하는가?
    """

    pattern_texts = [f"{i+1}. {p['text']}" for i, p in enumerate(patterns)]

    prompt = f"""
당신은 담론 분석 전문가입니다.

세계관: "{worldview_title}"
아래 패턴들의 **의미적 변별력**을 평가해주세요.

패턴들:
{chr(10).join(pattern_texts)}

각 패턴에 대해:
- 변별력 점수 (0.0-1.0): 이 세계관을 다른 세계관과 구별하는데 기여하는 정도
- 이유: 왜 그 점수를 주었는지

평가 기준:
- 1.0: 이 세계관만의 독특한 특징 (예: "좌파는 본질적으로 독재적")
- 0.5: 일부 세계관에서 공통 (예: "정치는 복잡하다")
- 0.0: 모든 세계관에 공통 (예: "사람들이 말한다")

응답 형식 (JSON):
{{
  "scores": [
    {{"id": 1, "score": 0.9, "reason": "이 세계관의 핵심 특징"}},
    ...
  ]
}}
"""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def approach_2_contribution(patterns, worldview_title, layer):
    """
    접근법 2: 세계관 기여도

    이 패턴이 세계관의 논리 구조를 이해하는데 필수적인가?
    """

    pattern_texts = [f"{i+1}. {p['text']}" for i, p in enumerate(patterns)]

    layer_description = {
        'surface': '구체적 사건/주장들',
        'implicit': '전제되는 가정들',
        'deep': '근본적 믿음들'
    }

    prompt = f"""
당신은 담론 분석 전문가입니다.

세계관: "{worldview_title}"
레이어: {layer_description[layer]}

아래 패턴들의 **세계관 기여도**를 평가해주세요.

패턴들:
{chr(10).join(pattern_texts)}

각 패턴에 대해:
- 기여도 점수 (0.0-1.0): 이 세계관을 이해하는데 필수적인 정도
- 이유: 왜 그 점수를 주었는지

평가 기준:
- 1.0: 이 패턴 없이는 세계관 이해 불가능 (핵심 논리)
- 0.5: 있으면 도움되지만 필수는 아님
- 0.0: 제거해도 세계관 이해에 영향 없음 (부차적 정보)

이 레이어의 역할:
- surface: 세계관이 주목하는 사건/현상
- implicit: 세계관의 논리 전제
- deep: 세계관의 존재 이유

응답 형식 (JSON):
{{
  "scores": [
    {{"id": 1, "score": 0.9, "reason": "세계관의 핵심 논리"}},
    ...
  ]
}}
"""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def approach_3_information_value(patterns, layer):
    """
    접근법 3: 정보 가치

    이 패턴이 얼마나 구체적이고 정보량이 많은가?
    """

    pattern_texts = [f"{i+1}. {p['text']}" for i, p in enumerate(patterns)]

    layer_expectations = {
        'surface': '구체적 사건, 주장, 행위 (예: "민주당이 통신사를 협박했다")',
        'implicit': '명확한 전제/가정 (예: "당국이 극좌와 한편이다")',
        'deep': '근본적 믿음 (예: "좌파는 본질적으로 독재적이다")'
    }

    prompt = f"""
당신은 정보 이론 전문가입니다.

레이어: {layer}
기대되는 패턴: {layer_expectations[layer]}

아래 패턴들의 **정보 가치**를 평가해주세요.

패턴들:
{chr(10).join(pattern_texts)}

각 패턴에 대해:
- 정보 가치 점수 (0.0-1.0)
- 이유: 왜 그 점수를 주었는지

평가 기준:
- 1.0: 구체적이고 명확한 주장/믿음 (정보량 높음)
- 0.5: 어느 정도 구체적이지만 모호함
- 0.0: 너무 일반적이거나 의미 불명 (정보량 거의 없음)

체크 포인트:
✓ 구체성: 누가, 무엇을, 왜 명확한가?
✓ 명확성: 주장/믿음이 분명한가?
✓ 적절성: 이 레이어에 맞는 내용인가?
✗ 너무 짧거나 길지 않은가?
✗ 의미가 불명확하지 않은가?

응답 형식 (JSON):
{{
  "scores": [
    {{"id": 1, "score": 0.9, "reason": "구체적이고 명확한 주장"}},
    ...
  ]
}}
"""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def main():
    print(f"\n{'='*80}")
    print(f"Pattern Quality Evaluation - 3 Approaches Comparison")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    supabase = get_supabase()

    # Get test worldview
    worldview_id = '72494546-0243-43f8-91d5-3a6c24791951'
    wv = supabase.table('worldviews').select('title').eq('id', worldview_id).single().execute()
    worldview_title = wv.data['title']

    print(f"세계관: {worldview_title}")
    print(f"ID: {worldview_id}\n")

    # Test on deep layer (가장 중요한 레이어)
    layer = 'deep'
    print(f"테스트 레이어: {layer} (심층 - 근본 믿음)\n")

    patterns = get_sample_patterns(worldview_id, layer, limit=15)
    print(f"샘플 패턴 {len(patterns)}개:\n")

    for i, p in enumerate(patterns[:5], 1):
        print(f"{i}. [{p['strength']:.1f}, {p['appearance_count']}회] {p['text']}")
    print(f"... (총 {len(patterns)}개)\n")

    print("="*80)
    print("접근법 1: 의미적 변별력 (Semantic Distinctiveness)")
    print("="*80)
    print("평가 중...\n")

    result_1 = approach_1_distinctiveness(patterns, worldview_title)
    print(result_1)
    print("\n")

    print("="*80)
    print("접근법 2: 세계관 기여도 (Worldview Contribution)")
    print("="*80)
    print("평가 중...\n")

    result_2 = approach_2_contribution(patterns, worldview_title, layer)
    print(result_2)
    print("\n")

    print("="*80)
    print("접근법 3: 정보 가치 (Information Value)")
    print("="*80)
    print("평가 중...\n")

    result_3 = approach_3_information_value(patterns, layer)
    print(result_3)
    print("\n")

    print("="*80)
    print("비교 완료")
    print("="*80)
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n결과를 검토하고 가장 효과적인 접근법을 선택하세요.")
    print("각 접근법이 어떤 패턴을 높게/낮게 평가했는지 비교해보세요.\n")


if __name__ == '__main__':
    main()
