"""
데이터 마이그레이션 스크립트

Old System → New System 전환:
1. Schema migration (SQL 실행)
2. Populate reasoning structures (기존 501개 분석 결과 사용)
3. Archive old worldviews
4. Insert new 9 worldviews
5. Re-match with mechanism matcher
"""

import asyncio
import json
from engines.utils.supabase_client import get_supabase
from engines.analyzers.mechanism_matcher import MechanismMatcher


async def main():
    print("="*80)
    print("세계관 시스템 마이그레이션")
    print("="*80)

    supabase = get_supabase()

    # ========================================
    # Step 1: Schema Migration
    # ========================================
    print("\n[Step 1] Schema Migration")
    print("-"*80)

    print("⚠️  다음 SQL 파일을 Supabase에서 수동으로 실행하세요:")
    print("   supabase/migrations/301_add_reasoning_structure_fields.sql")
    print()

    confirm = input("실행 완료했습니까? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ 마이그레이션 취소")
        return

    # ========================================
    # Step 2: Populate Reasoning Structures
    # ========================================
    print("\n[Step 2] Populate Reasoning Structures")
    print("-"*80)

    # Load analysis results
    print("분석 결과 로드 중...")
    with open('_reasoning_structures_analysis.json', 'r', encoding='utf-8') as f:
        analysis_results = json.load(f)

    print(f"✅ {len(analysis_results)}개 분석 결과 로드 완료")

    # Update each perception
    print("\n기존 perception 업데이트 중...")
    updated_count = 0

    for i, item in enumerate(analysis_results):
        perception_id = item['perception_id']
        rs = item['reasoning_structure']

        try:
            supabase.table('layered_perceptions')\
                .update({
                    'mechanisms': rs.get('mechanisms', []),
                    'skipped_steps': rs.get('skipped_steps', []),
                    'actor': rs.get('actor', {}),
                    'logic_chain': rs.get('logic_chain', []),
                    'consistency_pattern': rs.get('consistency_pattern', '')
                })\
                .eq('id', perception_id)\
                .execute()

            updated_count += 1

            if (i + 1) % 50 == 0:
                print(f"  진행: {i+1}/{len(analysis_results)}")

        except Exception as e:
            print(f"  ⚠️  {perception_id}: {e}")

    print(f"\n✅ {updated_count}개 perception 업데이트 완료")

    # ========================================
    # Step 3: Archive Old Worldviews
    # ========================================
    print("\n[Step 3] Archive Old Worldviews")
    print("-"*80)

    # Get existing worldviews
    existing_wvs = supabase.table('worldviews').select('id, title').execute().data

    print(f"기존 세계관: {len(existing_wvs)}개")
    for wv in existing_wvs:
        print(f"  - {wv['title']}")

    print()
    confirm = input("이 세계관들을 아카이브할까요? (yes/no): ")
    if confirm.lower() == 'yes':
        for wv in existing_wvs:
            supabase.table('worldviews')\
                .update({'archived': True})\
                .eq('id', wv['id'])\
                .execute()
        print(f"✅ {len(existing_wvs)}개 세계관 아카이브 완료")
    else:
        print("⚠️  아카이브 건너뜀")

    # ========================================
    # Step 4: Insert New Worldviews
    # ========================================
    print("\n[Step 4] Insert New Worldviews")
    print("-"*80)

    # Load new worldviews
    print("새 세계관 로드 중...")
    with open('_consolidated_worldviews_gpt5.json', 'r', encoding='utf-8') as f:
        new_worldviews = json.load(f)

    print(f"✅ {len(new_worldviews)}개 새 세계관 로드 완료")

    # Insert each worldview
    print("\n새 세계관 생성 중...")
    from datetime import datetime

    inserted_count = 0
    for wv_data in new_worldviews:
        worldview = {
            'title': wv_data['title'],
            'frame': json.dumps({
                'actor': wv_data['actor'],
                'core_mechanisms': wv_data['core_mechanisms'],
                'logic_pattern': wv_data['logic_pattern'],
                'examples': wv_data.get('examples', []),
                'estimated_coverage_pct': wv_data.get('estimated_coverage_pct', 0)
            }, ensure_ascii=False),
            'description': wv_data['logic_pattern']['trigger'] + ' → ' + wv_data['logic_pattern']['conclusion'],
            'core_subject': wv_data['actor'],
            'core_attributes': wv_data['core_mechanisms'],
            'overall_valence': 'negative',
            'version': 1,
            'last_updated': datetime.now().isoformat(),
            'total_perceptions': 0,
            'perception_ids': [],
            'archived': False
        }

        try:
            supabase.table('worldviews').insert(worldview).execute()
            inserted_count += 1
            print(f"  ✓ {wv_data['title']}")
        except Exception as e:
            print(f"  ❌ {wv_data['title']}: {e}")

    print(f"\n✅ {inserted_count}개 새 세계관 생성 완료")

    # ========================================
    # Step 5: Re-match with Mechanism Matcher
    # ========================================
    print("\n[Step 5] Re-match with Mechanism Matcher")
    print("-"*80)

    matcher = MechanismMatcher()
    links_created = await matcher.match_all_perceptions(threshold=0.4)

    print(f"\n✅ {links_created}개 링크 생성 완료")

    # ========================================
    # Final Summary
    # ========================================
    print("\n" + "="*80)
    print("마이그레이션 완료!")
    print("="*80)

    print(f"\n요약:")
    print(f"  - Reasoning structures 업데이트: {updated_count}개")
    print(f"  - 기존 세계관 아카이브: {len(existing_wvs)}개")
    print(f"  - 새 세계관 생성: {inserted_count}개")
    print(f"  - Perception-Worldview 링크: {links_created}개")

    # Check coverage
    print(f"\n커버리지 확인:")
    new_wvs = supabase.table('worldviews')\
        .select('title, total_perceptions')\
        .eq('archived', False)\
        .execute().data

    total_perceptions = len(analysis_results)
    total_links = sum(wv['total_perceptions'] for wv in new_wvs)

    for wv in new_wvs:
        count = wv['total_perceptions']
        pct = count / total_perceptions * 100 if total_perceptions > 0 else 0
        print(f"  {wv['title'][:60]}: {count}개 ({pct:.1f}%)")

    avg_links = total_links / total_perceptions if total_perceptions > 0 else 0
    print(f"\n  평균: {avg_links:.2f} links/perception")

    print("\n✅ 시스템 전환 완료!")
    print("   Dashboard에서 새 세계관을 확인하세요.")


if __name__ == "__main__":
    asyncio.run(main())
