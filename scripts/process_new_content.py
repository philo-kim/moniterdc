"""
신규 Content 처리 스크립트

Crawler가 새 content 수집 시 자동 실행:
1. Reasoning structure 추출
2. 기존 세계관에 매칭
3. 매칭 실패 시 임시 보관
"""

import asyncio
from engines.analyzers.reasoning_structure_extractor import ReasoningStructureExtractor
from engines.analyzers.mechanism_matcher import MechanismMatcher
from engines.utils.supabase_client import get_supabase


async def process_new_contents(limit: int = None):
    """
    Process new contents that don't have reasoning structures yet

    Args:
        limit: Maximum number of contents to process (None = all new contents)
    """

    print("="*80)
    print("신규 Content 처리")
    print("="*80)

    # Step 1: Extract reasoning structures
    print("\n[Step 1] Reasoning Structure 추출")
    print("-"*80)

    extractor = ReasoningStructureExtractor()
    perception_ids = await extractor.extract_all_new(limit=limit)

    if not perception_ids:
        print("\n처리할 새 content가 없습니다.")
        return

    print(f"\n✅ {len(perception_ids)}개 perception 생성")

    # Step 2: Match to worldviews
    print("\n[Step 2] Worldview 매칭")
    print("-"*80)

    matcher = MechanismMatcher()
    supabase = get_supabase()

    matched_count = 0
    unmatched_ids = []

    for perception_id in perception_ids:
        matched_worldviews = await matcher.match_single_perception(str(perception_id), threshold=0.4)

        if matched_worldviews:
            matched_count += 1
        else:
            unmatched_ids.append(str(perception_id))

    print(f"\n✅ {matched_count}개 매칭 완료")

    if unmatched_ids:
        print(f"⚠️  {len(unmatched_ids)}개 매칭 실패 (임시 보관)")

        # Mark as unmatched for later review
        for pid in unmatched_ids:
            # Could add to a separate table or flag field
            pass

    # Summary
    print("\n" + "="*80)
    print("처리 완료")
    print("="*80)
    print(f"\n총 처리: {len(perception_ids)}개")
    print(f"매칭 성공: {matched_count}개 ({matched_count/len(perception_ids)*100:.1f}%)")
    print(f"매칭 실패: {len(unmatched_ids)}개 ({len(unmatched_ids)/len(perception_ids)*100:.1f}%)")

    if unmatched_ids:
        print(f"\n⚠️  매칭되지 않은 perception이 있습니다.")
        print(f"   다음 진화 사이클에서 재매칭됩니다.")


async def main():
    """Main entry point"""
    await process_new_contents()


if __name__ == "__main__":
    asyncio.run(main())
