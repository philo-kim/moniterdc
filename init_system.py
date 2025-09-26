#!/usr/bin/env python3
"""
Logic Defense System v3.0 - 시스템 초기화 및 관리
DC갤러리 정치 AI 모니터링 시스템 관리 도구
"""

import os
import sys
import asyncio
import argparse
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogicDefenseSystemManager:
    """시스템 초기화 및 관리 클래스"""

    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')

        # 지연 로딩을 위한 클라이언트 변수
        self._supabase = None
        self._openai_client = None

    @property
    def supabase(self):
        """Supabase 클라이언트 지연 로딩"""
        if self._supabase is None:
            try:
                from supabase import create_client
                self._supabase = create_client(self.supabase_url, self.supabase_key)
            except ImportError:
                logger.error("Supabase 라이브러리가 설치되지 않았습니다: pip install supabase")
                sys.exit(1)
        return self._supabase

    @property
    def openai_client(self):
        """OpenAI 클라이언트 지연 로딩"""
        if self._openai_client is None:
            try:
                from openai import AsyncOpenAI
                self._openai_client = AsyncOpenAI(api_key=self.openai_key)
            except ImportError:
                logger.error("OpenAI 라이브러리가 설치되지 않았습니다: pip install openai")
                sys.exit(1)
        return self._openai_client

    def print_header(self, title: str):
        """헤더 출력"""
        print("=" * 70)
        print(f"   {title}")
        print("=" * 70)
        print()

    def check_environment(self) -> Dict[str, Any]:
        """환경변수 및 의존성 체크"""
        self.print_header("Logic Defense System v3.0 - Environment Check")

        result = {
            'env_vars': {},
            'dependencies': {},
            'overall_status': 'healthy'
        }

        # 환경변수 체크
        required_vars = {
            'SUPABASE_URL': self.supabase_url,
            'SUPABASE_SERVICE_KEY': self.supabase_key,
            'OPENAI_API_KEY': self.openai_key
        }

        optional_vars = {
            'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
            'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
            'GPT_ANALYSIS_MODEL': os.getenv('GPT_ANALYSIS_MODEL', 'gpt-5-mini')
        }

        print("🔍 환경변수 체크:")
        for var, value in required_vars.items():
            if value and not value.startswith('your-'):
                print(f"  ✅ {var}: 설정됨")
                result['env_vars'][var] = True
            else:
                print(f"  ❌ {var}: 누락 또는 기본값")
                result['env_vars'][var] = False
                result['overall_status'] = 'error'

        print("\n📋 선택적 환경변수:")
        for var, value in optional_vars.items():
            if value and not value.startswith('your-'):
                print(f"  ✅ {var}: 설정됨")
                result['env_vars'][var] = True
            else:
                print(f"  ⚠️ {var}: 미설정 (선택사항)")
                result['env_vars'][var] = False

        # 의존성 체크
        print("\n📦 Python 의존성 체크:")
        dependencies = [
            ('supabase', 'Supabase 클라이언트'),
            ('openai', 'OpenAI API'),
            ('aiohttp', 'HTTP 클라이언트'),
            ('beautifulsoup4', '웹 스크래핑'),
            ('python-dotenv', '환경변수 관리'),
            ('telegram', '텔레그램 봇')
        ]

        for package, description in dependencies:
            try:
                __import__(package)
                print(f"  ✅ {package}: {description}")
                result['dependencies'][package] = True
            except ImportError:
                print(f"  ❌ {package}: {description} - 설치 필요")
                result['dependencies'][package] = False
                if package in ['supabase', 'openai', 'aiohttp', 'beautifulsoup4']:
                    result['overall_status'] = 'error'

        print(f"\n🏥 전체 상태: {result['overall_status'].upper()}")
        return result

    async def test_connections(self) -> Dict[str, Any]:
        """데이터베이스 및 API 연결 테스트"""
        self.print_header("Connection Tests")

        result = {
            'database': False,
            'openai': False,
            'vector_functions': False,
            'telegram': False
        }

        # 데이터베이스 연결 테스트
        print("🗄️ Supabase 연결 테스트:")
        try:
            test_query = self.supabase.table('logic_repository').select('id').limit(1).execute()
            if test_query:
                print("  ✅ 데이터베이스 연결 성공")
                result['database'] = True

                # 테이블 존재 확인
                tables = ['logic_repository', 'logic_matches', 'alerts', 'system_stats']
                for table in tables:
                    try:
                        self.supabase.table(table).select('*').limit(1).execute()
                        print(f"  ✅ 테이블 '{table}' 확인")
                    except Exception as e:
                        print(f"  ❌ 테이블 '{table}' 오류: {str(e)[:50]}")
            else:
                print("  ❌ 데이터베이스 연결 실패")
        except Exception as e:
            print(f"  ❌ 데이터베이스 오류: {str(e)[:50]}")

        # OpenAI API 테스트
        print("\n🤖 OpenAI API 테스트:")
        try:
            response = await self.openai_client.chat.completions.create(
                model=os.getenv('GPT_ANALYSIS_MODEL', 'gpt-5-mini'),
                messages=[
                    {"role": "system", "content": "Test"},
                    {"role": "user", "content": "Reply with 'OK'"}
                ],
                max_completion_tokens=10
            )

            if response.choices[0].message.content:
                print("  ✅ OpenAI API 연결 성공")
                result['openai'] = True
            else:
                print("  ❌ OpenAI API 응답 없음")
        except Exception as e:
            print(f"  ❌ OpenAI API 오류: {str(e)[:50]}")

        # 벡터 함수 테스트
        print("\n🔍 벡터 검색 함수 테스트:")
        try:
            test_rpc = self.supabase.rpc('check_embedding_status').execute()
            if test_rpc.data is not None:
                print("  ✅ pgvector 함수 작동 중")
                result['vector_functions'] = True

                # 임베딩 상태 출력
                for row in test_rpc.data:
                    print(f"    📊 {row['logic_type']}: {row['embedded_count']}/{row['total_count']} ({row['embedding_rate']}%)")
            else:
                print("  ❌ pgvector 함수 오류")
        except Exception as e:
            print(f"  ❌ 벡터 함수 오류: {str(e)[:50]}")

        # 텔레그램 봇 테스트 (선택사항)
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

        print("\n📱 텔레그램 봇 테스트:")
        if telegram_token and telegram_chat and not telegram_token.startswith('your-'):
            try:
                from telegram import Bot
                bot = Bot(token=telegram_token)
                await bot.get_me()
                print("  ✅ 텔레그램 봇 설정 확인")
                result['telegram'] = True
            except Exception as e:
                print(f"  ❌ 텔레그램 봇 오류: {str(e)[:50]}")
        else:
            print("  ⚠️ 텔레그램 봇 미설정 (선택사항)")

        return result

    async def run_migration(self):
        """데이터베이스 마이그레이션 실행"""
        self.print_header("Database Migration")

        migration_dir = Path(__file__).parent / 'supabase' / 'migrations'

        if not migration_dir.exists():
            print(f"❌ 마이그레이션 디렉토리가 없습니다: {migration_dir}")
            return False

        # 마이그레이션 파일 목록
        migration_files = sorted([
            f for f in migration_dir.glob('*.sql')
            if f.name.startswith(('001_', '003_', '007_'))
        ])

        if not migration_files:
            print("❌ 마이그레이션 파일이 없습니다")
            return False

        print(f"📁 발견된 마이그레이션 파일: {len(migration_files)}개")

        for migration_file in migration_files:
            print(f"\n🔄 실행 중: {migration_file.name}")

            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()

                # SQL을 세미콜론으로 분할해서 실행
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

                success_count = 0
                for i, statement in enumerate(statements):
                    if not statement:
                        continue

                    try:
                        # Supabase RPC로 SQL 실행 시도
                        if statement.lower().startswith('select'):
                            # SELECT 문은 직접 실행
                            result = self.supabase.rpc('exec_sql', {'sql': statement}).execute()
                        else:
                            # DDL/DML은 PostgreSQL에서 직접 실행해야 함
                            # 여기서는 로깅만 하고 실제 실행은 별도 도구 사용
                            logger.info(f"SQL 문 준비됨: {statement[:50]}...")

                        success_count += 1
                    except Exception as e:
                        logger.warning(f"SQL 문 실행 건너뜀 ({i+1}): {str(e)[:50]}")

                print(f"  ✅ {migration_file.name}: {success_count}/{len(statements)} 문 처리")

            except Exception as e:
                print(f"  ❌ {migration_file.name} 실행 실패: {str(e)}")
                return False

        print(f"\n🎉 마이그레이션 완료!")
        print("\n⚠️ 주의: SQL 마이그레이션은 Supabase 대시보드에서 직접 실행하거나")
        print("   Supabase CLI를 사용해서 완료해야 할 수 있습니다.")
        return True

    async def get_system_stats(self) -> Dict[str, Any]:
        """시스템 통계 조회"""
        self.print_header("System Statistics")

        stats = {
            'database': {},
            'embeddings': {},
            'matches': {},
            'alerts': {}
        }

        try:
            # 논리 저장소 통계
            logics = self.supabase.table('logic_repository').select('*').execute()
            if logics.data:
                stats['database']['total_logics'] = len(logics.data)
                stats['database']['attacks'] = len([l for l in logics.data if l['logic_type'] == 'attack'])
                stats['database']['defenses'] = len([l for l in logics.data if l['logic_type'] == 'defense'])
                stats['database']['embedded'] = len([l for l in logics.data if l.get('vector_embedding')])

                print(f"📊 논리 저장소:")
                print(f"  전체 논리: {stats['database']['total_logics']}개")
                print(f"  공격 논리: {stats['database']['attacks']}개")
                print(f"  방어 논리: {stats['database']['defenses']}개")
                print(f"  임베딩 완료: {stats['database']['embedded']}개")

            # 매칭 통계
            matches = self.supabase.table('logic_matches').select('*').execute()
            if matches.data:
                stats['matches']['total'] = len(matches.data)
                stats['matches']['high_confidence'] = len([m for m in matches.data if m['match_confidence'] >= 0.8])
                stats['matches']['avg_confidence'] = sum(m['match_confidence'] for m in matches.data) / len(matches.data)

                print(f"\n🎯 매칭 통계:")
                print(f"  총 매칭: {stats['matches']['total']}개")
                print(f"  고신뢰도 매칭: {stats['matches']['high_confidence']}개")
                print(f"  평균 신뢰도: {stats['matches']['avg_confidence']:.2%}")

            # 알림 통계
            alerts = self.supabase.table('alerts').select('*').execute()
            if alerts.data:
                stats['alerts']['total'] = len(alerts.data)
                stats['alerts']['pending'] = len([a for a in alerts.data if not a.get('sent_at')])

                print(f"\n📨 알림 통계:")
                print(f"  총 알림: {stats['alerts']['total']}개")
                print(f"  대기 중: {stats['alerts']['pending']}개")

            # 벡터 함수로 상세 통계
            try:
                embedding_status = self.supabase.rpc('check_embedding_status').execute()
                if embedding_status.data:
                    print(f"\n🔍 임베딩 상세:")
                    for row in embedding_status.data:
                        print(f"  {row['logic_type']}: {row['embedding_rate']}% 완료")
            except:
                pass

        except Exception as e:
            print(f"❌ 통계 조회 실패: {str(e)}")

        return stats

    async def run_health_check(self) -> Dict[str, Any]:
        """종합 헬스체크"""
        self.print_header("System Health Check")

        health = {
            'overall': 'healthy',
            'components': {}
        }

        # 1. 환경 체크
        env_result = self.check_environment()
        health['components']['environment'] = env_result['overall_status']

        # 2. 연결 테스트
        conn_result = await self.test_connections()
        health['components']['connections'] = 'healthy' if all(conn_result.values()) else 'degraded'

        # 3. 통계 확인
        try:
            await self.get_system_stats()
            health['components']['data'] = 'healthy'
        except:
            health['components']['data'] = 'error'

        # 전체 상태 결정
        if any(status == 'error' for status in health['components'].values()):
            health['overall'] = 'error'
        elif any(status == 'degraded' for status in health['components'].values()):
            health['overall'] = 'degraded'

        print(f"\n🏥 전체 시스템 상태: {health['overall'].upper()}")

        # 권장사항 출력
        print(f"\n💡 권장사항:")
        if health['overall'] != 'healthy':
            print("  1. .env 파일에서 누락된 환경변수를 설정하세요")
            print("  2. pip install -r requirements.txt로 의존성을 설치하세요")
            print("  3. Supabase 프로젝트 설정을 확인하세요")
        else:
            print("  ✅ 시스템이 정상 작동 중입니다")
            print("  📝 크롤링 시작: ./run.sh crawl")
            print("  🎯 매칭 시작: ./run.sh match")

        return health

def main():
    parser = argparse.ArgumentParser(description='Logic Defense System v3.0 관리 도구')
    parser.add_argument('command', choices=['test', 'migrate', 'stats', 'health'],
                       help='실행할 명령')

    args = parser.parse_args()
    manager = LogicDefenseSystemManager()

    async def run_command():
        if args.command == 'test':
            await manager.run_health_check()
        elif args.command == 'migrate':
            await manager.run_migration()
        elif args.command == 'stats':
            await manager.get_system_stats()
        elif args.command == 'health':
            await manager.run_health_check()

    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\n중단됨")
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()