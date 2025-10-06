"""
Rebuild belief_patterns from layered_perceptions
"""

import asyncio
from engines.utils.supabase_client import get_supabase

async def main():
    supabase = get_supabase()

    print("="*80)
    print("🔧 belief_patterns 재구축")
    print("="*80)

    # 1. Get all deep_beliefs from layered_perceptions
    print("\n1️⃣  layered_perceptions에서 deep_beliefs 추출...")

    layered = supabase.table('layered_perceptions')\
        .select('id, content_id, deep_beliefs')\
        .execute().data

    print(f"✅ {len(layered)}개 레코드")

    # 2. Count belief frequencies
    print("\n2️⃣  믿음 빈도 계산...")

    belief_freq = {}  # belief_text -> {frequency, content_ids}

    for lp in layered:
        deep = lp.get('deep_beliefs', [])
        content_id = lp['content_id']

        for belief in deep:
            if belief not in belief_freq:
                belief_freq[belief] = {
                    'frequency': 0,
                    'content_ids': []
                }
            belief_freq[belief]['frequency'] += 1
            belief_freq[belief]['content_ids'].append(content_id)

    print(f"✅ {len(belief_freq)}개 고유 믿음")

    # 3. Insert into belief_patterns
    print("\n3️⃣  belief_patterns에 저장...")

    total_contents = len(layered)
    patterns = []

    for belief_text, data in belief_freq.items():
        percentage = (data['frequency'] / total_contents * 100) if total_contents > 0 else 0

        patterns.append({
            'belief': belief_text,
            'frequency': data['frequency'],
            'percentage': round(percentage, 2),
            'example_content_ids': data['content_ids'][:10],  # Max 10 examples
            'cluster_id': None,
            'cluster_name': None
        })

    if patterns:
        supabase.table('belief_patterns').insert(patterns).execute()

    print(f"✅ {len(patterns)}개 패턴 저장 완료")

    # 4. Show stats
    print("\n" + "="*80)
    print("📊 통계")
    print("="*80)

    freq_1 = len([p for p in patterns if p['frequency'] == 1])
    freq_2_5 = len([p for p in patterns if 2 <= p['frequency'] <= 5])
    freq_6_plus = len([p for p in patterns if p['frequency'] >= 6])

    print(f"\n빈도 분포:")
    print(f"  1회: {freq_1}개 ({freq_1/len(patterns)*100:.1f}%)")
    print(f"  2-5회: {freq_2_5}개 ({freq_2_5/len(patterns)*100:.1f}%)")
    print(f"  6회+: {freq_6_plus}개 ({freq_6_plus/len(patterns)*100:.1f}%)")

    print(f"\n🔥 상위 10개:")
    top10 = sorted(patterns, key=lambda x: x['frequency'], reverse=True)[:10]
    for i, p in enumerate(top10, 1):
        print(f"{i:2d}. [{p['frequency']:3d}회, {p['percentage']:5.1f}%] {p['belief'][:60]}...")

    print("\n" + "="*80)
    print("✅ 재구축 완료!")
    print("="*80)
    print("\n다음: PYTHONPATH=. python3 run_belief_normalization.py")

if __name__ == '__main__':
    asyncio.run(main())
