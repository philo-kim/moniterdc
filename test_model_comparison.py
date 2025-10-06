"""
GPT-5-mini vs GPT-5 성능 비교 시뮬레이션

목적: 3-Layer 분석에서 어떤 모델이 더 적합한지 검증
"""

import asyncio
from openai import AsyncOpenAI
import os
from engines.utils.supabase_client import get_supabase
import json

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def analyze_with_model(content_title: str, content_body: str, model: str) -> dict:
    """특정 모델로 3-Layer 분석"""

    prompt = f"""다음 DC Inside 게시글을 3-Layer로 분석하세요.

제목: {content_title}
본문: {content_body}

분석 결과를 다음 JSON 형식으로 반환하세요:
{{
    "explicit_claims": [
        {{"subject": "주체", "predicate": "서술", "quote": "인용"}}
    ],
    "implicit_assumptions": ["암묵적 전제1", "암묵적 전제2"],
    "deep_beliefs": ["심층 믿음1", "심층 믿음2"],
    "worldview_hints": "세계관 힌트"
}}"""

    # GPT-5는 temperature 파라미터를 지원하지 않음
    params = {
        "model": model,
        "messages": [
            {"role": "system", "content": "당신은 정치 담론 분석 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    response = await client.chat.completions.create(**params)

    result = json.loads(response.choices[0].message.content)

    return {
        "model": model,
        "result": result,
        "tokens_used": response.usage.total_tokens,
        "cost_estimate": calculate_cost(response.usage.total_tokens, model)
    }

def calculate_cost(tokens: int, model: str) -> float:
    """토큰 기반 비용 계산 (추정치)"""
    # GPT-5 pricing (추정)
    if "mini" in model:
        cost_per_1k = 0.0001  # $0.0001/1k tokens
    else:
        cost_per_1k = 0.003   # $0.003/1k tokens

    return (tokens / 1000) * cost_per_1k

async def compare_models():
    """두 모델 비교"""

    supabase = get_supabase()

    # 테스트용 샘플 1개 선택 (빠른 테스트)
    samples = supabase.table('contents').select('id, title, body').neq('body', '').limit(1).execute().data

    print("\n" + "="*80)
    print("GPT-5-mini vs GPT-5 성능 비교 시뮬레이션")
    print("="*80)
    print(f"\n테스트 샘플: {len(samples)}개")
    print("\n목적: 3-Layer 분석에서 어떤 모델이 더 적합한지 검증")
    print("기준: 1) 분석 깊이, 2) 비용 효율성, 3) 일관성")
    print("="*80)

    comparison_results = []

    for i, sample in enumerate(samples, 1):
        print(f"\n{'='*80}")
        print(f"샘플 {i}: \"{sample['title'][:50]}...\"")
        print(f"{'='*80}")

        # GPT-5-mini로 분석
        print("\n🔵 GPT-5-mini 분석 중...")
        mini_result = await analyze_with_model(sample['title'], sample['body'][:1000], "gpt-5-mini")

        # GPT-5로 분석
        print("🟢 GPT-5 분석 중...")
        full_result = await analyze_with_model(sample['title'], sample['body'][:1000], "gpt-5")

        # 결과 비교
        print("\n" + "-"*80)
        print("📊 분석 결과 비교:")
        print("-"*80)

        print(f"\n[GPT-5-mini]")
        print(f"  Deep Beliefs 개수: {len(mini_result['result'].get('deep_beliefs', []))}개")
        print(f"  토큰 사용: {mini_result['tokens_used']}개")
        print(f"  예상 비용: ${mini_result['cost_estimate']:.4f}")
        print(f"  Deep Beliefs 예시:")
        for j, belief in enumerate(mini_result['result'].get('deep_beliefs', [])[:2], 1):
            print(f"    {j}. {belief[:80]}...")

        print(f"\n[GPT-5]")
        print(f"  Deep Beliefs 개수: {len(full_result['result'].get('deep_beliefs', []))}개")
        print(f"  토큰 사용: {full_result['tokens_used']}개")
        print(f"  예상 비용: ${full_result['cost_estimate']:.4f}")
        print(f"  Deep Beliefs 예시:")
        for j, belief in enumerate(full_result['result'].get('deep_beliefs', [])[:2], 1):
            print(f"    {j}. {belief[:80]}...")

        comparison_results.append({
            "sample_id": sample['id'],
            "title": sample['title'],
            "mini": mini_result,
            "full": full_result
        })

        await asyncio.sleep(1)  # Rate limiting

    # 전체 통계
    print("\n" + "="*80)
    print("📈 전체 통계")
    print("="*80)

    total_mini_cost = sum(r['mini']['cost_estimate'] for r in comparison_results)
    total_full_cost = sum(r['full']['cost_estimate'] for r in comparison_results)

    avg_mini_beliefs = sum(len(r['mini']['result'].get('deep_beliefs', [])) for r in comparison_results) / len(comparison_results)
    avg_full_beliefs = sum(len(r['full']['result'].get('deep_beliefs', [])) for r in comparison_results) / len(comparison_results)

    print(f"\n평균 Deep Beliefs 개수:")
    print(f"  GPT-5-mini: {avg_mini_beliefs:.1f}개")
    print(f"  GPT-5: {avg_full_beliefs:.1f}개")

    print(f"\n총 비용 (3개 샘플):")
    print(f"  GPT-5-mini: ${total_mini_cost:.4f}")
    print(f"  GPT-5: ${total_full_cost:.4f}")
    print(f"  비용 차이: {total_full_cost / total_mini_cost:.1f}x")

    print(f"\n예상 월간 비용 (일 100개 분석 기준):")
    print(f"  GPT-5-mini: ${(total_mini_cost / len(comparison_results) * 100 * 30):.2f}")
    print(f"  GPT-5: ${(total_full_cost / len(comparison_results) * 100 * 30):.2f}")

    # 결론
    print("\n" + "="*80)
    print("💡 결론")
    print("="*80)

    quality_diff = avg_full_beliefs / avg_mini_beliefs if avg_mini_beliefs > 0 else 1
    cost_ratio = total_full_cost / total_mini_cost if total_mini_cost > 0 else 1

    print(f"\n품질 차이: GPT-5가 {quality_diff:.1f}x 더 많은 Deep Beliefs 추출")
    print(f"비용 차이: GPT-5가 {cost_ratio:.1f}x 더 비쌈")

    if quality_diff > 1.5 and cost_ratio < 10:
        print("\n✅ 권장: GPT-5")
        print("   이유: 품질 향상이 비용 증가를 정당화함")
    elif cost_ratio > 20:
        print("\n✅ 권장: GPT-5-mini")
        print("   이유: 비용 대비 품질이 충분함")
    else:
        print("\n⚖️  권장: 상황에 따라 선택")
        print(f"   - 대량 분석: GPT-5-mini (비용 효율)")
        print(f"   - 정밀 분석: GPT-5 (품질 우선)")

    print("\n" + "="*80)

    return comparison_results

if __name__ == '__main__':
    asyncio.run(compare_models())
