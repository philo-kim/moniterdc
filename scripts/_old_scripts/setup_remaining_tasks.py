"""
남은 작업 자동 실행 스크립트

1. perception_worldview_links 테이블 생성 (수동 필요)
2. 전체 perception 매칭
3. 반박 논리 생성
"""

import asyncio
import sys
import os
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')

print("="*70)
print("남은 작업 실행")
print("="*70)

print("""
⚠️  먼저 Supabase에서 테이블을 생성해야 합니다.

Supabase Dashboard → SQL Editor에서 다음 실행:

---

CREATE TABLE IF NOT EXISTS perception_worldview_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perception_id UUID REFERENCES layered_perceptions(id) ON DELETE CASCADE,
    worldview_id UUID REFERENCES worldviews(id) ON DELETE CASCADE,
    relevance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pwlinks_perception
    ON perception_worldview_links(perception_id);

CREATE INDEX IF NOT EXISTS idx_pwlinks_worldview
    ON perception_worldview_links(worldview_id);

CREATE INDEX IF NOT EXISTS idx_pwlinks_relevance
    ON perception_worldview_links(relevance_score DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_pwlinks_unique
    ON perception_worldview_links(perception_id, worldview_id);

---

테이블 생성 후 아무 키나 누르세요...
""")

input()

print("\n테이블이 생성되었다고 가정하고 계속 진행합니다.")
print("\n" + "="*70)
print("Task 1: 전체 Perception 매칭")
print("="*70)

async def task1_match_all():
    """전체 perception을 세계관에 매칭"""
    from engines.utils.supabase_client import get_supabase
    from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

    supabase = get_supabase()
    constructor = OptimalWorldviewConstructor()

    # 모든 perception 로드
    perceptions = supabase.table('layered_perceptions').select('*').execute().data

    # 모든 worldview 로드
    worldviews = supabase.table('worldviews').select('*').execute().data
    new_wvs = [w for w in worldviews if '>' in w['title']]

    print(f"\nPerception: {len(perceptions)}개")
    print(f"Worldview: {len(new_wvs)}개")

    # 매칭
    links = await constructor._match_perceptions_to_worldviews(perceptions, new_wvs)

    print(f"\n✅ {links}개 링크 생성")

    return links

try:
    links_created = asyncio.run(task1_match_all())
except Exception as e:
    print(f"\n❌ 실패: {e}")
    print("\n테이블이 생성되지 않았을 수 있습니다.")
    print("Supabase에서 먼저 테이블을 생성하세요.")
    sys.exit(1)

print("\n" + "="*70)
print("Task 2: 반박 논리 생성")
print("="*70)

async def task2_generate_deconstruction():
    """모든 세계관에 대한 반박 논리 생성"""
    from engines.analyzers.deconstruction_generator import DeconstructionGenerator

    generator = DeconstructionGenerator()
    stats = await generator.generate_for_all_worldviews()

    return stats

stats = asyncio.run(task2_generate_deconstruction())

print("\n" + "="*70)
print("모든 작업 완료")
print("="*70)

print(f"""
✅ Perception 매칭: {links_created}개 링크
✅ 반박 논리: {stats['generated']}/{stats['total']}개 생성

다음 단계:
1. 대시보드 API 구현
2. 세계관 브라우징 UI 구현
""")
