"""
Step 3: DeconstructionEngine 통합 로직 검증
FlawDetector + CounterNarrativeGenerator 통합이 제대로 작동하는지 확인
"""
import asyncio
from engines.utils.supabase_client import get_supabase
from engines.deconstructors.deconstruction_engine import DeconstructionEngine

async def verify_deconstruction_engine():
    print("=" * 60)
    print("Step 3: DeconstructionEngine 통합 로직 검증")
    print("=" * 60)

    supabase = get_supabase()
    engine = DeconstructionEngine()

    # 1. worldview 가져오기
    print("\n[1] 실제 worldview 조회...")
    worldviews = supabase.table('worldviews').select('*').limit(1).execute()
    worldview_id = worldviews.data[0]['id']
    worldview_title = worldviews.data[0]['title']

    print(f"✅ Worldview ID: {worldview_id}")
    print(f"   Title: {worldview_title}")

    # 2. DB 저장 없이 분석만 실행
    print("\n[2] DeconstructionEngine 실행 (DB 저장 안함)...")
    try:
        result = await engine.deconstruct(worldview_id, save_to_db=False)
        print(f"✅ Deconstruction 완료")
    except Exception as e:
        print(f"❌ Deconstruction 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. 결과 구조 검증
    print("\n[3] 결과 구조 검증...")
    expected_keys = [
        'flaws', 'counter_narrative', 'key_rebuttals',
        'suggested_response', 'evidence_needed', 'action_guide',
        'generated_at'
    ]

    for key in expected_keys:
        if key in result:
            print(f"   ✅ {key}: 존재")
        else:
            print(f"   ❌ {key}: 누락")

    # 4. Structural flaws 검증
    print("\n[4] Structural Flaws 검증...")
    flaws = result.get('flaws', [])
    print(f"   총 {len(flaws)}개 결함")

    if flaws:
        print(f"\n   결함 타입 분포:")
        flaw_types = {}
        for flaw in flaws:
            flaw_type = flaw.get('type', 'unknown')
            flaw_types[flaw_type] = flaw_types.get(flaw_type, 0) + 1

        for flaw_type, count in sorted(flaw_types.items(), key=lambda x: -x[1]):
            print(f"     - {flaw_type}: {count}개")

        print(f"\n   샘플 결함:")
        sample_flaw = flaws[0]
        print(f"     타입: {sample_flaw.get('type')}")
        print(f"     심각도: {sample_flaw.get('severity')}")
        print(f"     설명: {sample_flaw.get('description')[:60]}...")

    # 5. Counter-narrative 검증
    print("\n[5] Counter-Narrative 검증...")
    narrative = result.get('counter_narrative', '')
    print(f"   타입: {type(narrative).__name__}")
    print(f"   길이: {len(narrative)} 문자")
    if narrative:
        print(f"   샘플: {narrative[:100]}...")

    # 6. Key rebuttals 검증
    print("\n[6] Key Rebuttals 검증...")
    key_rebuttals = result.get('key_rebuttals', [])
    print(f"   개수: {len(key_rebuttals)}개")
    if key_rebuttals:
        print(f"   샘플: {key_rebuttals[0][:60]}...")

    # 7. Evidence needed 검증
    print("\n[7] Evidence Needed 검증...")
    evidence_needed = result.get('evidence_needed', [])
    print(f"   개수: {len(evidence_needed)}개")
    if evidence_needed:
        print(f"   샘플: {evidence_needed[0][:60]}...")

    # 8. Suggested response 검증
    print("\n[8] Suggested Response 검증...")
    suggested_response = result.get('suggested_response', '')
    print(f"   길이: {len(suggested_response)} 문자")
    if suggested_response:
        print(f"   샘플: {suggested_response[:60]}...")

    # 9. Action guide 검증
    print("\n[9] Action Guide 검증...")
    action_guide = result.get('action_guide', {})
    ag_count = len(action_guide) if isinstance(action_guide, (list, dict)) else 0
    print(f"   항목 수: {ag_count}개")

    # 10. DB 저장 테스트
    print("\n[10] DB 저장 테스트...")
    try:
        result_with_save = await engine.deconstruct(worldview_id, save_to_db=True)
        print(f"✅ DB 저장 성공")

        # 저장 확인
        updated_wv = supabase.table('worldviews').select('deconstruction').eq('id', worldview_id).execute()
        if updated_wv.data and updated_wv.data[0]['deconstruction']:
            print(f"✅ DB에서 deconstruction 필드 확인됨")
            saved_deconstruction = updated_wv.data[0]['deconstruction']
            print(f"   저장된 데이터 크기: {len(str(saved_deconstruction))} 문자")
        else:
            print(f"❌ DB에 deconstruction 필드 없음")

    except Exception as e:
        print(f"❌ DB 저장 실패: {e}")

    print("\n" + "=" * 60)
    print("✅ DeconstructionEngine 통합 로직 검증 완료")
    print("=" * 60)

    return result

if __name__ == '__main__':
    asyncio.run(verify_deconstruction_engine())
