"""
WorldviewEvolutionEngine - 살아있는 세계관 시스템

주기적으로 전체 perception을 재분석하여:
1. 새로운 세계관 발견
2. 기존 세계관 변화 감지
3. 사라진 세계관 아카이브
4. 세계관 분리/병합

실시간으로 담론 변화를 추적하는 살아있는 시스템
"""

from openai import AsyncOpenAI
import os
import json
from typing import Dict, List, Tuple
from datetime import datetime
from engines.utils.supabase_client import get_supabase

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


class WorldviewEvolutionEngine:
    """Evolving worldview system that adapts to discourse changes"""

    def __init__(self):
        self.supabase = get_supabase()

    async def run_evolution_cycle(self, sample_size: int = 200) -> Dict:
        """
        Run a complete evolution cycle

        Args:
            sample_size: Number of recent perceptions to analyze

        Returns:
            Evolution report with changes detected
        """

        print("\n" + "="*80)
        print("세계관 진화 사이클 시작")
        print("="*80)

        # 1. Load recent perceptions
        perceptions = await self._load_recent_perceptions(sample_size)
        print(f"\n✅ 최근 {len(perceptions)}개 perception 로드")

        # 2. Extract new worldviews from current data
        new_worldviews = await self._consolidate_worldviews(perceptions)
        print(f"\n✅ {len(new_worldviews)}개 세계관 추출")

        # 3. Load existing worldviews
        existing_worldviews = await self._load_existing_worldviews()
        print(f"\n✅ 기존 {len(existing_worldviews)}개 세계관 로드")

        # 4. Compare and detect changes
        changes = await self._detect_changes(existing_worldviews, new_worldviews)
        print(f"\n✅ 변화 감지 완료")

        # 5. Apply changes (if significant)
        if changes['significant']:
            await self._apply_changes(changes)
            print(f"\n✅ 변화 적용 완료")
        else:
            print(f"\n⚠️  유의미한 변화 없음 (변화 적용 건너뜀)")

        # 6. Generate report
        report = self._generate_report(changes)

        print("\n" + "="*80)
        print("세계관 진화 사이클 완료")
        print("="*80)

        return report

    async def _load_recent_perceptions(self, limit: int) -> List[Dict]:
        """Load most recent perceptions with reasoning structures"""

        perceptions = self.supabase.table('layered_perceptions')\
            .select('id, content_id, mechanisms, actor, logic_chain, consistency_pattern, deep_beliefs, implicit_assumptions, created_at')\
            .not_.is_('mechanisms', 'null')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute().data

        # Filter out perceptions without mechanisms
        perceptions = [p for p in perceptions if p.get('mechanisms') and len(p.get('mechanisms', [])) > 0]

        return perceptions

    async def _consolidate_worldviews(self, perceptions: List[Dict]) -> List[Dict]:
        """
        Use GPT-5 to consolidate perceptions into 5-10 core worldviews

        Args:
            perceptions: List of perception dicts with reasoning structures

        Returns:
            List of worldview dicts
        """

        # Prepare summary data
        summary_data = []
        for p in perceptions[:200]:  # Limit for GPT token constraints
            summary_data.append({
                'mechanisms': p.get('mechanisms', []),
                'actor': p.get('actor', {}).get('subject', ''),
                'purpose': p.get('actor', {}).get('purpose', ''),
                'pattern': p.get('consistency_pattern', ''),
                'logic_chain': p.get('logic_chain', [])[:3]
            })

        prompt = f"""
다음은 DC Gallery 정치 글 {len(summary_data)}개의 추론 구조 분석 결과입니다.

{json.dumps(summary_data, ensure_ascii=False, indent=1)}

이 데이터를 분석해서 **5-10개의 핵심 세계관**을 추출해주세요.

**요구사항:**

1. 각 세계관은 **추론 메커니즘 기반**이어야 합니다 (주제가 아님)
   - 좋은 예: "민주당의 어떤 행동도 독재 시도로 해석하는 구조"
   - 나쁜 예: "민주당에 대한 인식" (이건 주제임)

2. 각 세계관은 **다양한 사건에 적용 가능**해야 합니다
   - 유심교체, 집회제한, 법안발의 등 전혀 다른 사건에도 같은 논리 적용

3. 행위자 중심으로 분류:
   - 민주당/좌파에 대한 해석
   - 중국에 대한 해석
   - 언론/사법부에 대한 해석
   - 보수 진영 자신들에 대한 해석

4. 각 세계관마다:
   - 핵심 메커니즘 (즉시_단정, 필연적_인과 등)
   - 행위자
   - 추정 목적
   - 논리 구조 (A → B → C)

JSON 형식:
{{
  "worldviews": [
    {{
      "title": "민주당/좌파의 정보 파악 → 즉시 불법/사찰로 해석",
      "actor": "민주당/좌파",
      "core_mechanisms": ["즉시_단정", "역사_투사"],
      "logic_pattern": {{
        "trigger": "민주당이 어떤 정보를 알고 있음",
        "skipped_verification": ["정보 출처 확인", "합법 가능성"],
        "conclusion": "불법 사찰 및 독재 시도"
      }},
      "examples": ["유심교체 정보", "집회 정보"],
      "estimated_coverage_pct": 15
    }}
  ]
}}

**중요:** 통합 시 특정성을 잃지 마세요. 각 세계관은 구체적인 논리 패턴을 가져야 합니다.
"""

        print("\n🤖 GPT-5로 세계관 클러스터링 중...")

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert in cognitive structure analysis. Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        worldviews = result.get('worldviews', [])

        # Print summary
        for i, wv in enumerate(worldviews, 1):
            print(f"  {i}. {wv['title']}")
            print(f"     행위자: {wv['actor']}, 메커니즘: {', '.join(wv['core_mechanisms'][:2])}")

        return worldviews

    async def _load_existing_worldviews(self) -> List[Dict]:
        """Load existing worldviews from database"""

        worldviews = self.supabase.table('worldviews')\
            .select('*')\
            .execute().data

        return worldviews

    async def _detect_changes(self, existing: List[Dict], new: List[Dict]) -> Dict:
        """
        Detect changes between existing and new worldviews

        Returns:
            Dict with change details
        """

        print("\n" + "="*80)
        print("변화 감지")
        print("="*80)

        # Parse existing worldview structures
        existing_parsed = []
        for wv in existing:
            try:
                frame = json.loads(wv.get('frame', '{}'))
                existing_parsed.append({
                    'id': wv['id'],
                    'title': wv['title'],
                    'frame': frame
                })
            except:
                # Old format worldview - treat as legacy
                existing_parsed.append({
                    'id': wv['id'],
                    'title': wv['title'],
                    'frame': {}
                })

        # Compare using GPT-5
        comparison_prompt = f"""
기존 세계관 ({len(existing_parsed)}개):
{json.dumps([{'title': e['title']} for e in existing_parsed], ensure_ascii=False, indent=2)}

새 세계관 ({len(new)}개):
{json.dumps([{'title': w['title'], 'actor': w['actor']} for w in new], ensure_ascii=False, indent=2)}

이 두 세계관 목록을 비교하고 변화를 분석해주세요:

1. **새로 등장한 세계관** (기존에 없던 것)
2. **사라진 세계관** (새 목록에 없는 것)
3. **변화한 세계관** (비슷하지만 내용이 달라진 것)
4. **유지된 세계관** (거의 같은 것)

JSON 형식:
{{
  "new_worldviews": ["새 세계관 title 1", ...],
  "disappeared_worldviews": ["사라진 세계관 title 1", ...],
  "evolved_worldviews": [
    {{
      "old_title": "기존 title",
      "new_title": "새 title",
      "change_description": "변화 설명"
    }}
  ],
  "stable_worldviews": ["유지된 세계관 title 1", ...],
  "significant": true,  // 유의미한 변화가 있는가?
  "summary": "변화 요약 (1-2문장)"
}}
"""

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert in comparing worldview structures. Always respond in valid JSON."},
                {"role": "user", "content": comparison_prompt}
            ],
            response_format={"type": "json_object"}
        )

        changes = json.loads(response.choices[0].message.content)

        # Add actual worldview objects
        changes['new_worldview_objects'] = [
            wv for wv in new if wv['title'] in changes.get('new_worldviews', [])
        ]
        changes['disappeared_worldview_ids'] = [
            wv['id'] for wv in existing_parsed if wv['title'] in changes.get('disappeared_worldviews', [])
        ]

        # Print summary
        print(f"\n신규: {len(changes.get('new_worldviews', []))}개")
        print(f"소멸: {len(changes.get('disappeared_worldviews', []))}개")
        print(f"진화: {len(changes.get('evolved_worldviews', []))}개")
        print(f"유지: {len(changes.get('stable_worldviews', []))}개")
        print(f"\n요약: {changes.get('summary', '')}")

        return changes

    async def _apply_changes(self, changes: Dict):
        """
        Apply detected changes to database

        1. Archive disappeared worldviews
        2. Insert new worldviews
        3. Update evolved worldviews
        """

        print("\n" + "="*80)
        print("변화 적용")
        print("="*80)

        # 1. Archive disappeared worldviews
        for wv_id in changes.get('disappeared_worldview_ids', []):
            self.supabase.table('worldviews')\
                .update({
                    'archived': True,
                    'archived_at': datetime.now().isoformat()
                })\
                .eq('id', wv_id)\
                .execute()
            print(f"  📦 아카이브: {wv_id}")

        # 2. Insert new worldviews
        for wv_data in changes.get('new_worldview_objects', []):
            await self._insert_worldview(wv_data)
            print(f"  ✨ 신규 생성: {wv_data['title']}")

        # 3. Update evolved worldviews
        # (For now, just create new versions - can be enhanced later)

        print(f"\n✅ {len(changes.get('new_worldview_objects', []))}개 신규, {len(changes.get('disappeared_worldview_ids', []))}개 아카이브")

    async def _insert_worldview(self, wv_data: Dict):
        """Insert a new worldview into database"""

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
            'perception_ids': []
        }

        self.supabase.table('worldviews').insert(worldview).execute()

    def _generate_report(self, changes: Dict) -> Dict:
        """Generate evolution report"""

        return {
            'timestamp': datetime.now().isoformat(),
            'changes_detected': changes.get('significant', False),
            'summary': changes.get('summary', ''),
            'new_count': len(changes.get('new_worldviews', [])),
            'disappeared_count': len(changes.get('disappeared_worldviews', [])),
            'evolved_count': len(changes.get('evolved_worldviews', [])),
            'stable_count': len(changes.get('stable_worldviews', [])),
            'details': changes
        }
