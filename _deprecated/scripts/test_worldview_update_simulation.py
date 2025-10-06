"""
세계관 업데이트 시뮬레이션

테스트 시나리오:
1. 새로운 글 수집
2. 3-layer 분석
3. 세계관 업데이트 방식 비교:
   - 방식 A: 전체 재구성 (새로 생성)
   - 방식 B: 기존 세계관에 추가
   - 방식 C: 점진적 업데이트 (merge)
   - 방식 D: 임계값 기반 업데이트
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from openai import AsyncOpenAI
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def collect_new_posts(limit=50):
    """최신 개념글 수집 (시뮬레이션)"""
    print("\n" + "="*70)
    print("1. 새로운 글 수집")
    print("="*70)

    supabase = get_supabase()

    # 기존 데이터 확인
    existing = supabase.table('contents').select('id', count='exact').execute()
    print(f"\n기존 contents: {existing.count}개")

    # 실제로는 DC Gallery에서 크롤링하지만, 여기서는 기존 데이터로 시뮬레이션
    # 가장 최근 글들을 "새 글"로 가정
    new_posts = supabase.table('contents')\
        .select('*')\
        .order('created_at', desc=True)\
        .limit(limit)\
        .execute().data

    print(f"새로 수집할 글: {len(new_posts)}개 (시뮬레이션)")

    # 샘플 출력
    print(f"\n샘플 3개:")
    for i, post in enumerate(new_posts[:3], 1):
        print(f"  {i}. {post['title'][:60]}")

    return new_posts


async def analyze_new_posts(new_posts):
    """새 글 3-layer 분석"""
    print("\n" + "="*70)
    print("2. 새 글 3-Layer 분석")
    print("="*70)

    from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor

    extractor = LayeredPerceptionExtractor()
    supabase = get_supabase()

    # 이미 분석된 것 제외
    analyzed_ids = set(
        lp['content_id']
        for lp in supabase.table('layered_perceptions').select('content_id').execute().data
    )

    new_to_analyze = [p for p in new_posts if p['id'] not in analyzed_ids]

    print(f"\n분석 대상: {len(new_to_analyze)}개")

    if len(new_to_analyze) == 0:
        print("⚠️  모두 이미 분석됨. 시뮬레이션을 위해 기존 분석 사용")

        # 기존 분석 중 최신 것 사용
        existing_lps = supabase.table('layered_perceptions')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(20)\
            .execute().data

        return existing_lps

    # 실제 분석 (샘플만)
    analyzed = []
    for i, post in enumerate(new_to_analyze[:5], 1):
        print(f"\r  분석 중: {i}/5", end='', flush=True)

        try:
            lp_id = await extractor.extract(post)
            lp = supabase.table('layered_perceptions')\
                .select('*')\
                .eq('id', str(lp_id))\
                .execute().data[0]
            analyzed.append(lp)
        except Exception as e:
            print(f"\n  ⚠️  분석 실패: {e}")

    print(f"\n\n✅ {len(analyzed)}개 분석 완료")

    return analyzed


async def scenario_a_full_rebuild(old_worldviews, new_perceptions):
    """
    방식 A: 전체 재구성

    - 기존 + 새 데이터 전부 합쳐서 다시 세계관 구성
    - 장점: 완전히 새로운 시각
    - 단점: 기존 세계관 소실, 비용 높음
    """
    print("\n" + "="*70)
    print("시나리오 A: 전체 재구성")
    print("="*70)

    supabase = get_supabase()

    # 모든 perception 가져오기
    all_perceptions = supabase.table('layered_perceptions')\
        .select('*')\
        .execute().data

    print(f"\n전체 perception: {len(all_perceptions)}개")

    # 전체 재구성 (OptimalWorldviewConstructor 사용)
    from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

    constructor = OptimalWorldviewConstructor()

    # 샘플로만 테스트 (비용 절감)
    print("\n⚠️  비용 절감을 위해 샘플 30개로 테스트")

    sample_perceptions = all_perceptions[:30]

    hierarchy = await constructor._extract_hierarchical_worldviews(sample_perceptions)

    print(f"\n새로 추출된 세계관:")
    for cat in hierarchy:
        print(f"  📂 {cat['category']}")
        for sub in cat.get('subcategories', []):
            print(f"    └─ {sub['title']}")

    # 평가
    print("\n📊 평가:")
    print("  장점: 완전히 새로운 관점 반영")
    print("  단점:")
    print("    - 기존 세계관 ID 변경 (링크 깨짐)")
    print("    - GPT 비용 높음")
    print("    - 일관성 유지 어려움")

    return {
        'method': 'full_rebuild',
        'new_worldviews': len(hierarchy),
        'cost': 'high',
        'consistency': 'low'
    }


async def scenario_b_append_to_existing(old_worldviews, new_perceptions):
    """
    방식 B: 기존 세계관에 추가

    - 새 perception을 기존 세계관에 매칭만
    - 세계관 자체는 변경 없음
    - 장점: 빠름, 일관성 유지
    - 단점: 새로운 세계관 발견 불가
    """
    print("\n" + "="*70)
    print("시나리오 B: 기존 세계관에 추가만")
    print("="*70)

    supabase = get_supabase()

    # 기존 세계관 로드
    existing_wvs = [wv for wv in old_worldviews if '>' in wv['title']]

    print(f"\n기존 세계관: {len(existing_wvs)}개")
    for wv in existing_wvs:
        print(f"  - {wv['title']}")

    # 새 perception 매칭
    print(f"\n새 perception {len(new_perceptions)}개를 기존 세계관에 매칭...")

    matched = 0
    unmatched = 0

    for lp in new_perceptions[:10]:  # 샘플만
        lp_text = ' '.join(lp.get('deep_beliefs', []))

        # 간단한 키워드 매칭
        best_match = None
        best_score = 0

        for wv in existing_wvs:
            frame = json.loads(wv['frame'])
            keywords = frame['metadata'].get('key_concepts', [])

            score = sum(1 for kw in keywords if kw in lp_text)

            if score > best_score:
                best_score = score
                best_match = wv['title']

        if best_score > 0:
            matched += 1
            print(f"  ✅ 매칭: '{best_match}' (score: {best_score})")
        else:
            unmatched += 1
            print(f"  ❌ 미매칭: {lp_text[:50]}...")

    # 평가
    print(f"\n📊 결과:")
    print(f"  매칭: {matched}개")
    print(f"  미매칭: {unmatched}개")

    if unmatched > 0:
        print(f"\n⚠️  문제: {unmatched}개 perception이 기존 세계관에 안 맞음")
        print(f"  → 새로운 세계관이 필요할 수 있음")

    print("\n📊 평가:")
    print("  장점: 빠름, 비용 낮음, 일관성 유지")
    print("  단점: 새로운 세계관 발견 불가")

    return {
        'method': 'append_only',
        'matched': matched,
        'unmatched': unmatched,
        'cost': 'low',
        'new_worldviews': 0
    }


async def scenario_c_incremental_merge(old_worldviews, new_perceptions):
    """
    방식 C: 점진적 병합

    - 새 perception 분석
    - 기존 세계관과 유사도 계산
    - 높으면 기존 세계관 업데이트 (narrative 예시 추가)
    - 낮으면 새 세계관 생성
    - 장점: 발전 + 일관성
    - 단점: 복잡도
    """
    print("\n" + "="*70)
    print("시나리오 C: 점진적 병합 (Incremental Merge)")
    print("="*70)

    supabase = get_supabase()

    existing_wvs = [wv for wv in old_worldviews if '>' in wv['title']]

    print(f"\n기존 세계관: {len(existing_wvs)}개")

    # 새 perception들의 주요 패턴 추출
    print(f"\n새 perception {len(new_perceptions)}개 분석...")

    new_themes = {}
    for lp in new_perceptions[:15]:
        hint = lp.get('worldview_hints', '')
        beliefs = lp.get('deep_beliefs', [])

        # 주제 추출 (간단한 키워드 기반)
        if '민주당' in hint or '좌파' in hint:
            theme = '민주당/좌파'
        elif '중국' in hint:
            theme = '중국'
        elif '북한' in hint:
            theme = '북한'
        else:
            theme = '기타'

        if theme not in new_themes:
            new_themes[theme] = []
        new_themes[theme].append(lp)

    print(f"\n새 데이터의 주제 분포:")
    for theme, lps in new_themes.items():
        print(f"  - {theme}: {len(lps)}개")

    # 병합 전략
    print("\n병합 전략:")

    updated = []
    created = []

    for theme, lps in new_themes.items():
        # 기존 세계관 중 매칭되는 것 찾기
        matching_wv = None

        for wv in existing_wvs:
            if theme in wv['title']:
                matching_wv = wv
                break

        if matching_wv:
            print(f"\n  ✅ '{theme}' → 기존 세계관 업데이트: {matching_wv['title']}")
            print(f"     새 예시 {len(lps)}개 추가 가능")
            updated.append(matching_wv['title'])
        else:
            print(f"\n  ⭐ '{theme}' → 새 세계관 생성 필요")
            print(f"     데이터: {len(lps)}개")
            created.append(theme)

    # 실제 업데이트 시뮬레이션 (1개만)
    if updated:
        print(f"\n\n업데이트 시뮬레이션: {updated[0]}")

        wv_to_update = [wv for wv in existing_wvs if wv['title'] == updated[0]][0]
        frame = json.loads(wv_to_update['frame'])

        print(f"\n현재 예시 개수: {len(frame['narrative'].get('examples', []))}개")

        # 새 예시 생성 (GPT)
        sample_lp = new_themes[list(new_themes.keys())[0]][0]

        prompt = f"""
