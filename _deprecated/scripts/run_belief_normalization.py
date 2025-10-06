"""
Run BeliefNormalizer - 전체 889개 믿음 정규화
"""

import asyncio
from engines.analyzers.belief_normalizer import BeliefNormalizer

async def main():
    normalizer = BeliefNormalizer()

    print("="*80)
    print("🚀 전체 믿음 정규화 시작")
    print("="*80)
    print("\n⚠️  이 작업은 약 10-15분 소요될 수 있습니다.")
    print("    (889개 믿음을 20개씩 배치 처리)")
    print()

    # Run normalization
    stats = await normalizer.normalize_all_beliefs(batch_size=20)

    print("\n" + "="*80)
    print("✅ 정규화 완료!")
    print("="*80)

    print(f"\n📊 통계:")
    print(f"  원본 믿음 수: {stats['original_count']}개")
    print(f"  정규화 후: {stats['normalized_count']}개")
    print(f"  축소율: {stats['reduction_rate']:.1f}%")

    print(f"\n🔥 상위 10개 핵심 믿음:")
    for i, belief in enumerate(stats['top_10'], 1):
        print(f"\n{i:2d}. [{belief['frequency']:3d}회, {belief['percentage']:5.1f}%]")
        print(f"    {belief['belief'][:100]}{'...' if len(belief['belief']) > 100 else ''}")

    print("\n" + "="*80)
    print("🎯 다음 단계: Phase 5 - WorldviewSynthesizer")
    print("="*80)

if __name__ == '__main__':
    asyncio.run(main())
