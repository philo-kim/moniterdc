#!/usr/bin/env python3
"""
Background Matcher v3.0 - 공격 vs 방어 자동 매칭
지속적으로 새로운 공격을 감지하고 최적 방어를 매칭
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.logic_matcher_fixed import LogicDefenseMatcher, DefenseOrchestrator
from supabase import create_client

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


class BackgroundMatcher:
    """백그라운드 매칭 서비스"""
    
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.matcher = LogicDefenseMatcher()
        self.orchestrator = DefenseOrchestrator()
        self.is_running = False
        
    async def check_system_health(self) -> Dict:
        """시스템 상태 확인"""
        try:
            # 1. DB 연결 확인
            test = self.supabase.table('logic_repository').select('id').limit(1).execute()
            db_ok = bool(test.data is not None)
            
            # 2. 통계 조회
            stats = self.supabase.rpc('check_embedding_status').execute()
            
            if stats.data:
                total_logics = sum(s['total_count'] for s in stats.data)
                with_embedding = sum(s['with_embedding'] for s in stats.data)
                embedding_rate = with_embedding / total_logics if total_logics > 0 else 0
            else:
                total_logics = 0
                embedding_rate = 0
            
            # 3. 미매칭 공격 수
            unmatched = await self.matcher.get_unmatched_attacks(limit=100)
            unmatched_count = len(unmatched)
            
            # 4. 최근 매칭 수
            recent_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            recent_matches = self.supabase.table('logic_matches').select('id').gte(
                'created_at', recent_time
            ).execute()
            recent_match_count = len(recent_matches.data) if recent_matches.data else 0
            
            health = {
                'status': 'healthy' if db_ok else 'unhealthy',
                'db_connection': db_ok,
                'total_logics': total_logics,
                'embedding_rate': embedding_rate,
                'unmatched_attacks': unmatched_count,
                'recent_matches_1h': recent_match_count,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"System Health: {health}")
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def process_new_attacks(self) -> List[Dict]:
        """새로운 공격 처리"""
        
        # 1. 최근 1시간 내 새로운 공격 찾기
        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        
        new_attacks = self.supabase.table('logic_repository').select('*').eq(
            'logic_type', 'attack'
        ).eq(
            'is_active', True
        ).gte(
            'created_at', one_hour_ago
        ).is_(
            'vector_embedding', 'not.null'
        ).order(
            'threat_level', desc=True
        ).execute()
        
        if not new_attacks.data:
            logger.info("No new attacks in the last hour")
            return []
        
        logger.info(f"Found {len(new_attacks.data)} new attacks to process")
        
        # 2. 각 공격에 대해 매칭 확인 및 처리
        processed = []
        for attack in new_attacks.data:
            # 이미 매칭되었는지 확인
            existing = self.supabase.table('logic_matches').select('id').eq(
                'attack_id', attack['id']
            ).execute()
            
            if existing.data:
                logger.info(f"Attack {attack['id'][:8]} already matched")
                continue
            
            # 매칭 처리
            matches = await self.matcher.process_single_attack(attack)
            processed.extend(matches)
            
            await asyncio.sleep(1)  # Rate limiting
        
        return processed
    
    async def instant_matching_loop(self):
        """즉시 매칭 루프 (긴급 공격 우선)"""
        
        logger.info("Starting instant matching for high-threat attacks...")
        
        # 위협도 8 이상 미매칭 공격
        critical_attacks = self.supabase.table('logic_repository').select('*').eq(
            'logic_type', 'attack'
        ).eq(
            'is_active', True
        ).gte(
            'threat_level', 8
        ).not_.is_(
            'vector_embedding', 'null'
        ).execute()
        
        if not critical_attacks.data:
            logger.info("No critical attacks found")
            return
        
        # 매칭 여부 확인 후 처리
        for attack in critical_attacks.data:
            existing = self.supabase.table('logic_matches').select('id').eq(
                'attack_id', attack['id']
            ).execute()
            
            if not existing.data:  # 미매칭
                logger.warning(f"CRITICAL: Processing high-threat attack - {attack['core_argument'][:50]}")
                await self.matcher.process_single_attack(attack)
                await asyncio.sleep(0.5)
    
    async def run_continuous(self):
        """지속적 실행"""
        
        self.is_running = True
        logger.info("Starting Background Matcher v3.0...")
        
        # 초기 헬스체크
        health = await self.check_system_health()
        if health['status'] != 'healthy':
            logger.error("System unhealthy, exiting")
            return
        
        cycle = 0
        while self.is_running:
            try:
                cycle += 1
                logger.info(f"=== Matching Cycle {cycle} ===")
                
                # 1. 긴급 공격 우선 처리
                await self.instant_matching_loop()
                
                # 2. 새로운 공격 처리
                new_matches = await self.process_new_attacks()
                
                # 3. 일반 미매칭 공격 처리
                if cycle % 6 == 0:  # 30분마다
                    logger.info("Running batch matching for all unmatched attacks...")
                    batch_matches = await self.matcher.batch_process_attacks()
                    new_matches.extend(batch_matches)
                
                # 4. 결과 요약
                if new_matches:
                    logger.info(f"Cycle {cycle}: Created {len(new_matches)} new matches")
                    await self._log_matches(new_matches)
                else:
                    logger.info(f"Cycle {cycle}: No new matches")
                
                # 5. 헬스체크 (10사이클마다)
                if cycle % 10 == 0:
                    await self.check_system_health()
                
                # 대기 (5분)
                logger.info("Waiting 5 minutes until next cycle...")
                await asyncio.sleep(300)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                self.is_running = False
                break
                
            except Exception as e:
                logger.error(f"Error in cycle {cycle}: {str(e)}")
                await asyncio.sleep(60)  # 에러시 1분 대기
        
        logger.info("Background Matcher stopped")
    
    async def _log_matches(self, matches: List[Dict]):
        """매칭 결과 로깅"""
        for match in matches:
            attack = match.get('attack', {})
            defense = match.get('defense', {})
            match_info = match.get('match', {})
            
            logger.info(
                f"Match: [{match_info.get('match_confidence', 0):.0%}] "
                f"{attack.get('core_argument', '')[:30]}... → "
                f"{defense.get('core_argument', '')[:30]}..."
            )
    
    async def run_once(self):
        """1회 실행 (테스트용)"""
        
        logger.info("Running once...")
        
        # 헬스체크
        health = await self.check_system_health()
        logger.info(f"Health: {health}")
        
        # 긴급 매칭
        await self.instant_matching_loop()
        
        # 배치 매칭
        matches = await self.matcher.batch_process_attacks()
        
        if matches:
            logger.info(f"Created {len(matches)} matches")
            await self._log_matches(matches)
        else:
            logger.info("No matches created")
        
        return matches


async def main():
    """메인 실행"""
    
    # 환경변수 확인
    if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
        logger.error("Missing required environment variables")
        return
    
    matcher = BackgroundMatcher()
    
    # 실행 모드
    import sys
    if '--once' in sys.argv:
        # 1회 실행
        matches = await matcher.run_once()
        logger.info(f"Complete. Processed {len(matches) if matches else 0} matches")
    elif '--health' in sys.argv:
        # 헬스체크만
        health = await matcher.check_system_health()
        print(f"System Health: {health}")
    else:
        # 지속 실행
        await matcher.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
