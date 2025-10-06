"""
전체 시스템 재실행 스크립트
1. 오래된 perception/worldview 데이터 삭제
2. 현재 버전의 PerceptionExtractor로 재실행
3. WorldviewDetector 재실행
4. Deconstruction 실행
"""
import asyncio
from engines.utils.supabase_client import get_supabase
from engines.extractors.perception_extractor import PerceptionExtractor
from engines.analyzers.worldview_detector import WorldviewDetector
from engines.deconstructors.deconstruction_engine import DeconstructionEngine

async def main():
    supabase = get_supabase()

    print("=" * 80)
    print("전체 시스템 재실행")
    print("=" * 80)

    # Step 1: 기존 데이터 삭제
    print("\n[Step 1] 기존 perception/worldview 데이터 삭제...")

    # Delete worldviews first (foreign key)
    worldviews = supabase.table('worldviews').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"  ✅ Worldviews 삭제 완료")

    # Delete perceptions
    perceptions = supabase.table('perceptions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"  ✅ Perceptions 삭제 완료")

    # Delete connections
    connections = supabase.table('perception_connections').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"  ✅ Connections 삭제 완료")

    # Step 2: Content 가져오기 (상위 20개만)
    print("\n[Step 2] Content 조회...")
    contents = supabase.table('contents').select('id').limit(20).execute()
    content_ids = [c['id'] for c in contents.data]
    print(f"  ✅ {len(content_ids)}개 contents 조회")

    # Step 3: PerceptionExtractor 재실행
    print("\n[Step 3] PerceptionExtractor 실행...")
    extractor = PerceptionExtractor()

    all_perception_ids = []
    for i, content_id in enumerate(content_ids, 1):
        print(f"  [{i}/{len(content_ids)}] Processing {content_id}...")
        perception_ids = await extractor.extract(content_id)
        all_perception_ids.extend(perception_ids)
        print(f"    → {len(perception_ids)}개 perceptions 추출")

    print(f"\n  ✅ 총 {len(all_perception_ids)}개 perceptions 생성")

    # Step 4: ConnectionDetector는 스킵 (너무 많은 connections)
    print("\n[Step 4] ConnectionDetector 스킵 (worldview 탐지에 영향 없음)")

    # Step 5: WorldviewDetector 실행
    print("\n[Step 5] WorldviewDetector 실행...")
    detector = WorldviewDetector()
    worldview_ids = await detector.detect_worldviews()
    print(f"  ✅ {len(worldview_ids)}개 worldviews 탐지")

    # Fetch worldview details
    worldviews = []
    for wv_id in worldview_ids:
        wv = supabase.table('worldviews').select('*').eq('id', str(wv_id)).execute()
        if wv.data:
            worldviews.append(wv.data[0])
            print(f"    - {wv.data[0]['title']}")
            print(f"      Frame: {wv.data[0]['frame']}")
            print(f"      Perceptions: {wv.data[0]['total_perceptions']}개")

    # Step 6: Deconstruction 실행
    print("\n[Step 6] Deconstruction 실행...")
    engine = DeconstructionEngine()

    for wv in worldviews:
        print(f"\n  Deconstructing: {wv['title']}")
        result = await engine.deconstruct(wv['id'], save_to_db=True)
        print(f"    ✅ {len(result.get('flaws', []))}개 결함 탐지")
        print(f"    ✅ {len(result.get('counter_narrative', ''))}자 대안 서사 생성")

    print("\n" + "=" * 80)
    print("✅ 전체 재실행 완료")
    print("=" * 80)

    # Final stats
    final_perceptions = supabase.table('perceptions').select('id', count='exact').execute()
    final_worldviews = supabase.table('worldviews').select('id', count='exact').execute()

    print(f"\n최종 통계:")
    print(f"  - Perceptions: {final_perceptions.count}개")
    print(f"  - Worldviews: {final_worldviews.count}개")

if __name__ == '__main__':
    asyncio.run(main())