다음 새 데이터를 기존 세계관 예시 형식으로 변환하세요.

새 데이터:
- 심층 믿음: {sample_lp.get('deep_beliefs', [])[:2]}
- 암묵적 전제: {sample_lp.get('implicit_assumptions', [])[:2]}

기존 예시 형식:
{{
  "case": "구체적 사례",
  "dc_interpretation": "DC Gallery 해석",
  "normal_interpretation": "일반적 해석",
  "gap": "핵심 차이"
}}

JSON으로 응답:
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        new_example = json.loads(response.choices[0].message.content)

        print(f"\n생성된 새 예시:")
        print(json.dumps(new_example, ensure_ascii=False, indent=2))

        print(f"\n→ 이 예시를 narrative.examples에 추가")

    # 평가
    print("\n\n📊 평가:")
    print(f"  업데이트될 세계관: {len(updated)}개")
    print(f"  새로 생성될 세계관: {len(created)}개")
    print("\n  장점:")
    print("    - 기존 세계관 발전 (예시 증가)")
    print("    - 새로운 세계관 발견")
    print("    - 일관성 유지 (ID 변경 없음)")
    print("  단점:")
    print("    - 구현 복잡도 높음")
    print("    - GPT 비용 중간")

    return {
        'method': 'incremental_merge',
        'updated': len(updated),
        'created': len(created),
        'cost': 'medium',
        'consistency': 'high'
    }


