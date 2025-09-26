"""
Logic Defense System - Attack vs Defense Matcher
공격 논리에 대한 최적 방어 논리 자동 매칭
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from dotenv import load_dotenv

from openai import AsyncOpenAI
from supabase import create_client, Client
import numpy as np

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)

# 환경변수
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def safe_json_loads(text, default=None):
    """안전한 JSON 파싱"""
    if not text or text.strip() == '':
        return default or {}
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default or {}


class MatchConfidence(Enum):
    """매칭 확신도 레벨"""
    PERFECT = "perfect"      # 90% 이상
    EXCELLENT = "excellent"  # 80-90%
    GOOD = "good"           # 70-80%
    MODERATE = "moderate"   # 60-70%
    WEAK = "weak"          # 50-60%


class LogicDefenseMatcher:
    """공격 vs 방어 논리 매칭 엔진"""
    
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.openai = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
        
    async def get_unmatched_attacks(self, limit: int = 10) -> List[Dict]:
        """매칭되지 않은 공격 논리 조회"""
        try:
            # 직접 쿼리로 매칭되지 않은 공격 조회
            result = self.supabase.table('logic_repository').select('*').eq(
                'logic_type', 'attack'
            ).eq(
                'is_active', True
            ).not_.is_(
                'vector_embedding', 'null'
            ).order(
                'threat_level', desc=True
            ).order(
                'created_at', desc=True
            ).limit(limit).execute()
            
            attacks = result.data if result.data else []
            
            # 이미 매칭된 것들 필터링
            unmatched = []
            for attack in attacks:
                matches = self.supabase.table('logic_matches').select('id').eq(
                    'attack_id', attack['id']
                ).execute()
                
                if not matches.data:  # 매칭 없음
                    unmatched.append(attack)
                    
            return unmatched
            
        except Exception as e:
            self.logger.error(f"Error fetching unmatched attacks: {str(e)}")
            return []
    
    async def get_available_defenses(self, category: str = None) -> List[Dict]:
        """사용 가능한 방어 논리 조회"""
        try:
            query = self.supabase.table('logic_repository').select('*').eq(
                'logic_type', 'defense'
            ).eq(
                'is_active', True
            ).not_.is_(
                'vector_embedding', 'null'
            )
            
            # 카테고리 필터
            if category:
                query = query.filter('ai_classification->category', 'eq', category)
            
            result = query.order(
                'effectiveness_score', desc=True
            ).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            self.logger.error(f"Error fetching defenses: {str(e)}")
            return []
    
    async def find_best_defenses_for_attack(self, attack: Dict, limit: int = 5) -> List[Dict]:
        """공격에 대한 최적 방어 논리 찾기"""
        
        # 1. 벡터 임베딩이 있는 경우 벡터 검색
        if attack.get('vector_embedding'):
            defenses = await self._vector_search_defenses(attack['vector_embedding'], limit * 2, attack.get('id'))
        else:
            # 2. 임베딩이 없으면 카테고리/키워드 기반 검색
            ai_class = safe_json_loads(attack.get('ai_classification'))
            category = ai_class.get('category') if ai_class else None
            defenses = await self.get_available_defenses(category)
        
        if not defenses:
            self.logger.warning(f"No defenses found for attack {attack['id'][:8]}")
            return []
        
        # 3. GPT-5로 정밀 평가
        scored_defenses = await self._score_defenses_for_attack(attack, defenses[:limit*2])
        
        # 4. 상위 N개 선택
        return scored_defenses[:limit]
    
    async def _vector_search_defenses(self, attack_embedding: List[float], limit: int, attack_logic_id: str = None) -> List[Dict]:
        """벡터 유사도 기반 방어 논리 검색"""
        try:
            # PostgreSQL 함수 호출 (올바른 파라미터 사용)
            if attack_logic_id:
                result = self.supabase.rpc(
                    'find_defense_for_attack',
                    {
                        'attack_logic_id': attack_logic_id,
                        'confidence_threshold': 0.6,
                        'max_results': limit
                    }
                ).execute()
            else:
                # 벡터 기반 검색은 수동으로 처리
                result = None
            
            if result.data:
                return result.data
                
            # 함수가 없으면 수동 검색
            all_defenses = await self.get_available_defenses()
            
            # 코사인 유사도 계산
            # 벡터가 문자열인 경우 JSON 파싱
            if isinstance(attack_embedding, str):
                attack_embedding = safe_json_loads(attack_embedding, [])
            attack_vec = np.array(attack_embedding, dtype=np.float32)
            similarities = []

            for defense in all_defenses:
                if defense.get('vector_embedding'):
                    defense_embedding = defense['vector_embedding']
                    if isinstance(defense_embedding, str):
                        defense_embedding = safe_json_loads(defense_embedding, [])
                    defense_vec = np.array(defense_embedding, dtype=np.float32)
                    similarity = np.dot(attack_vec, defense_vec) / (
                        np.linalg.norm(attack_vec) * np.linalg.norm(defense_vec)
                    )
                    defense['similarity'] = float(similarity)
                    similarities.append(defense)
            
            # 유사도 순 정렬
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            self.logger.error(f"Vector search error: {str(e)}")
            return []
    
    async def _score_defenses_for_attack(self, attack: Dict, defenses: List[Dict]) -> List[Dict]:
        """GPT-5를 사용한 공격-방어 매칭 점수 계산"""
        
        if not defenses:
            return []
        
        prompt = f"""
