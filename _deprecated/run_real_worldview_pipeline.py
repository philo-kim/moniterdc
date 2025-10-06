"""
진짜 세계관 분석 파이프라인
기존: 수집 → Perception 추출 → 연결 탐지 → 세계관 그룹핑
새로운: 수집 → 세계관 직접 분석 (인과/대립/감정/전제)
"""
import asyncio
from engines.utils.supabase_client import get_supabase
from engines.analyzers.worldview_analyzer import WorldviewAnalyzer
from engines.deconstructors.deconstruction_engine import DeconstructionEngine
import json

async def main():
    print("=" * 80)
    print("진짜 세계관 분석 파이프라인")
    print("=" * 80)

    supabase = get_supabase()
    analyzer = WorldviewAnalyzer()
    deconstructor = DeconstructionEngine()

    # Step 1: 기존 worldview 삭제
    print("\n[Step 1] 기존 worldview 삭제...")
    supabase.table('worldviews').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print("  ✅ 완료")

    # Step 2: Contents 조회
    print("\n[Step 2] Contents 조회...")
    contents = supabase.table('contents').select('*').neq('body', '').execute().data
    print(f"  ✅ {len(contents)}개 contents 조회")

    # Step 3: 세계관 분석
    print("\n[Step 3] 세계관 분석 중...")
    worldview_ids = await analyzer.detect_worldviews()
    print(f"  ✅ {len(worldview_ids)}개 worldview 탐지")

    # Step 4: 결과 출력
    print("\n" + "=" * 80)
    print("탐지된 세계관")
    print("=" * 80)

    for wv_id in worldview_ids:
        wv = supabase.table('worldviews').select('*').eq('id', str(wv_id)).execute().data[0]

        print(f"\n제목: {wv['title']}")
        print(f"\n대립 구도:")
        frame = json.loads(wv['frame']) if isinstance(wv['frame'], str) else wv['frame']
        print(f"  우리: {', '.join(frame.get('us', {}).get('identity', []))}")
        print(f"  적: {', '.join(frame.get('them', {}).get('identity', []))}")

        print(f"\n인과 구조: {len(wv.get('cognitive_mechanisms', []))}개")
        for i, chain in enumerate(wv.get('cognitive_mechanisms', [])[:2], 1):
            print(f"  [{i}] {' → '.join(chain['chain'])}")

        print(f"\n감정 논리: {len(wv.get('formation_phases', []))}개")
        for i, emo in enumerate(wv.get('formation_phases', [])[:2], 1):
            print(f"  [{i}] {emo.get('emotion', '')}: {emo.get('conclusion', '')}")

        print(f"\n암묵적 전제: {len(wv.get('structural_flaws', []))}개")
        for i, assumption in enumerate(wv.get('structural_flaws', [])[:2], 1):
            print(f"  [{i}] {assumption.get('assumption', '')}")

        print(f"\n전체 서사:")
        print(f"  {wv.get('description', '')[:200]}...")

    # Step 5: Deconstruction
    print("\n" + "=" * 80)
    print("[Step 5] Deconstruction 실행")
    print("=" * 80)

    for wv_id in worldview_ids:
        wv = supabase.table('worldviews').select('title').eq('id', str(wv_id)).execute().data[0]
        print(f"\n해체 중: {wv['title']}")

        result = await deconstructor.deconstruct(wv_id, save_to_db=True)

        print(f"  ✅ 결함: {len(result.get('flaws', []))}개")
        print(f"  ✅ 대안 서사: {len(result.get('counter_narrative', ''))}자")

    print("\n" + "=" * 80)
    print("✅ 전체 파이프라인 완료")
    print("=" * 80)

if __name__ == '__main__':
    asyncio.run(main())
