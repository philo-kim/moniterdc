"""
Step 1: FlawDetector 로직 검증
실제 worldview로 결함 탐지가 작동하는지 확인
"""
import asyncio
from engines.utils.supabase_client import get_supabase
from engines.deconstructors.flaw_detector import FlawDetector

async def verify_flaw_detector():
    print("=" * 60)
    print("Step 1: FlawDetector 로직 검증")
    print("=" * 60)

    supabase = get_supabase()
    detector = FlawDetector()

    # 1. 실제 worldview 가져오기
    print("\n[1] 실제 worldview 데이터 조회...")
    worldviews = supabase.table('worldviews').select('*').limit(1).execute()

    if not worldviews.data:
        print("❌ worldview 데이터 없음")
        return

    worldview = worldviews.data[0]
    print(f"✅ Worldview ID: {worldview['id']}")
    print(f"   Title: {worldview['title']}")
    print(f"   Frame: {worldview['frame']}")

    # 2. 관련 perceptions 가져오기
    print("\n[2] 관련 perceptions 조회...")
    perception_ids = worldview.get('perception_ids', [])
    if not perception_ids:
        print("❌ perception_ids 없음")
        return

    perceptions_data = supabase.table('perceptions')\
        .select('*')\
        .in_('id', perception_ids)\
        .execute()

    perceptions = perceptions_data.data
    print(f"✅ {len(perceptions)}개 perceptions 발견 (총 {len(perception_ids)}개 ID)")

    # 3. Rule-based 결함 탐지 테스트
    print("\n[3] Rule-based 결함 탐지 실행...")
    rule_flaws = detector._detect_rule_based(worldview, perceptions)
    print(f"✅ {len(rule_flaws)}개 rule-based 결함 탐지")
    for i, flaw in enumerate(rule_flaws[:3], 1):
        print(f"   {i}. {flaw['type']}: {flaw['description'][:60]}...")

    # 4. GPT 기반 결함 탐지 테스트
    print("\n[4] GPT 기반 결함 탐지 실행...")
    try:
        gpt_flaws = await detector._detect_with_gpt(worldview, perceptions)
        print(f"✅ {len(gpt_flaws)}개 GPT 결함 탐지")
        for i, flaw in enumerate(gpt_flaws[:3], 1):
            print(f"   {i}. {flaw['type']}: {flaw['description'][:60]}...")
    except Exception as e:
        print(f"❌ GPT 탐지 실패: {e}")
        gpt_flaws = []

    # 5. 전체 결함 탐지 (중복 제거 포함)
    print("\n[5] 전체 결함 탐지 (중복 제거)...")
    all_flaws = await detector.detect_flaws(worldview, perceptions)
    print(f"✅ 최종 {len(all_flaws)}개 결함 (중복 제거 후)")

    # 6. 결함 타입별 분포
    print("\n[6] 결함 타입 분포:")
    flaw_types = {}
    for flaw in all_flaws:
        flaw_type = flaw['type']
        flaw_types[flaw_type] = flaw_types.get(flaw_type, 0) + 1

    for flaw_type, count in sorted(flaw_types.items(), key=lambda x: -x[1]):
        print(f"   - {flaw_type}: {count}개")

    # 7. 실제 결함 내용 샘플
    print("\n[7] 탐지된 결함 샘플 (상위 2개):")
    for i, flaw in enumerate(all_flaws[:2], 1):
        print(f"\n   --- 결함 #{i} ---")
        print(f"   타입: {flaw['type']}")
        print(f"   심각도: {flaw['severity']}")
        print(f"   설명: {flaw['description']}")
        print(f"   증거: {flaw.get('evidence', 'N/A')[:100]}...")

    print("\n" + "=" * 60)
    print("✅ FlawDetector 로직 검증 완료")
    print("=" * 60)

    return all_flaws

if __name__ == '__main__':
    asyncio.run(verify_flaw_detector())
