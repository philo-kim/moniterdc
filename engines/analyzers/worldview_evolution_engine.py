"""
WorldviewEvolutionEngine - 살아있는 세계관 시스템

주기적으로 전체 perception을 재분석하여:
1. 새로운 세계관 발견
2. 기존 세계관 변화 감지
3. 사라진 세계관 아카이브
4. 세계관 분리/병합

실시간으로 담론 변화를 추적하는 살아있는 시스템
"""

from anthropic import Anthropic
import os
import json
import asyncio
from typing import Dict, List, Tuple
from datetime import datetime
from engines.utils.supabase_client import get_supabase

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


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

        # Prepare statistics
        mechanism_counts = {}
        actor_counts = {}
        logic_chain_samples = []

        for p in perceptions[:200]:
            # Mechanisms
            for mech in p.get('mechanisms', []):
                mechanism_counts[mech] = mechanism_counts.get(mech, 0) + 1

            # Actors
            actor = p.get('actor', {})
            if isinstance(actor, dict):
                subj = actor.get('subject', 'Unknown')
                if isinstance(subj, list):
                    subj = ', '.join(str(s) for s in subj)
                elif not isinstance(subj, str):
                    subj = str(subj)
                actor_counts[subj] = actor_counts.get(subj, 0) + 1

            # Logic chain samples
            logic = p.get('logic_chain', [])
            if logic and len(logic) > 0:
                logic_chain_samples.append(logic[0])

        # Top stats
        top_mechs = sorted(mechanism_counts.items(), key=lambda x: x[1], reverse=True)
        top_actors = sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)

        # Sample data (simplified)
        sample_data = []
        for p in perceptions[:5]:
            sample_data.append({
                'mechanisms': p.get('mechanisms', []),
                'actor': p.get('actor', {}),
                'logic_chain': p.get('logic_chain', [])[:3] if p.get('logic_chain') else []
            })

        prompt = f"""
{len(perceptions)}개 담론 통계 분석:

## 메커니즘 빈도
{json.dumps(top_mechs, ensure_ascii=False, indent=2)}

## Actor 빈도
{json.dumps(top_actors, ensure_ascii=False, indent=2)}

## Logic Chain 시작점 샘플 (10개)
{json.dumps(logic_chain_samples[:10], ensure_ascii=False, indent=2)}

전체 데이터 샘플:
{json.dumps(sample_data, ensure_ascii=False, indent=2)}

---

## 데이터 기반 세계관 발견

### 분석 기준

1. **유의미한 공출현**: 어떤 메커니즘들이 자주 함께 나타나는가?
2. **지배적 Actor**: 가장 자주 언급되는 Actor는?
3. **공통 Logic 패턴**: Logic Chain 시작점의 공통점은?

### 세계관 정의

위 통계를 바탕으로 **5-10개의 핵심 세계관**을 정의하세요.

⚠️ 주의: 단순 빈도가 아닌 **의미있는 조합**을 찾으세요.

## 🎯 세계관 제목 작성 원칙 (매우 중요!)

**DC Gallery 사용자들의 실제 언어와 시각**으로 표현하세요.

❌ 나쁜 예 (학술적/객관적 표현):
- "즉시 단정형 음모론 세계관"
- "역사 반복 필연론 세계관"
- "외부 세력 침투론 세계관"

✅ 좋은 예 (그들의 언어로):
- "중국/좌파가 댓글부대로 여론을 조작한다"
- "민주당은 과거 독재처럼 사찰로 국민을 감시한다"
- "이재명은 네트워크로 권력을 유지한다"
- "정부는 권력을 악용해 국민을 탄압한다"
- "언론은 진실을 왜곡하여 조작한다"

**형식**: "[행위자]는/가 [행동]한다" (30-50자)
**톤**: DC Gallery 사용자가 직접 말하는 것처럼

JSON 형식:
{{
  "worldviews": [
    {{
      "title": "세계관 제목 - DC 사용자 언어로 (30-50자)",
      "description": "핵심 특징 (2-3문장)",
      "actor": {{
        "subject": "주체",
        "purpose": "목적",
        "methods": ["수단1", "수단2", "수단3"]
      }},
      "core_mechanisms": ["메커니즘1", "메커니즘2", "메커니즘3"],
      "logic_pattern": {{
        "trigger": "시작",
        "skipped_verification": "생략",
        "conclusion": "결론"
      }},
      "statistical_basis": {{
        "top_mechanisms": ["메커니즘들"],
        "top_actor": "Actor",
        "occurrence_count": 숫자
      }}
    }}
  ]
}}
"""

        print("\n🤖 Claude로 세계관 발견 중 (Data-Driven)...")

        # Claude Sonnet 4.5 (Data-Driven 프롬프트)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8192,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        )

        response_text = response.content[0].text

        # Parse JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
        else:
            json_str = response_text

        result = json.loads(json_str)
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

        # Claude Sonnet 4.5
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0,
                messages=[
                    {"role": "user", "content": comparison_prompt}
                ]
            )
        )

        response_text = response.content[0].text

        # Parse JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
        else:
            json_str = response_text

        changes = json.loads(json_str)

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
