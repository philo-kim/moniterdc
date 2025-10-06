#!/usr/bin/env python3
"""
GPT-5 기반 전체 분석 실행

3단계:
1. 3-layer perception 분석 (GPT-5)
2. Worldview 구성 (GPT-5)
3. Hybrid matching

진행 상황을 실시간으로 출력
"""

import asyncio
import sys
from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor
from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor
from engines.analyzers.worldview_updater import WorldviewUpdater
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("=" * 60)
    print("GPT-5 기반 전체 분석 실행")
    print("=" * 60)

    # Step 1: 3-layer perception analysis
    print("\n[1/3] 3-Layer Perception 분석 (GPT-5)")
    print("-" * 60)
    extractor = LayeredPerceptionExtractor()
    perception_ids = await extractor.extract_all(limit=100, batch_size=10)
    print(f"\n✅ {len(perception_ids)}개 perception 생성완료")

    # Step 2: Worldview construction
    print("\n\n[2/3] Worldview 구성 (GPT-5)")
    print("-" * 60)
    constructor = OptimalWorldviewConstructor()
    stats = await constructor.construct_all()
    print(f"\n✅ {stats['worldviews_created']}개 worldview 생성완료")

    # Step 3: Hybrid matching
    print("\n\n[3/3] Hybrid Matching (Perception → Worldview)")
    print("-" * 60)
    updater = WorldviewUpdater()
    link_stats = await updater.match_all_perceptions()
    print(f"\n✅ {link_stats['total_links']}개 링크 생성완료")

    print("\n" + "=" * 60)
    print("전체 분석 완료!")
    print("=" * 60)
    print(f"Perceptions: {len(perception_ids)}")
    print(f"Worldviews: {stats['worldviews_created']}")
    print(f"Links: {link_stats['total_links']}")
    print("\nDashboard: http://localhost:3000")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n중단됨")
        sys.exit(0)
