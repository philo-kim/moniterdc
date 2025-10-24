"""
PatternManager - Dynamic pattern lifecycle management

Manages the living ecosystem of worldview patterns:
- Surface layer: Fast-changing (events, 7 days)
- Implicit layer: Medium-changing (assumptions, 30 days)
- Deep layer: Slow-changing (beliefs, 90 days)

Patterns are added, reinforced, weakened, and removed organically.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
from engines.utils.supabase_client import get_supabase

# Initialize embedding model (multilingual, 1024 dimensions)
# Using paraphrase-multilingual-mpnet-base-v2 for Korean support
embedding_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')


class PatternManager:
    """
    Manages dynamic pattern lifecycle for worldviews

    Key methods:
    - integrate_perception(): Add new perception to pattern pool
    - find_similar_pattern(): Check if pattern already exists
    - reinforce_pattern(): Strengthen existing pattern
    - create_pattern(): Add new pattern
    - decay_patterns(): Weaken old patterns
    - cleanup_dead_patterns(): Remove dead patterns
    """

    def __init__(self):
        self.supabase = get_supabase()

        # Layer-specific thresholds
        self.SIMILARITY_THRESHOLDS = {
            'surface': 0.85,   # Strict (specific events)
            'implicit': 0.70,  # Medium (patterns)
            'deep': 0.60       # Lenient (fundamental beliefs)
        }

        # Decay rates (per day)
        self.DECAY_RATES = {
            'surface': 0.7,    # 30% per day
            'implicit': 0.9,   # 10% per week
            'deep': 0.95       # 5% per month
        }

        # Expiration days (3-month window)
        self.EXPIRATION_DAYS = {
            'surface': 7,
            'implicit': 30,
            'deep': 90  # 3 months - aligned with content archiving
        }


    def integrate_perception(self, worldview_id: str, perception: Dict) -> Dict:
        """
        Integrate a new perception into the worldview's pattern pool

        For each layer:
        1. Check if item matches existing patterns
        2. If match: reinforce existing pattern
        3. If no match: create new pattern

        Returns:
            Statistics about integration (matched, new, reinforced)
        """
        stats = {
            'surface': {'matched': 0, 'new': 0},
            'implicit': {'matched': 0, 'new': 0},
            'deep': {'matched': 0, 'new': 0}
        }

        # Process surface layer (explicit_claims)
        for claim in perception.get('explicit_claims', []):
            matched = self.find_similar_pattern(worldview_id, 'surface', claim)
            if matched:
                self.reinforce_pattern(matched['id'])
                stats['surface']['matched'] += 1
            else:
                pattern_id = self.create_pattern(worldview_id, 'surface', claim)
                if pattern_id:  # Only count if not filtered
                    stats['surface']['new'] += 1

        # Process implicit layer (implicit_assumptions)
        for assumption in perception.get('implicit_assumptions', []):
            matched = self.find_similar_pattern(worldview_id, 'implicit', assumption)
            if matched:
                self.reinforce_pattern(matched['id'])
                stats['implicit']['matched'] += 1
            else:
                pattern_id = self.create_pattern(worldview_id, 'implicit', assumption)
                if pattern_id:
                    stats['implicit']['new'] += 1

        # Process deep layer (deep_beliefs)
        for belief in perception.get('deep_beliefs', []):
            matched = self.find_similar_pattern(worldview_id, 'deep', belief)
            if matched:
                self.reinforce_pattern(matched['id'])
                stats['deep']['matched'] += 1
            else:
                pattern_id = self.create_pattern(worldview_id, 'deep', belief)
                if pattern_id:
                    stats['deep']['new'] += 1

        return stats


    def find_similar_pattern(
        self,
        worldview_id: str,
        layer: str,
        text: str
    ) -> Optional[Dict]:
        """
        Find if a similar pattern already exists

        Uses embedding similarity with layer-specific thresholds:
        - Surface: 0.85+ (strict, events are specific)
        - Implicit: 0.70+ (medium, patterns repeat)
        - Deep: 0.60+ (lenient, beliefs are fundamental)

        Returns:
            Matched pattern dict or None
        """
        # Get embedding for new text
        embedding = self._get_embedding(text)

        # Get threshold for this layer
        threshold = self.SIMILARITY_THRESHOLDS[layer]

        # Query for similar patterns using vector similarity
        # Note: This uses pgvector's <=> operator for cosine distance
        # 1 - distance = similarity, so we need 1 - threshold as max distance
        max_distance = 1 - threshold

        result = self.supabase.rpc(
            'find_similar_patterns',
            {
                'target_worldview_id': worldview_id,
                'target_layer': layer,
                'target_embedding': embedding,
                'max_distance': max_distance,
                'limit_count': 1
            }
        ).execute()

        if result.data and len(result.data) > 0:
            return result.data[0]

        return None


    def reinforce_pattern(self, pattern_id: str) -> None:
        """
        Reinforce an existing pattern

        - Increase strength by 0.5 (max 10.0)
        - Update last_seen to now
        - Increment appearance_count
        - Set status to 'active'
        """
        result = self.supabase.table('worldview_patterns').select('strength, appearance_count').eq('id', pattern_id).single().execute()

        if result.data:
            current_strength = result.data['strength']
            current_count = result.data['appearance_count']

            new_strength = min(10.0, current_strength + 0.5)

            self.supabase.table('worldview_patterns').update({
                'strength': new_strength,
                'last_seen': datetime.now().isoformat(),
                'appearance_count': current_count + 1,
                'status': 'active'
            }).eq('id', pattern_id).execute()


    def create_pattern(self, worldview_id: str, layer: str, text: str) -> str:
        """
        Create a new pattern with enhanced fast filter (Phase 1)

        Phase 1: Rule-based filtering (fast, no cost)
        - Filters out obviously bad patterns
        - ~17% filtered for surface layer

        Phase 2 (periodic): Claude-based validation
        - See cleanup_low_quality_patterns() method
        - Validates suspicious weak patterns

        Returns:
            Pattern ID or None if filtered out
        """
        # 표면층 필터링: Phase 1 - Enhanced Fast Filter
        if layer == 'surface':
            should_keep, reason = self._fast_filter_surface(text)
            if not should_keep:
                return None

        embedding = self._get_embedding(text)

        result = self.supabase.table('worldview_patterns').insert({
            'worldview_id': worldview_id,
            'layer': layer,
            'text': text,
            'embedding': embedding,
            'strength': 1.0,
            'status': 'active',
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'appearance_count': 1
        }).execute()

        return result.data[0]['id']


    def decay_patterns(self, worldview_id: Optional[str] = None) -> Dict:
        """
        Apply natural decay to all patterns based on inactivity

        Decay rates (per day inactive):
        - Surface: 30% per day
        - Implicit: 10% per 7 days
        - Deep: 5% per 30 days

        Args:
            worldview_id: If provided, only decay patterns for this worldview

        Returns:
            Statistics about decay (total, fading, dead per layer)
        """
        stats = {
            'surface': {'total': 0, 'fading': 0, 'dead': 0},
            'implicit': {'total': 0, 'fading': 0, 'dead': 0},
            'deep': {'total': 0, 'fading': 0, 'dead': 0}
        }

        for layer in ['surface', 'implicit', 'deep']:
            query = self.supabase.table('worldview_patterns').select('*').eq('layer', layer).in_('status', ['active', 'fading'])

            if worldview_id:
                query = query.eq('worldview_id', worldview_id)

            patterns = query.execute().data

            for pattern in patterns:
                stats[layer]['total'] += 1

                # Calculate days inactive
                last_seen = datetime.fromisoformat(pattern['last_seen'].replace('Z', '+00:00'))
                days_inactive = (datetime.now(last_seen.tzinfo) - last_seen).days

                if days_inactive == 0:
                    continue  # Active today, no decay

                # Apply decay
                current_strength = pattern['strength']
                decay_rate = self.DECAY_RATES[layer]
                new_strength = current_strength * (decay_rate ** days_inactive)

                # Determine new status
                new_status = pattern['status']
                expiration_days = self.EXPIRATION_DAYS[layer]

                if new_strength < 0.1:
                    new_status = 'dead'
                    stats[layer]['dead'] += 1
                elif days_inactive > expiration_days:
                    if layer == 'deep':
                        new_status = 'fading'  # Deep beliefs don't die, they fade
                        stats[layer]['fading'] += 1
                    else:
                        new_status = 'dead'
                        stats[layer]['dead'] += 1

                # Update pattern
                self.supabase.table('worldview_patterns').update({
                    'strength': new_strength,
                    'status': new_status
                }).eq('id', pattern['id']).execute()

        return stats


    def cleanup_dead_patterns(self, worldview_id: Optional[str] = None) -> int:
        """
        Remove dead patterns from database

        Args:
            worldview_id: If provided, only clean up for this worldview

        Returns:
            Number of patterns removed
        """
        query = self.supabase.table('worldview_patterns').delete().eq('status', 'dead')

        if worldview_id:
            query = query.eq('worldview_id', worldview_id)

        result = query.execute()

        return len(result.data) if result.data else 0


    def get_active_patterns(
        self,
        worldview_id: str,
        layer: Optional[str] = None,
        min_strength: float = 0.1
    ) -> List[Dict]:
        """
        Get active patterns for a worldview

        Args:
            worldview_id: Worldview ID
            layer: Optional layer filter ('surface', 'implicit', 'deep')
            min_strength: Minimum strength threshold

        Returns:
            List of active patterns, sorted by strength descending
        """
        query = self.supabase.table('worldview_patterns').select('*').eq('worldview_id', worldview_id).in_('status', ['active', 'fading']).gte('strength', min_strength)

        if layer:
            query = query.eq('layer', layer)

        result = query.order('strength', desc=True).execute()

        return result.data if result.data else []


    def _get_embedding(self, text: str) -> List[float]:
        """
        Get sentence embedding for text

        Uses paraphrase-multilingual-mpnet-base-v2 (768 dimensions)
        Supports Korean language
        """
        embedding = embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()


    def _fast_filter_surface(self, text: str) -> Tuple[bool, str]:
        """
        Phase 1: Enhanced fast filter for surface layer patterns

        Rule-based filtering (no cost, instant):
        - Filters ~17% of bad patterns
        - Remaining ~17% need Claude validation (Phase 2)

        Returns:
            (should_keep, reason_if_filtered)
        """
        text_clean = text.strip()

        # 1. 길이 체크
        if len(text_clean) < 10:
            return (False, "길이 < 10")

        # 2. 지시대명사로 시작
        pronouns_start = [
            '이는 ', '이는,', '이것은 ', '이것이 ', '그것은 ', '그것이 ',
            '여기는 ', '거기는 ', '저기는 '
        ]
        for p in pronouns_start:
            if text_clean.startswith(p):
                return (False, "지시대명사 시작")

        # 지시대명사 단독 (끝에 조사)
        if text_clean.startswith('이 ') or text_clean.startswith('그 ') or text_clean.startswith('저 '):
            # 단, "이 사건", "이 사람" 같은 경우는 허용
            if not any(text_clean.startswith(p) for p in ['이 사건', '이 사람', '이 일', '그 사건', '그 사람']):
                return (False, "지시대명사 시작")

        # 3. 대명사/막연한 주어로 시작
        vague_subjects = [
            '우리가 ', '우리는 ', '이들은 ', '이들이 ', '그들은 ', '그들이 ',
            '엄마들이 ', '좌파들이 ', '보수들이 ', '사람들이 '
        ]
        for s in vague_subjects:
            if text_clean.startswith(s):
                return (False, "막연한 주어")

        # 4. 당위문/규범문
        normative = ['해야 한다', '해야한다', '하자', '드리자', '말아야', '되어야']
        for n in normative:
            if n in text_clean:
                return (False, "당위문")

        # 5. 막연한 평가/감정 (구체적 주어 없으면 제거)
        vague_eval = ['웃기다', '다행', '부당', '적절', '나쁜', '좋은',
                      '이상하다', '복잡하다', '어렵다', '쉽다']

        # 구체적 주어 체크
        concrete_subjects = ['민주당', '국민의힘', '윤석열', '이재명',
                            '경찰', '검찰', '법원', '정부', '국회',
                            '대통령', '의원', '장관', '판사', '검사']

        has_concrete_subject = any(subj in text_clean for subj in concrete_subjects)

        if not has_concrete_subject:
            for v in vague_eval:
                if v in text_clean:
                    return (False, "막연한 평가")

        # 6. 불완전한 문장 (서술어 없음)
        # 한국어 종결어미 체크
        endings = ['다.', '다,', '다"', '다\'', '다!', '다?',
                   '까.', '까,', '까?',
                   '냐.', '냐,', '냐?',
                   '요.', '요,', '요!',
                   '음.', '음,']

        # 문장 끝에 종결어미가 있는지 체크
        has_ending = any(text_clean.endswith(end) for end in endings)

        # 또는 '다'로 끝나는지 (마침표 없어도)
        if not has_ending and not text_clean.endswith('다'):
            return (False, "불완전한 문장")

        # 7. 특수문자만 있는 이니셜 (ㅉ, ㅁㅈ 등)
        # 한글 자음만 있는 패턴
        korean_consonants = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
        if any(c in korean_consonants for c in text_clean[:3]):
            return (False, "자음 이니셜")

        return (True, "")


    def cleanup_low_quality_patterns(
        self,
        worldview_id: str,
        strength_threshold: float = 3.0,
        batch_size: int = 50
    ) -> Dict:
        """
        Phase 2: Periodic Claude-based quality validation

        Validates weak surface layer patterns using Claude:
        - Only checks patterns with strength < threshold
        - Batches patterns for efficiency
        - Removes patterns identified as low quality

        Args:
            worldview_id: Worldview to clean up
            strength_threshold: Only check patterns weaker than this
            batch_size: Patterns per Claude request

        Returns:
            Statistics about cleanup (checked, removed)
        """
        import anthropic
        import json

        # Get weak surface patterns
        weak_patterns = self.supabase.table('worldview_patterns').select('*').eq('worldview_id', worldview_id).eq('layer', 'surface').lt('strength', strength_threshold).in_('status', ['active', 'fading']).execute().data

        if not weak_patterns:
            return {'checked': 0, 'removed': 0}

        # Initialize Claude
        claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        stats = {'checked': 0, 'removed': 0}

        # Process in batches
        for i in range(0, len(weak_patterns), batch_size):
            batch = weak_patterns[i:i+batch_size]
            pattern_list = "\n".join([f"{idx+1}. {p['text']}" for idx, p in enumerate(batch)])

            prompt = f"""당신은 패턴 품질 평가 전문가입니다.

