"""
GPT-5-mini vs GPT-5 최종 비교
- 3-Layer 분석 품질
- 세계관 구성 품질
- 비용 효율성
"""

import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from engines.utils.supabase_client import get_supabase

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def test_3layer_analysis():
    """3-Layer 분석 품질 비교"""

    supabase = get_supabase()

    # 테스트 샘플 1개
    sample = supabase.table('contents').select('title, body').neq('body', '').limit(1).execute().data[0]

    prompt = f"""다음 DC Inside 게시글을 3-Layer로 분석하세요.

제목: {sample['title']}
본문: {sample['body'][:500]}

분석 결과를 다음 형식으로 반환하세요:
1. Explicit Claims (표면적 주장) - 3개
2. Implicit Assumptions (암묵적 전제) - 3개
3. Deep Beliefs (심층 믿음) - 3개
4. Worldview Hints (세계관 힌트) - 간략히
"""

    print("\n" + "="*80)
    print("1️⃣  3-Layer 분석 품질 비교")
    print("="*80)
    print(f"\n테스트 글: \"{sample['title'][:60]}...\"")

    # GPT-5-mini
    print("\n🔵 GPT-5-mini 분석...")
    mini_resp = await client.chat.completions.create(
        model='gpt-5-mini',
        messages=[
            {'role': 'system', 'content': '당신은 정치 담론 분석 전문가입니다.'},
            {'role': 'user', 'content': prompt}
        ]
    )

    print(f"\n[GPT-5-mini 결과]")
    print(mini_resp.choices[0].message.content[:400] + "...")
    mini_tokens = mini_resp.usage.total_tokens
    mini_cost = mini_tokens / 1000 * 0.0001

    # GPT-5
    print("\n🟢 GPT-5 분석...")
    full_resp = await client.chat.completions.create(
        model='gpt-5',
        messages=[
            {'role': 'system', 'content': '당신은 정치 담론 분석 전문가입니다.'},
            {'role': 'user', 'content': prompt}
        ]
    )

    print(f"\n[GPT-5 결과]")
    print(full_resp.choices[0].message.content[:400] + "...")
    full_tokens = full_resp.usage.total_tokens
    full_cost = full_tokens / 1000 * 0.003

    print(f"\n📊 비교:")
    print(f"  토큰: mini {mini_tokens} vs full {full_tokens}")
    print(f"  비용: ${mini_cost:.6f} vs ${full_cost:.6f} (차이: {full_cost/mini_cost:.1f}x)")

    return {
        'mini_cost': mini_cost,
        'full_cost': full_cost,
        'mini_tokens': mini_tokens,
        'full_tokens': full_tokens
    }

async def test_worldview_construction():
    """세계관 구성 품질 비교"""

    supabase = get_supabase()

    # 샘플 deep beliefs 수집
    lps = supabase.table('layered_perceptions').select('deep_beliefs').limit(20).execute().data
    all_beliefs = []
    for lp in lps:
        if lp.get('deep_beliefs'):
            all_beliefs.extend(lp['deep_beliefs'][:2])

    beliefs_text = "\n".join([f"- {b}" for b in all_beliefs[:15]])

    prompt = f"""다음은 DC Inside에서 추출한 deep beliefs입니다:

{beliefs_text}

이 믿음들을 분석하여:
1. 주요 세계관 2-3개를 도출하세요
2. 각 세계관의 핵심 특징을 설명하세요
3. 왜 이런 세계관이 형성되었는지 분석하세요

간결하게 답변하세요.
"""

    print("\n" + "="*80)
    print("2️⃣  세계관 구성 품질 비교")
    print("="*80)

    # GPT-5-mini
    print("\n🔵 GPT-5-mini 분석...")
    mini_resp = await client.chat.completions.create(
        model='gpt-5-mini',
        messages=[
            {'role': 'system', 'content': '당신은 세계관 분석 전문가입니다.'},
            {'role': 'user', 'content': prompt}
        ]
    )

    print(f"\n[GPT-5-mini 결과]")
    print(mini_resp.choices[0].message.content[:500] + "...")
    mini_tokens = mini_resp.usage.total_tokens
    mini_cost = mini_tokens / 1000 * 0.0001

    # GPT-5
    print("\n🟢 GPT-5 분석...")
    full_resp = await client.chat.completions.create(
        model='gpt-5',
        messages=[
            {'role': 'system', 'content': '당신은 세계관 분석 전문가입니다.'},
            {'role': 'user', 'content': prompt}
        ]
    )

    print(f"\n[GPT-5 결과]")
    print(full_resp.choices[0].message.content[:500] + "...")
    full_tokens = full_resp.usage.total_tokens
    full_cost = full_tokens / 1000 * 0.003

    print(f"\n📊 비교:")
    print(f"  토큰: mini {mini_tokens} vs full {full_tokens}")
    print(f"  비용: ${mini_cost:.6f} vs ${full_cost:.6f} (차이: {full_cost/mini_cost:.1f}x)")

    return {
        'mini_cost': mini_cost,
        'full_cost': full_cost
    }