다음 공격 논리에 대한 각 방어 논리의 효과성을 평가하세요.

**공격 논리:**
- 핵심: {attack['core_argument']}
- 키워드: {', '.join(attack.get('keywords', []))}
- 위협도: {attack.get('threat_level', 0)}/10
- 카테고리: {safe_json_loads(attack.get('ai_classification')).get('category', '일반')}

**방어 논리 목록:**
{json.dumps([{
    'id': d['id'],
    'argument': d['core_argument'],
    'keywords': d.get('keywords', []),
    'evidence_quality': d.get('evidence_quality', 0.5)
} for d in defenses[:10]], ensure_ascii=False, indent=2)}

각 방어에 대해 평가:
1. match_score: 매칭 점수 (0-1)
2. effectiveness: 예상 효과성 (0-1)
3. strategy_type: 대응 전략 유형
   - direct_counter: 직접 반박
   - fact_check: 팩트 체크
   - reframe: 프레임 전환
   - deflect: 논점 전환
   - emotional: 감성적 대응
4. confidence: 확신도 (0-1)
5. reason: 추천 이유 (한 문장)

JSON 형식:
{{
  "evaluations": [
    {{
      "defense_id": "...",
      "match_score": 0.85,
      "effectiveness": 0.8,
      "strategy_type": "direct_counter",
      "confidence": 0.9,
      "reason": "핵심 논점을 정확히 반박"
    }}
  ]
}}
"""

        try:
            response = await self.openai.chat.completions.create(
                model="gpt-5-mini",  # temperature 제거
                messages=[
                    {"role": "system", "content": "정치 논리 대응 전문가. 공격에 대한 최적 방어를 찾습니다."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            evaluations = result.get('evaluations', [])
            
            # 평가 결과를 방어 논리에 매핑
            for defense in defenses:
                eval_data = next((e for e in evaluations if e['defense_id'] == defense['id']), {})
                defense['match_score'] = float(eval_data.get('match_score', 0))
                defense['effectiveness'] = float(eval_data.get('effectiveness', 0))
                defense['strategy_type'] = eval_data.get('strategy_type', 'unknown')
                defense['confidence'] = float(eval_data.get('confidence', 0))
                defense['match_reason'] = eval_data.get('reason', '')
            
            # 매칭 점수 순으로 정렬
            defenses.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            # 일정 점수 이상만 반환
            return [d for d in defenses if d.get('match_score', 0) >= 0.6]
            
        except Exception as e:
            self.logger.error(f"GPT scoring error: {str(e)}")
            # 오류시 유사도 기준으로 반환
            defenses.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            return defenses[:5]
    
    async def create_match(self, attack_id: str, defense_id: str, confidence: float, 
                           strategy_type: str, reason: str) -> Optional[Dict]:
        """공격-방어 매칭 생성"""
        try:
            match_data = {
                'attack_id': attack_id,
                'defense_id': defense_id,
                'match_confidence': confidence,
                'match_reason': f"[{strategy_type}] {reason}"
            }
            
            result = self.supabase.table('logic_matches').upsert(
                match_data,
                on_conflict='attack_id,defense_id'
            ).execute()
            
            if result.data:
                self.logger.info(f"Created match: Attack {attack_id[:8]} → Defense {defense_id[:8]} (conf: {confidence:.2f})")
                return result.data[0]
            
        except Exception as e:
            self.logger.error(f"Error creating match: {str(e)}")
            return None
    
    async def process_single_attack(self, attack: Dict) -> List[Dict]:
        """단일 공격에 대한 방어 매칭 처리"""
        
        self.logger.info(f"Processing attack: {attack['core_argument'][:50]}...")
        
        # 1. 최적 방어 찾기
        defenses = await self.find_best_defenses_for_attack(attack, limit=3)
        
        if not defenses:
            self.logger.warning(f"No suitable defenses for attack {attack['id'][:8]}")
            await self._create_no_defense_alert(attack)
            return []
        
        # 2. 매칭 생성
        created_matches = []
        for defense in defenses:
            if defense.get('match_score', 0) >= 0.7:  # 일정 점수 이상만
                match = await self.create_match(
                    attack['id'],
                    defense['id'],
                    defense['match_score'],
                    defense.get('strategy_type', 'general'),
                    defense.get('match_reason', '자동 매칭')
                )
                if match:
                    created_matches.append({
                        'attack': attack,
                        'defense': defense,
                        'match': match
                    })
        
        # 3. 알림 생성
        if created_matches:
            await self._create_match_alert(attack, created_matches)
        
        return created_matches
    
    async def _create_match_alert(self, attack: Dict, matches: List[Dict]):
        """매칭 성공 알림 생성"""
        try:
            best_match = matches[0]
            defense = best_match['defense']
            
            # 긴급도 판단
            severity = self._determine_severity(attack, defense)
            
            message = f"""
