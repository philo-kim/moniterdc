"""
Test BeliefNormalizer - 먼저 작은 샘플로 테스트
"""

import asyncio
from engines.analyzers.belief_normalizer import BeliefNormalizer

async def main():
    normalizer = BeliefNormalizer()

    print("="*80)
    print("🧪 BeliefNormalizer 미리보기 테스트")
    print("="*80)

    # Preview with 20 samples (smaller for faster testing)
    await normalizer.show_normalization_preview(sample_size=20)

    print("\n" + "="*80)
    print("✅ 미리보기 완료")
    print("="*80)
    print("\n만족스러우면 전체 실행:")
    print("  PYTHONPATH=. python3 run_belief_normalization.py")

if __name__ == '__main__':
    asyncio.run(main())
