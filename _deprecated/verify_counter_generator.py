"""
Step 2: CounterNarrativeGenerator 로직 검증
실제 worldview로 대안 서사 생성이 작동하는지 확인
"""
import asyncio
from engines.utils.supabase_client import get_supabase
from engines.deconstructors.flaw_detector import FlawDetector
from engines.deconstructors.counter_narrative_generator import CounterNarrativeGenerator

async def verify_counter_generator():
    print("=" * 60)
    print("Step 2: CounterNarrativeGenerator 로직 검증")
    print("=" * 60)

    supabase = get_supabase()
    detector = FlawDetector()
    generator = CounterNarrativeGenerator()

    # 1. worldview + perceptions 가져오기
    print("\n[1] 실제 데이터 조회...")
    worldviews = supabase.table('worldviews').select('*').limit(1).execute()
    worldview = worldviews.data[0]

    perception_ids = worldview.get('perception_ids', [])
    perceptions_data = supabase.table('perceptions').select('*').in_('id', perception_ids).execute()
    perceptions = perceptions_data.data

    print(f"✅ Worldview: {worldview['title']}")
    print(f"✅ Perceptions: {len(perceptions)}개")

    # 2. 결함 탐지 (generator에 필요)
    print("\n[2] 결함 탐지 (대안 서사에 필요)...")
    flaws = await detector.detect_flaws(worldview, perceptions)
    print(f"✅ {len(flaws)}개 결함 탐지됨")

    # 3. Counter-narrative 생성 테스트
    print("\n[3] Counter-narrative 생성...")
    try:
        counter_narrative = await generator._generate_counter_narrative(worldview, perceptions, flaws)
        print(f"✅ Counter-narrative 생성 완료")
        print(f"   길이: {len(counter_narrative)} 문자")
        print(f"   내용 샘플: {counter_narrative[:150]}...")
    except Exception as e:
        print(f"❌ Counter-narrative 생성 실패: {e}")
        return

    # 4. Rebuttals 생성 테스트
    print("\n[4] 핵심 반박 논리 생성...")
    try:
        rebuttals = await generator._generate_rebuttals(worldview, flaws)
        print(f"✅ {len(rebuttals)}개 반박 논리 생성")
        for i, rebuttal in enumerate(rebuttals[:2], 1):
            print(f"   {i}. {rebuttal[:80]}...")
    except Exception as e:
        print(f"❌ Rebuttals 생성 실패: {e}")
        return

    # 5. Suggested response 생성 테스트
    print("\n[5] 구체적 대응 방안 생성...")
    try:
        response = await generator._generate_suggested_response(worldview, flaws)
        print(f"✅ Suggested response 생성 완료")
        print(f"   길이: {len(response)} 문자")
        print(f"   내용 샘플: {response[:150]}...")
    except Exception as e:
        print(f"❌ Suggested response 생성 실패: {e}")
        return

    # 6. 전체 통합 생성 테스트
    print("\n[6] 전체 대안 서사 패키지 생성...")
    try:
        result = await generator.generate(worldview, perceptions, flaws)
        print(f"✅ 전체 패키지 생성 완료")
        print(f"\n   구성 요소:")
        print(f"   - counter_narrative: {len(result['counter_narrative'])} 문자")
        print(f"   - key_rebuttals: {len(result['key_rebuttals'])}개")
        print(f"   - suggested_response: {len(result['suggested_response'])} 문자")
        print(f"   - evidence_needed: {len(result['evidence_needed'])}개")
        ag = result['action_guide']
        ag_count = len(ag) if isinstance(ag, (list, dict)) else 0
        print(f"   - action_guide: {ag_count}개 항목")
    except Exception as e:
        print(f"❌ 전체 패키지 생성 실패: {e}")
        return

    # 7. 생성 결과 상세 출력
    print("\n[7] 생성 결과 상세:")
    print(f"\n   --- Counter Narrative ---")
    print(f"   {result['counter_narrative'][:300]}...")

    print(f"\n   --- Key Rebuttals (상위 2개) ---")
    for i, reb in enumerate(result['key_rebuttals'][:2], 1):
        print(f"   {i}. {reb}")

    print(f"\n   --- Evidence Needed (상위 2개) ---")
    for i, ev in enumerate(result['evidence_needed'][:2], 1):
        print(f"   {i}. {ev}")

    print(f"\n   --- Action Guide ---")
    action_guide = result['action_guide']
    if isinstance(action_guide, dict):
        for key, value in list(action_guide.items())[:2]:
            print(f"   {key}: {value}")
    elif isinstance(action_guide, list):
        for i, action in enumerate(action_guide[:2], 1):
            print(f"   {i}. {action}")

    print("\n" + "=" * 60)
    print("✅ CounterNarrativeGenerator 로직 검증 완료")
    print("=" * 60)

    return result

if __name__ == '__main__':
    asyncio.run(verify_counter_generator())