🎯 **공격-방어 매칭 완료**

**🔴 공격 논리:**
• 출처: {attack.get('source_gallery', 'uspolitics')}
• 내용: {attack['core_argument'][:100]}...
• 위협도: {attack.get('threat_level', 0)}/10

**🛡️ 최적 방어:**
• 출처: {defense.get('source_gallery', 'minjudang')}
• 내용: {defense['core_argument'][:100]}...
• 매칭도: {defense.get('match_score', 0):.0%}

**💡 대응 전략:** {defense.get('strategy_type', 'direct_counter')}
**📝 추천 이유:** {defense.get('match_reason', '')}

**추가 방어 옵션:** {len(matches)-1}개

---
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#LogicDefense #자동매칭
"""
            
            alert_data = {
                'alert_type': 'attack_defense_match',
                'severity': severity,
                'title': f"[{severity.upper()}] 공격 논리 매칭: {attack['core_argument'][:30]}...",
                'message': message,
                'metadata': {
                    'attack_id': attack['id'],
                    'defense_id': defense['id'],
                    'match_score': defense.get('match_score', 0),
                    'strategy_type': defense.get('strategy_type'),
                    'threat_level': attack.get('threat_level', 0),
                    'additional_defenses': len(matches) - 1
                },
                'send_channel': 'telegram'
            }
            
            self.supabase.table('alerts').insert(alert_data).execute()
            self.logger.info(f"Created {severity} alert for attack-defense match")
            
        except Exception as e:
            self.logger.error(f"Error creating match alert: {str(e)}")
    
    async def _create_no_defense_alert(self, attack: Dict):
        """방어 논리 없음 알림 생성"""
        try:
            message = f"""
⚠️ **방어 논리 부재 - 긴급 대응 필요**

**🔴 무방비 공격:**
• 출처: {attack.get('source_gallery', 'uspolitics')}
• 내용: {attack['core_argument']}
• 위협도: {attack.get('threat_level', 0)}/10
• 키워드: {', '.join(attack.get('keywords', [])[:5])}

**❗ 즉시 필요한 조치:**
1. 팩트체크 팀 가동
2. 대응 논리 긴급 개발
3. 관련 부서 상황 파악

**⏰ 권장 대응 시한:** 1시간 이내