아래는 표면층 패턴들입니다. 각 패턴을 평가하여 **의미없거나 정보가치가 낮은 패턴**을 식별하세요.

패턴 목록:
{pattern_list}

나쁜 패턴의 특징:
1. 주어가 불명확 (누가?)
2. 내용이 모호함 (무엇을?)
3. 단순한 감정적 평가 ("미친짓이다", "심금을 울린다")
4. 일반론적 ("흐름이 바뀌고 있다")
5. 추측성 평가 without 근거

각 패턴을 평가하고, **제거해야 할 나쁜 패턴**만 JSON 배열로 출력하세요:

{{
  "bad_patterns": [
    {{"id": 번호, "reason": "이유"}},
    ...
  ]
}}

좋은 패턴은 출력하지 마세요. 나쁜 패턴만 출력하세요."""

            try:
                response = claude.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )

                result_text = response.content[0].text

                # Parse JSON
                if "```json" in result_text:
                    json_str = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    json_str = result_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = result_text

                result_data = json.loads(json_str)
                bad_patterns = result_data.get('bad_patterns', [])

                # Remove bad patterns
                for bp in bad_patterns:
                    pattern_idx = bp['id'] - 1  # 1-indexed to 0-indexed
                    if 0 <= pattern_idx < len(batch):
                        pattern_to_remove = batch[pattern_idx]
                        self.supabase.table('worldview_patterns').update({
                            'status': 'dead'
                        }).eq('id', pattern_to_remove['id']).execute()
                        stats['removed'] += 1

                stats['checked'] += len(batch)

            except Exception as e:
                print(f"Error in Claude validation: {str(e)}")
                continue

        return stats


# Helper function to create RPC function in Supabase
def create_similarity_search_function():
    """
    SQL function for vector similarity search

    Run this once in Supabase SQL editor:
    """
    sql = """
    CREATE OR REPLACE FUNCTION find_similar_patterns(
        target_worldview_id UUID,
        target_layer TEXT,
        target_embedding vector(1536),
        max_distance FLOAT DEFAULT 0.3,
        limit_count INT DEFAULT 10
    )
    RETURNS TABLE (
        id UUID,
        worldview_id UUID,
        layer TEXT,
        text TEXT,
        strength FLOAT,
        status TEXT,
        similarity FLOAT
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            wp.id,
            wp.worldview_id,
            wp.layer,
            wp.text,
            wp.strength,
            wp.status,
            1 - (wp.embedding <=> target_embedding) AS similarity
        FROM worldview_patterns wp
        WHERE wp.worldview_id = target_worldview_id
            AND wp.layer = target_layer
            AND wp.status IN ('active', 'fading')
            AND wp.embedding <=> target_embedding <= max_distance
        ORDER BY wp.embedding <=> target_embedding
        LIMIT limit_count;
    END;
    $$;
    """
    print(sql)
    return sql
