"""
Comprehensive Pattern Quality Test

Tests all 3 approaches across:
- All 3 layers (surface, implicit, deep)
- Multiple worldviews
- With actual filtering comparison

Goal: Find which approach ACTUALLY improves pattern quality
"""

import sys
import os
from datetime import datetime
import anthropic
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.utils.supabase_client import get_supabase

claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def evaluate_approach(patterns, worldview_title, layer, approach_name, prompt_template):
    """Generic evaluation function"""

    pattern_texts = [f"{i+1}. [{p['strength']:.1f}, {p['appearance_count']}회] {p['text']}"
                     for i, p in enumerate(patterns)]

    prompt = prompt_template.format(
        worldview=worldview_title,
        layer=layer,
        patterns=chr(10).join(pattern_texts)
    )

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def test_single_layer(worldview_id, worldview_title, layer, sample_size=20):
    """Test all approaches on one layer"""

    print(f"\n{'='*80}")
    print(f"테스트: {worldview_title} / {layer.upper()}")
    print(f"{'='*80}\n")

    supabase = get_supabase()

    # Get patterns
    result = supabase.table('worldview_patterns').select(
        'id, text, strength, appearance_count'
    ).eq('worldview_id', worldview_id).eq('layer', layer).eq(
        'status', 'active'
    ).order('strength', desc=True).limit(sample_size).execute()

    patterns = result.data

    if len(patterns) < 5:
        print(f"⚠️  패턴 부족 ({len(patterns)}개), 스킵\n")
        return None

    print(f"샘플: {len(patterns)}개 패턴\n")

    # Approach 1: Distinctiveness
    print("접근법 1: 의미적 변별력...")
    prompt1 = """
세계관: "{worldview}"
레이어: {layer}

아래 패턴들의 의미적 변별력(이 세계관만의 독특함)을 0.0-1.0으로 평가하세요.

{patterns}

JSON만 출력:
{{"scores": [{{"id": 1, "score": 0.8}}, ...]}}
"""
    result1 = evaluate_approach(patterns, worldview_title, layer, "distinctiveness", prompt1)

    # Approach 2: Contribution
    print("접근법 2: 세계관 기여도...")
    prompt2 = """
세계관: "{worldview}"
레이어: {layer}

아래 패턴들의 세계관 기여도(세계관 이해에 필수적인 정도)를 0.0-1.0으로 평가하세요.

{patterns}

JSON만 출력:
{{"scores": [{{"id": 1, "score": 0.9}}, ...]}}
"""
    result2 = evaluate_approach(patterns, worldview_title, layer, "contribution", prompt2)

    # Approach 3: Information Value
    print("접근법 3: 정보 가치...")
    prompt3 = """
레이어: {layer}

아래 패턴들의 정보 가치(구체성과 명확성)를 0.0-1.0으로 평가하세요.

{patterns}

JSON만 출력:
{{"scores": [{{"id": 1, "score": 0.7}}, ...]}}
"""
    result3 = evaluate_approach(patterns, worldview_title, layer, "information_value", prompt3)

    print("\n평가 완료\n")

    return {
        'worldview': worldview_title,
        'layer': layer,
        'patterns': patterns,
        'distinctiveness': result1,
        'contribution': result2,
        'information_value': result3
    }


def analyze_results(all_results):
    """
    실제로 어떤 접근법이 좋은 패턴을 선택하는지 분석
    """

    print("\n" + "="*80)
    print("종합 분석: 어떤 접근법이 효과적인가?")
    print("="*80 + "\n")

    for result in all_results:
        if not result:
            continue

        print(f"\n{result['worldview']} / {result['layer'].upper()}")
        print("-" * 60)

        try:
            scores1 = json.loads(result['distinctiveness'])['scores']
            scores2 = json.loads(result['contribution'])['scores']
            scores3 = json.loads(result['information_value'])['scores']

            # Top 5 from each approach
            top_distinctiveness = sorted(scores1, key=lambda x: x['score'], reverse=True)[:5]
            top_contribution = sorted(scores2, key=lambda x: x['score'], reverse=True)[:5]
            top_information = sorted(scores3, key=lambda x: x['score'], reverse=True)[:5]

            print("\n접근법 1 (변별력) Top 5:")
            for s in top_distinctiveness:
                pattern = result['patterns'][s['id']-1]
                print(f"  {s['score']:.1f} - {pattern['text'][:50]}...")

            print("\n접근법 2 (기여도) Top 5:")
            for s in top_contribution:
                pattern = result['patterns'][s['id']-1]
                print(f"  {s['score']:.1f} - {pattern['text'][:50]}...")

            print("\n접근법 3 (정보가치) Top 5:")
            for s in top_information:
                pattern = result['patterns'][s['id']-1]
                print(f"  {s['score']:.1f} - {pattern['text'][:50]}...")

        except Exception as e:
            print(f"⚠️  분석 실패: {str(e)}")


def main():
    print(f"\n{'='*80}")
    print(f"Comprehensive Pattern Quality Evaluation")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    supabase = get_supabase()

    # Get worldviews with patterns
    result = supabase.rpc('exec', {
        'query': '''
            SELECT w.id, w.title, COUNT(DISTINCT wp.id) as pattern_count
            FROM worldviews w
            LEFT JOIN worldview_patterns wp ON w.id = wp.worldview_id
            WHERE wp.status IN ('active', 'fading')
            GROUP BY w.id, w.title
            HAVING COUNT(DISTINCT wp.id) > 50
            ORDER BY pattern_count DESC
            LIMIT 3
        '''
    }).execute()

    if not result.data:
        # Fallback: just get worldviews with most patterns
        patterns_result = supabase.table('worldview_patterns').select('worldview_id').eq('status', 'active').execute()

        # Count by worldview
        from collections import Counter
        wv_counts = Counter([p['worldview_id'] for p in patterns_result.data])
        top_wvs = wv_counts.most_common(2)

        test_worldviews = []
        for wv_id, count in top_wvs:
            wv = supabase.table('worldviews').select('id, title').eq('id', wv_id).single().execute()
            test_worldviews.append((wv.data['id'], wv.data['title']))
    else:
        test_worldviews = [(w['id'], w['title']) for w in result.data[:2]]

    print(f"테스트 세계관 {len(test_worldviews)}개:")
    for wv_id, title in test_worldviews:
        print(f"  - {title}")
    print()

    all_results = []

    # Test each worldview on all 3 layers
    for wv_id, wv_title in test_worldviews:
        for layer in ['surface', 'implicit', 'deep']:
            result = test_single_layer(wv_id, wv_title, layer, sample_size=15)
            all_results.append(result)

    # Analyze
    analyze_results(all_results)

    print("\n" + "="*80)
    print("테스트 완료")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    print("결론: 각 레이어별로 어떤 접근법이 좋은 패턴을 선택했는지 비교하세요.")


if __name__ == '__main__':
    main()