---
🚨 방어 논리가 없는 공격입니다. 신속한 대응이 필요합니다.
"""
            
            alert_data = {
                'alert_type': 'no_defense_available',
                'severity': 'critical',
                'title': f"[CRITICAL] 무방비 공격: {attack['core_argument'][:30]}...",
                'message': message,
                'metadata': {
                    'attack_id': attack['id'],
                    'threat_level': attack.get('threat_level', 0),
                    'keywords': attack.get('keywords', []),
                    'requires_immediate_action': True
                },
                'send_channel': 'telegram'
            }
            
            self.supabase.table('alerts').insert(alert_data).execute()
            self.logger.warning(f"Created CRITICAL alert for undefended attack")
            
        except Exception as e:
            self.logger.error(f"Error creating no-defense alert: {str(e)}")
    
    def _determine_severity(self, attack: Dict, defense: Dict) -> str:
        """알림 긴급도 결정"""
        threat_level = attack.get('threat_level', 0)
        match_score = defense.get('match_score', 0)
        
        # 위협도 높고 매칭 낮음 = 위험
        if threat_level >= 8 and match_score < 0.7:
            return 'critical'
        elif threat_level >= 7 or (threat_level >= 5 and match_score < 0.8):
            return 'high'
        elif threat_level >= 5:
            return 'medium'
        else:
            return 'low'
    
    async def batch_process_attacks(self):
        """배치로 공격 논리 처리"""
        
        # 1. 미매칭 공격들 조회
        attacks = await self.get_unmatched_attacks(limit=10)
        
        if not attacks:
            self.logger.info("No unmatched attacks found")
            return []
        
        self.logger.info(f"Processing {len(attacks)} unmatched attacks")
        
        # 2. 각 공격 처리
        all_matches = []
        for attack in attacks:
            matches = await self.process_single_attack(attack)
            all_matches.extend(matches)
            await asyncio.sleep(1)  # Rate limiting
        
        # 3. 요약 리포트
        if all_matches:
            await self._create_summary_report(all_matches)
        
        return all_matches
    
    async def _create_summary_report(self, matches: List[Dict]):
        """배치 처리 요약 리포트"""
        try:
            total = len(matches)
            avg_confidence = sum(m['match']['match_confidence'] for m in matches) / total if total > 0 else 0
            
            strategies = {}
            for m in matches:
                strategy = m['defense'].get('strategy_type', 'unknown')
                strategies[strategy] = strategies.get(strategy, 0) + 1
            
            message = f"""
📊 **공격-방어 매칭 일일 리포트**

**처리 결과:**
• 총 매칭: {total}건
• 평균 확신도: {avg_confidence:.0%}

**전략 분포:**
{chr(10).join([f"• {k}: {v}건" for k, v in strategies.items()])}

**상위 매칭 (Top 3):**
{chr(10).join([
    f"{i+1}. {m['attack']['core_argument'][:30]}... → {m['defense']['core_argument'][:30]}... ({m['match']['match_confidence']:.0%})"
    for i, m in enumerate(matches[:3])
])}

---
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#일일리포트 #LogicDefense
"""
            
            alert_data = {
                'alert_type': 'daily_report',
                'severity': 'low',
                'title': f"매칭 리포트: {total}건 처리 완료",
                'message': message,
                'metadata': {
                    'total_matches': total,
                    'avg_confidence': avg_confidence,
                    'strategy_distribution': strategies
                },
                'send_channel': 'telegram'
            }
            
            self.supabase.table('alerts').insert(alert_data).execute()
            
        except Exception as e:
            self.logger.error(f"Error creating summary report: {str(e)}")


class DefenseOrchestrator:
    """전체 방어 시스템 오케스트레이터"""
    
    def __init__(self):
        self.matcher = LogicDefenseMatcher()
        self.logger = logging.getLogger(__name__)
    
    async def run_continuous_matching(self):
        """지속적인 공격-방어 매칭"""
        
        self.logger.info("Starting continuous attack-defense matching...")
        
        while True:
            try:
                # 1. 배치 처리
                matches = await self.matcher.batch_process_attacks()
                
                if matches:
                    self.logger.info(f"Processed {len(matches)} attack-defense matches")
                else:
                    self.logger.info("No new attacks to match")
                
                # 2. 대기 (5분)
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in continuous matching: {str(e)}")
                await asyncio.sleep(60)  # 에러시 1분 대기
    
    async def run_once(self):
        """1회 실행 (테스트/스케줄러용)"""
        matches = await self.matcher.batch_process_attacks()
        return matches


async def main():
    """메인 실행"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
        logger.error("Missing required environment variables")
        return
    
    orchestrator = DefenseOrchestrator()
    
    # 실행 모드 선택
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # 1회 실행
        matches = await orchestrator.run_once()
        logger.info(f"Completed. Processed {len(matches)} matches.")
    else:
        # 지속 실행
        await orchestrator.run_continuous_matching()


if __name__ == "__main__":
    asyncio.run(main())
