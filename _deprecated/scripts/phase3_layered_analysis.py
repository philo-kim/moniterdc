"""
Phase 3: 3층 구조 분석

297개 글을 각각:
- 표면층: 명시적 주장
- 암묵층: 전제하는 사고
- 심층: 무의식적 믿음

으로 분석하여 layered_perceptions 테이블에 저장
"""

import asyncio
from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor
from engines.utils.supabase_client import get_supabase

async def main():
    print("="*80)
    print("Phase 3: 3층 구조 분석")
    print("="*80)

    supabase = get_supabase()
    extractor = LayeredPerceptionExtractor()

    # 현재 상태 확인
    total_contents = supabase.table('contents').select('id', count='exact').neq('body', '').execute()
    total = total_contents.count or 0

    existing_perceptions = supabase.table('layered_perceptions').select('id', count='exact').execute()
    existing = existing_perceptions.count or 0

    print(f"\n전체 contents: {total}개")
    print(f"이미 분석됨: {existing}개")
    print(f"분석 필요: {total - existing}개")

    if total - existing == 0:
        print("\n✅ 이미 모두 분석 완료")
        return

    # 배치 처리 (안전)
    print(f"\n[3.1] 배치 분석 시작 (10개씩)")
    print("-"*80)

    # 분석되지 않은 contents 찾기
    analyzed_ids = [p['content_id'] for p in supabase.table('layered_perceptions').select('content_id').execute().data]

    contents_to_analyze = supabase.table('contents')\
        .select('id, title, body')\
        .neq('body', '')\
        .execute().data

    # 이미 분석된 것 제외
    to_analyze = [c for c in contents_to_analyze if c['id'] not in analyzed_ids]

    print(f"분석 대상: {len(to_analyze)}개")

    batch_size = 10
    total_batches = (len(to_analyze) + batch_size - 1) // batch_size

    success_count = 0
    error_count = 0

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(to_analyze))
        batch = to_analyze[start_idx:end_idx]

        print(f"\n배치 {batch_num + 1}/{total_batches} ({len(batch)}개)")

        for i, content in enumerate(batch, 1):
            try:
                print(f"  [{start_idx + i}/{len(to_analyze)}] {content['title'][:40]}...", end=' ')

                perception_id = await extractor.extract(content)

                print("✅")
                success_count += 1

            except Exception as e:
                print(f"❌ {str(e)[:50]}")
                error_count += 1
                continue

        # 배치 간 대기 (API rate limit 고려)
        if batch_num < total_batches - 1:
            print(f"  ⏳ 1초 대기...")
            await asyncio.sleep(1)

    # 최종 결과
    print("\n" + "="*80)
    print("Phase 3 완료")
    print("="*80)

    final_count = supabase.table('layered_perceptions').select('id', count='exact').execute()
    final = final_count.count or 0

    print(f"\n성공: {success_count}개")
    print(f"실패: {error_count}개")
    print(f"최종: {final}개 layered_perceptions 생성")

    if final >= total * 0.9:
        print("\n✅ 충분한 분석 완료 (90% 이상)")
        print("\n다음 단계: Phase 4 (패턴 탐지)")
        print("  실행: python3 phase4_pattern_detection.py")
    else:
        print(f"\n⚠️ 분석 부족 ({final}/{total} = {final/total*100:.0f}%)")
        print("재실행 권장")

    print("="*80)

if __name__ == '__main__':
    asyncio.run(main())
