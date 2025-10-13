"""
Mechanism Matcher 실행 스크립트

layered_perceptions와 worldviews를 연결
Actor + Mechanism 기반 매칭
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.analyzers.mechanism_matcher import MechanismMatcher


async def main():
    print("="*80)
    print("MECHANISM MATCHER - Perception-Worldview 연결")
    print("="*80)

    matcher = MechanismMatcher()

    # Run matching with threshold 0.4
    links_created = await matcher.match_all_perceptions(threshold=0.4)

    print("\n" + "="*80)
    print("완료")
    print("="*80)
    print(f"\n총 {links_created}개 링크 생성")


if __name__ == "__main__":
    asyncio.run(main())
