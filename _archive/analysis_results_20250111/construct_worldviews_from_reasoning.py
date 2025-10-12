"""
추론 구조 분석 결과로부터 세계관 자동 생성

실제 GPT 분석 결과 기반
"""

import json
from collections import Counter, defaultdict
from engines.utils.supabase_client import get_supabase

supabase = get_supabase()


def load_reasoning_results():
    """GPT 분석 결과 로드"""
    with open('_reasoning_structures_analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def cluster_by_pattern(results):
    """
    일관성 패턴으로 클러스터링
    """
    clusters = defaultdict(list)

    for r in results:
        pattern = r['reasoning_structure'].get('consistency_pattern', 'unknown')
        clusters[pattern].append(r)

    return clusters


def analyze_cluster(cluster_items):
    """
    클러스터 분석하여 세계관 정의
    """

    # 메커니즘 집계
    all_mechanisms = []
    all_actors = []
    all_purposes = []
    all_methods = []

    for item in cluster_items:
        structure = item['reasoning_structure']

        all_mechanisms.extend(structure.get('mechanisms', []))

        actor = structure.get('actor', {})
        if actor.get('subject'):
            all_actors.append(actor['subject'])
        if actor.get('purpose'):
            all_purposes.append(actor['purpose'])
        if actor.get('methods'):
            all_methods.extend(actor['methods'])

    # 빈도 계산
    mechanism_freq = Counter(all_mechanisms)
    actor_freq = Counter(all_actors)
    purpose_freq = Counter(all_purposes)
    method_freq = Counter(all_methods)

    return {
        'size': len(cluster_items),
        'mechanisms': mechanism_freq.most_common(3),
        'primary_actor': actor_freq.most_common(1)[0] if actor_freq else ('unknown', 0),
        'primary_purpose': purpose_freq.most_common(1)[0] if purpose_freq else ('unknown', 0),
        'common_methods': method_freq.most_common(3),
        'sample_items': cluster_items[:3]
    }


def generate_worldview_name(pattern, analysis):
    """
    패턴과 분석 결과로 세계관 이름 생성
    """

    actor = analysis['primary_actor'][0]
    mechanisms = [m[0] for m in analysis['mechanisms']]

    # 패턴 기반 이름 생성
    if '정보_파악_불법' in pattern:
        return f"{actor}의 정보 파악 즉시 불법 해석"
    elif '집회_제한' in pattern or '폭력' in pattern:
        return f"집회 제한 즉시 정치 탄압 해석"
    elif '네트워크' in pattern or '연결' in pattern:
        return f"연결 관찰 즉시 조직적 공모 해석"
    elif '외부_위협' in pattern or '중국' in actor:
        return f"{actor} 관련 즉시 위협 연결"
    elif '정치보복' in pattern:
        return f"권력 행위 즉시 정치보복 해석"
    elif '경고' in pattern or '위기' in pattern:
        return f"해외 경고 즉시 내부 위기 연결"
    else:
        return f"{actor} 행위 패턴 해석"


def main():
    """메인 실행"""

    print("="*80)
    print("추론 구조 기반 세계관 자동 생성")
    print("="*80)

    # 1. 결과 로드
    results = load_reasoning_results()
    print(f"\n✅ {len(results)}개 분석 결과 로드")

    # 2. 패턴으로 클러스터링
    clusters = cluster_by_pattern(results)
    print(f"\n✅ {len(clusters)}개 일관성 패턴 발견")

    # 3. 각 클러스터 분석
    worldviews = []

    print("\n" + "="*80)
    print("세계관 생성 결과")
    print("="*80)

    # 크기 순 정렬
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)

    for pattern, items in sorted_clusters:
        if len(items) < 2:  # 2개 미만은 제외
            continue

        analysis = analyze_cluster(items)
        name = generate_worldview_name(pattern, analysis)

        worldview = {
            'name': name,
            'consistency_pattern': pattern,
            'supporting_perceptions': len(items),
            'primary_mechanisms': [m[0] for m in analysis['mechanisms']],
            'primary_actor': analysis['primary_actor'][0],
            'primary_purpose': analysis['primary_purpose'][0],
            'common_methods': [m[0] for m in analysis['common_methods']],
            'perception_ids': [item['perception_id'] for item in items]
        }

        worldviews.append(worldview)

        # 출력
        print(f"\n세계관 {len(worldviews)}: {name}")
        print(f"  지지 perception: {len(items)}개")
        print(f"  주요 메커니즘: {', '.join(worldview['primary_mechanisms'])}")
        print(f"  주요 행위자: {worldview['primary_actor']}")
        print(f"  추정 목적: {worldview['primary_purpose']}")

        # 샘플 사례
        print(f"  대표 사례:")
        for i, sample in enumerate(analysis['sample_items'][:2], 1):
            content = supabase.table('contents').select('title').eq('id', sample['content_id']).execute().data
            if content:
                print(f"    {i}. {content[0]['title'][:70]}")

        # Logic chain 샘플
        if analysis['sample_items']:
            sample_chain = analysis['sample_items'][0]['reasoning_structure'].get('logic_chain', [])
            if sample_chain:
                print(f"  논리 체인 예시:")
                for i, step in enumerate(sample_chain[:3], 1):
                    print(f"    {i}. {step}")

    # 4. 결과 저장
    output_file = '_worldviews_from_reasoning.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(worldviews, f, ensure_ascii=False, indent=2)

    print(f"\n\n✅ 총 {len(worldviews)}개 세계관 생성")
    print(f"✅ 결과 저장: {output_file}")

    # 5. 통계
    print("\n" + "="*80)
    print("통계")
    print("="*80)

    total_perceptions = sum(wv['supporting_perceptions'] for wv in worldviews)
    print(f"\n총 perception: {len(results)}개")
    print(f"세계관에 포함: {total_perceptions}개")
    print(f"커버리지: {total_perceptions/len(results)*100:.1f}%")

    print("\n세계관별 분포:")
    for wv in worldviews[:10]:
        print(f"  {wv['name'][:60]}: {wv['supporting_perceptions']}개 ({wv['supporting_perceptions']/len(results)*100:.1f}%)")

    print("\n메커니즘 전체 분포:")
    all_mechanisms = Counter()
    for wv in worldviews:
        for mech in wv['primary_mechanisms']:
            all_mechanisms[mech] += wv['supporting_perceptions']

    for mech, count in all_mechanisms.most_common():
        print(f"  {mech}: {count}회")


if __name__ == "__main__":
    main()