async def scenario_d_threshold_based(old_worldviews, new_perceptions):
    """
    방식 D: 임계값 기반 업데이트

    - 새 perception 누적
    - N개 이상 쌓이면 재구성
    - 또는 기존 세계관과 불일치율 > X% 이면 재구성
    - 장점: 자동화, 안정성
    - 단점: 지연
    """
    print("\n" + "="*70)
    print("시나리오 D: 임계값 기반 업데이트")
    print("="*70)

    supabase = get_supabase()

    # 현재 상태
    total_perceptions = supabase.table('layered_perceptions').select('id', count='exact').execute().count

    existing_wvs = [wv for wv in old_worldviews if '>' in wv['title']]

    print(f"\n현재 상태:")
    print(f"  전체 perception: {total_perceptions}개")
    print(f"  세계관: {len(existing_wvs)}개")

    # 새 데이터
    new_count = len(new_perceptions)
    print(f"  새 perception: {new_count}개")

    # 임계값 설정
    REBUILD_THRESHOLD = 100  # 100개 새 데이터마다 재구성
    MISMATCH_THRESHOLD = 0.3  # 30% 미매칭 시 재구성

    print(f"\n임계값:")
    print(f"  재구성 임계값: {REBUILD_THRESHOLD}개")
    print(f"  불일치 임계값: {MISMATCH_THRESHOLD*100}%")

    # 조건 1: 개수 임계값
    needs_rebuild_count = new_count >= REBUILD_THRESHOLD

    print(f"\n조건 1: 누적 개수")
    print(f"  {new_count} / {REBUILD_THRESHOLD} = {new_count/REBUILD_THRESHOLD*100:.1f}%")
    print(f"  → {'재구성 필요' if needs_rebuild_count else '아직 충분하지 않음'}")

    # 조건 2: 불일치율
    matched = 0
    for lp in new_perceptions[:20]:  # 샘플
        lp_text = ' '.join(lp.get('deep_beliefs', []))

        for wv in existing_wvs:
            frame = json.loads(wv['frame'])
            keywords = frame['metadata'].get('key_concepts', [])

            if any(kw in lp_text for kw in keywords):
                matched += 1
                break

    mismatch_rate = 1 - (matched / min(len(new_perceptions), 20))
    needs_rebuild_mismatch = mismatch_rate > MISMATCH_THRESHOLD

    print(f"\n조건 2: 불일치율")
    print(f"  미매칭: {mismatch_rate*100:.1f}%")
    print(f"  → {'재구성 필요' if needs_rebuild_mismatch else '기존 세계관 충분'}")

    # 최종 결정
    should_rebuild = needs_rebuild_count or needs_rebuild_mismatch

    print(f"\n\n🎯 최종 결정:")
    if should_rebuild:
        print("  → 재구성 실행")
        print("  → OptimalWorldviewConstructor 호출")
    else:
        print("  → 기존 세계관 유지")
        print("  → 새 perception만 매칭")

    # 평가
    print("\n📊 평가:")
    print("  장점:")
    print("    - 자동화 가능")
    print("    - 안정적 (불필요한 재구성 방지)")
    print("  단점:")
    print("    - 업데이트 지연 가능")
    print("    - 임계값 튜닝 필요")

    return {
        'method': 'threshold_based',
        'should_rebuild': should_rebuild,
        'new_count': new_count,
        'mismatch_rate': mismatch_rate,
        'cost': 'low' if not should_rebuild else 'high'
    }


