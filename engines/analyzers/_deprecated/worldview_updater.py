"""
WorldviewUpdater - 세계관 지속적 업데이트 엔진

시뮬레이션 결과 기반 최적 전략:
- 하이브리드: 점진적 병합 (C) + 임계값 기반 (D)

운영 방식:
1. 일상 (매일): 새 글 수집 → 분석 → 매칭
2. 주간 (주 1회): 기존 세계관에 예시 추가
3. 월간 (조건 충족 시): 전체 재구성
4. 수시: 새 세계관 발견 및 생성
"""

from openai import AsyncOpenAI
import os
import json
import numpy as np
from typing import Dict, List, Tuple
from uuid import UUID
from datetime import datetime
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class WorldviewUpdater:
    """Continuously update worldviews with new data"""

    # 임계값 설정
    REBUILD_THRESHOLD_COUNT = 100  # 100개 새 perception 누적 시 재구성
    REBUILD_THRESHOLD_MISMATCH = 0.3  # 30% 미매칭 시 재구성
    NEW_WORLDVIEW_THRESHOLD = 10  # 같은 주제 10개 누적 시 새 세계관 생성

    def __init__(self):
        self.supabase = get_supabase()

    async def daily_update(self) -> Dict:
        """
        일상 업데이트 (매일)

        1. 새 글 수집
        2. 3-layer 분석
        3. 기존 세계관에 매칭

        Returns:
            업데이트 통계
        """
        print("\n" + "="*70)
        print("일상 업데이트 (Daily)")
        print("="*70)

        # 1. 분석되지 않은 contents 찾기
        all_contents = self.supabase.table('contents').select('id').execute().data
        analyzed_contents = self.supabase.table('layered_perceptions').select('content_id').execute().data

        analyzed_ids = set(lp['content_id'] for lp in analyzed_contents)
        unanalyzed = [c for c in all_contents if c['id'] not in analyzed_ids]

        print(f"\n미분석 contents: {len(unanalyzed)}개")

        if len(unanalyzed) == 0:
            print("✅ 모든 글이 분석되어 있습니다")
            return {'new_analyzed': 0, 'new_matched': 0}

        # 2. 3-layer 분석
        from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor

        extractor = LayeredPerceptionExtractor()

        new_lps = []
        for i, content in enumerate(unanalyzed[:10], 1):  # 일단 10개만
            print(f"\r  분석 중: {i}/{min(len(unanalyzed), 10)}", end='', flush=True)

            content_data = self.supabase.table('contents')\
                .select('*')\
                .eq('id', content['id'])\
                .execute().data[0]

            try:
                lp_id = await extractor.extract(content_data)
                lp = self.supabase.table('layered_perceptions')\
                    .select('*')\
                    .eq('id', str(lp_id))\
                    .execute().data[0]
                new_lps.append(lp)
            except Exception as e:
                print(f"\n  ⚠️  분석 실패: {e}")

        print(f"\n\n✅ {len(new_lps)}개 새 분석 완료")

        # 3. 기존 세계관에 매칭
        matched_count = await self._match_to_existing_worldviews(new_lps)

        print(f"✅ {matched_count}개 매칭 완료")

        return {
            'new_analyzed': len(new_lps),
            'new_matched': matched_count
        }

    async def weekly_update(self) -> Dict:
        """
        주간 업데이트 (주 1회)

        1. 최근 매칭된 perception 중 대표 사례 선정
        2. 기존 세계관 narrative에 예시 추가

        Returns:
            업데이트된 세계관 개수
        """
        print("\n" + "="*70)
        print("주간 업데이트 (Weekly)")
        print("="*70)

        # 기존 세계관 로드
        worldviews = self.supabase.table('worldviews')\
            .select('*')\
            .execute().data

        new_wvs = [wv for wv in worldviews if '>' in wv['title']]

        print(f"\n기존 세계관: {len(new_wvs)}개")

        updated_count = 0

        for wv in new_wvs:
            # 이 세계관에 최근 연결된 perception 찾기
            try:
                recent_links = self.supabase.table('perception_worldview_links')\
                    .select('perception_id')\
                    .eq('worldview_id', wv['id'])\
                    .order('created_at', desc=True)\
                    .limit(5)\
                    .execute().data

                if not recent_links:
                    continue

                # 대표 perception 선정 (relevance_score 높은 것)
                perception_id = recent_links[0]['perception_id']

                perception = self.supabase.table('layered_perceptions')\
                    .select('*')\
                    .eq('id', perception_id)\
                    .execute().data[0]

                # 새 예시 생성
                new_example = await self._generate_example_from_perception(perception)

                # 세계관 업데이트
                frame = json.loads(wv['frame'])

                if 'examples' not in frame['narrative']:
                    frame['narrative']['examples'] = []

                frame['narrative']['examples'].append(new_example)

                # DB 업데이트
                self.supabase.table('worldviews')\
                    .update({'frame': json.dumps(frame, ensure_ascii=False)})\
                    .eq('id', wv['id'])\
                    .execute()

                print(f"  ✅ '{wv['title']}' 예시 추가")
                updated_count += 1

            except Exception as e:
                print(f"  ⚠️  '{wv['title']}' 업데이트 실패: {e}")

        print(f"\n✅ {updated_count}개 세계관 업데이트 완료")

        return {'updated_worldviews': updated_count}

    async def check_and_rebuild_if_needed(self) -> Dict:
        """
        임계값 확인 및 재구성 (월간 또는 조건 충족 시)

        조건:
        1. 새 perception 100개+ 누적
        2. 미매칭률 30%+

        Returns:
            재구성 여부 및 통계
        """
        print("\n" + "="*70)
        print("임계값 확인 (Monthly Check)")
        print("="*70)

        # 현재 상태
        total_perceptions = self.supabase.table('layered_perceptions')\
            .select('id', count='exact')\
            .execute().count

        total_links = self.supabase.table('perception_worldview_links')\
            .select('id', count='exact')\
            .execute().count

        # 최근 업데이트 시점 확인 (worldviews의 updated_at)
        worldviews = self.supabase.table('worldviews')\
            .select('updated_at')\
            .order('updated_at', desc=True)\
            .limit(1)\
            .execute().data

        last_rebuild = worldviews[0]['updated_at'] if worldviews else None

        # 최근 업데이트 이후 새 perception 개수
        if last_rebuild:
            new_perceptions = self.supabase.table('layered_perceptions')\
                .select('id', count='exact')\
                .gt('created_at', last_rebuild)\
                .execute().count
        else:
            new_perceptions = total_perceptions

        print(f"\n현재 상태:")
        print(f"  전체 perception: {total_perceptions}개")
        print(f"  전체 링크: {total_links}개")
        print(f"  최근 재구성 이후 새 perception: {new_perceptions}개")

        # 조건 1: 개수 임계값
        needs_rebuild_count = new_perceptions >= self.REBUILD_THRESHOLD_COUNT

        print(f"\n조건 1: 누적 개수")
        print(f"  {new_perceptions} / {self.REBUILD_THRESHOLD_COUNT}")
        print(f"  → {'✅ 재구성 필요' if needs_rebuild_count else '❌ 충분하지 않음'}")

        # 조건 2: 미매칭률
        matched_perceptions = len(set(
            link['perception_id']
            for link in self.supabase.table('perception_worldview_links')
                .select('perception_id')
                .execute().data
        ))

        mismatch_rate = 1 - (matched_perceptions / max(total_perceptions, 1))
        needs_rebuild_mismatch = mismatch_rate > self.REBUILD_THRESHOLD_MISMATCH

        print(f"\n조건 2: 미매칭률")
        print(f"  {mismatch_rate*100:.1f}% (임계값: {self.REBUILD_THRESHOLD_MISMATCH*100}%)")
        print(f"  → {'✅ 재구성 필요' if needs_rebuild_mismatch else '❌ 충분히 매칭됨'}")

        # 최종 결정
        should_rebuild = needs_rebuild_count or needs_rebuild_mismatch

        print(f"\n🎯 최종 결정: {'재구성 실행' if should_rebuild else '유지'}")

        if should_rebuild:
            print("\n세계관 재구성 시작...")

            from engines.analyzers.optimal_worldview_constructor import OptimalWorldviewConstructor

            constructor = OptimalWorldviewConstructor()
            stats = await constructor.construct_all()

            print(f"✅ 재구성 완료: {stats['total_worldviews']}개 세계관")

            return {
                'rebuilt': True,
                'new_worldviews': stats['total_worldviews']
            }
        else:
            return {
                'rebuilt': False,
                'new_perceptions': new_perceptions,
                'mismatch_rate': mismatch_rate
            }

    async def detect_and_create_new_worldviews(self) -> Dict:
        """
        새 세계관 발견 (수시)

        미매칭 perception 중 같은 주제가 10개+ 누적되면
        새 세계관 생성

        Returns:
            새로 생성된 세계관 개수
        """
        print("\n" + "="*70)
        print("새 세계관 발견 (Ad-hoc)")
        print("="*70)

        # 미매칭 perception 찾기
        all_perceptions = self.supabase.table('layered_perceptions')\
            .select('*')\
            .execute().data

        matched_ids = set(
            link['perception_id']
            for link in self.supabase.table('perception_worldview_links')
                .select('perception_id')
                .execute().data
        )

        unmatched = [lp for lp in all_perceptions if lp['id'] not in matched_ids]

        print(f"\n미매칭 perception: {len(unmatched)}개")

        if len(unmatched) < self.NEW_WORLDVIEW_THRESHOLD:
            print(f"❌ 임계값 미달 ({len(unmatched)} < {self.NEW_WORLDVIEW_THRESHOLD})")
            return {'new_worldviews': 0}

        # 주제별 그룹화
        themes = {}
        for lp in unmatched:
            hint = lp.get('worldview_hints', '')
            beliefs = lp.get('deep_beliefs', [])

            # 간단한 키워드 기반 주제 추출
            theme = self._extract_theme(hint, beliefs)

            if theme not in themes:
                themes[theme] = []
            themes[theme].append(lp)

        print(f"\n주제별 그룹:")
        for theme, lps in themes.items():
            print(f"  - {theme}: {len(lps)}개")

        # 임계값 이상인 주제로 새 세계관 생성
        created_count = 0

        for theme, lps in themes.items():
            if len(lps) >= self.NEW_WORLDVIEW_THRESHOLD:
                print(f"\n⭐ '{theme}' 새 세계관 생성 ({len(lps)}개 데이터)")

                # GPT로 새 세계관 생성
                new_wv = await self._create_new_worldview(theme, lps)

                print(f"  ✅ 생성 완료: {new_wv['title']}")
                created_count += 1

        print(f"\n✅ {created_count}개 새 세계관 생성")

        return {'new_worldviews': created_count}

    async def _match_to_existing_worldviews(self, perceptions: List[Dict]) -> int:
        """새 perception을 기존 세계관에 매칭"""

        worldviews = self.supabase.table('worldviews')\
            .select('*')\
            .execute().data

        new_wvs = [wv for wv in worldviews if '>' in wv['title']]

        matched_count = 0

        for lp in perceptions:
            lp_text = ' '.join(lp.get('deep_beliefs', []))

            best_match = None
            best_score = 0

            for wv in new_wvs:
                frame = json.loads(wv['frame'])
                keywords = frame['metadata'].get('key_concepts', [])

                score = sum(1 for kw in keywords if kw in lp_text)

                if score > best_score:
                    best_score = score
                    best_match = wv['id']

            if best_score > 0:
                # Link 생성
                try:
                    self.supabase.table('perception_worldview_links').insert({
                        'perception_id': lp['id'],
                        'worldview_id': best_match,
                        'relevance_score': best_score / 5.0  # Normalize
                    }).execute()
                    matched_count += 1
                except:
                    pass  # 이미 존재할 수 있음

        return matched_count

    async def _generate_example_from_perception(self, perception: Dict) -> Dict:
        """Perception에서 예시 생성"""

        prompt = f"""
다음 분석 결과를 세계관 예시 형식으로 변환하세요.

심층 믿음: {perception.get('deep_beliefs', [])[:2]}
암묵적 전제: {perception.get('implicit_assumptions', [])[:2]}

형식:
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

        return json.loads(response.choices[0].message.content)

    def _extract_theme(self, hint: str, beliefs: List[str]) -> str:
        """간단한 주제 추출"""

        text = hint + ' ' + ' '.join(beliefs)

        if '민주당' in text or '좌파' in text:
            return '민주당/좌파'
        elif '중국' in text:
            return '중국'
        elif '북한' in text:
            return '북한'
        elif '통일교' in text or '종교' in text:
            return '종교/통일교'
        else:
            return '기타'

    async def _create_new_worldview(self, theme: str, perceptions: List[Dict]) -> Dict:
        """새 세계관 생성"""

        # 샘플 데이터 준비
        sample_data = []
        for lp in perceptions[:10]:
            sample_data.append({
                'deep_beliefs': lp.get('deep_beliefs', [])[:2],
                'implicit_assumptions': lp.get('implicit_assumptions', [])[:2]
            })

        prompt = f"""