async def main():
    print("\n" + "="*80)
    print("GPT-5-mini vs GPT-5 최종 비교 시뮬레이션")
    print("="*80)

    # 1. 3-Layer 분석 비교
    layer_results = await test_3layer_analysis()

    await asyncio.sleep(2)

    # 2. 세계관 구성 비교
    worldview_results = await test_worldview_construction()

    # 최종 결론
    print("\n" + "="*80)
    print("💡 최종 결론")
    print("="*80)

    # 비용 계산
    print("\n📊 비용 분석 (월간, 일 100개 분석 기준):")

    layer_mini_monthly = layer_results['mini_cost'] * 100 * 30
    layer_full_monthly = layer_results['full_cost'] * 100 * 30

    print(f"\n3-Layer 분석:")
    print(f"  GPT-5-mini: ${layer_mini_monthly:.2f}/월")
    print(f"  GPT-5: ${layer_full_monthly:.2f}/월")
    print(f"  차이: {layer_full_monthly/layer_mini_monthly:.1f}x")

    wv_mini_monthly = worldview_results['mini_cost'] * 4  # 주 1회
    wv_full_monthly = worldview_results['full_cost'] * 4

    print(f"\n세계관 구성 (주 1회):")
    print(f"  GPT-5-mini: ${wv_mini_monthly:.2f}/월")
    print(f"  GPT-5: ${wv_full_monthly:.2f}/월")
    print(f"  차이: {wv_full_monthly/wv_mini_monthly:.1f}x")

    total_mini = layer_mini_monthly + wv_mini_monthly
    total_full = layer_full_monthly + wv_full_monthly

    print(f"\n총 월간 비용:")
    print(f"  GPT-5-mini: ${total_mini:.2f}")
    print(f"  GPT-5: ${total_full:.2f}")
    print(f"  차이: ${total_full - total_mini:.2f} ({(total_full/total_mini):.1f}x)")

    print("\n" + "="*80)
    print("✅ 권장 사항")
    print("="*80)

    if total_full < 50:
        print("\n현재 규모(일 100개)에서는 GPT-5 사용 권장:")
        print("  - 비용 차이가 크지 않음 ($50 이하)")
        print("  - 품질 우선 시 GPT-5가 더 나은 인사이트 제공")
    elif total_full / total_mini > 30:
        print("\n현재 규모에서는 GPT-5-mini 사용 권장:")
        print(f"  - 비용이 30배 이상 차이남")
        print(f"  - 대량 분석에서는 mini도 충분한 품질")
        print(f"  - 중요한 분석만 GPT-5 사용하는 하이브리드 전략 고려")
    else:
        print("\n하이브리드 전략 권장:")
        print("  - 3-Layer 분석: GPT-5-mini (대량 처리)")
        print("  - 세계관 구성: GPT-5 (품질 우선)")
        print(f"  - 예상 비용: ${layer_mini_monthly + wv_full_monthly:.2f}/월")

    print("\n" + "="*80)

asyncio.run(main())