async def compare_all_scenarios(results):
    """모든 시나리오 비교"""
    print("\n" + "="*70)
    print("전체 시나리오 비교")
    print("="*70)

    print("\n| 방식 | 비용 | 일관성 | 발전성 | 자동화 | 추천도 |")
    print("|------|------|--------|--------|--------|--------|")

    scenarios = {
        'A. 전체 재구성': {
            'cost': '높음',
            'consistency': '낮음',
            'evolution': '높음',
            'automation': '중간',
            'score': '⚠️'
        },
        'B. 추가만': {
            'cost': '낮음',
            'consistency': '높음',
            'evolution': '낮음',
            'automation': '높음',
            'score': '⚠️'
        },
        'C. 점진적 병합': {
            'cost': '중간',
            'consistency': '높음',
            'evolution': '높음',
            'automation': '중간',
            'score': '✅✅'
        },
        'D. 임계값 기반': {
            'cost': '낮음',
            'consistency': '높음',
            'evolution': '중간',
            'automation': '높음',
            'score': '✅'
        }
    }

    for name, scores in scenarios.items():
        print(f"| {name} | {scores['cost']} | {scores['consistency']} | {scores['evolution']} | {scores['automation']} | {scores['score']} |")

    print("\n\n🏆 최적 전략:")
    print("="*70)
    print("""
방식 C (점진적 병합) + 방식 D (임계값)의 하이브리드

【운영 방식】

1. 일상 운영 (매일):
   - 새 글 수집
   - 3-layer 분석
   - 기존 세계관에 매칭 (방식 B)

2. 점진적 업데이트 (주 1회):
   - 새로 매칭된 perception 중 대표 사례 선정
   - 기존 세계관 narrative에 예시 추가 (방식 C)
   - GPT로 새 예시 생성 후 추가

3. 임계값 재구성 (월 1회 또는 조건 충족 시):
   - 조건 1: 새 perception 100개+ 누적
   - 조건 2: 미매칭률 30%+
   - 조건 충족 시: 전체 재구성 (방식 A)

4. 새 세계관 발견 (수시):
   - 미매칭 perception이 특정 주제로 10개+ 누적
   - GPT로 새 세계관 생성
   - 기존 계층에 추가

【장점】
- 일상: 빠르고 저비용 (매칭만)
- 주간: 기존 세계관 발전 (예시 증가)
- 월간: 전체 구조 재정비
- 수시: 새로운 담론 포착

【구현 복잡도】
- 중간 (하지만 가치 있음)
""")


async def main():
    print("="*70)
    print("세계관 업데이트 시뮬레이션")
    print("="*70)

    # 1. 새 글 수집
    new_posts = await collect_new_posts(limit=50)

    # 2. 3-layer 분석
    new_perceptions = await analyze_new_posts(new_posts)

    # 3. 기존 세계관 로드
    supabase = get_supabase()
    old_worldviews = supabase.table('worldviews').select('*').execute().data

    # 4. 시나리오 테스트
    results = {}

    results['A'] = await scenario_a_full_rebuild(old_worldviews, new_perceptions)
    results['B'] = await scenario_b_append_to_existing(old_worldviews, new_perceptions)
    results['C'] = await scenario_c_incremental_merge(old_worldviews, new_perceptions)
    results['D'] = await scenario_d_threshold_based(old_worldviews, new_perceptions)

    # 5. 비교
    await compare_all_scenarios(results)

if __name__ == '__main__':
    asyncio.run(main())