주제 '{theme}'에 대한 새로운 세계관을 생성하세요.

데이터 {len(sample_data)}개:
{json.dumps(sample_data, ensure_ascii=False, indent=1)}

세계관 구조:
{{
  "title": "세계관 제목",
  "category": "대분류 (기존: 민주당/좌파에 대한 인식, 외부 세력의 위협, 국내 정치적 불안정)",
  "narrative": {{
    "summary": "한 줄 요약",
    "examples": [...],
    "logic_chain": "논리",
    "historical_context": "역사"
  }},
  "metadata": {{
    "core": {{"primary_subject": "...", "primary_attribute": "..."}},
    "interpretation_frame": {{...}},
    "emotional_drivers": {{...}},
    "key_concepts": [...]
  }}
}}

JSON으로 응답:
"""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        wv_data = json.loads(response.choices[0].message.content)

        # DB 저장
        worldview = {
            'title': f"{wv_data['category']} > {wv_data['title']}",
            'frame': json.dumps({
                'category': wv_data['category'],
                'subcategory': wv_data['title'],
                'narrative': wv_data['narrative'],
                'metadata': wv_data['metadata']
            }, ensure_ascii=False),
            'description': wv_data['narrative']['summary'],
            'core_subject': wv_data['metadata']['core']['primary_subject'],
            'core_attributes': wv_data['metadata'].get('key_concepts', []),
            'overall_valence': 'negative'
        }

        result = self.supabase.table('worldviews').insert(worldview).execute()

        return result.data[0]
