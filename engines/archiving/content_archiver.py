"""
ContentArchiver - 3개월 데이터 보관 시스템

90일 이상 contents를 자동으로 아카이브하여 DB 크기 관리 및 비용 절감
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from engines.utils.supabase_client import get_supabase


class ContentArchiver:
    """
    3개월 아카이빙 시스템

    - Active: 최근 90일 (세계관 분석 대상)
    - Archived: 90일 이상 (보관만, 분석 제외)
    """

    def __init__(self, days_threshold: int = 90):
        """
        Args:
            days_threshold: 아카이브 기준 일수 (기본 90일)
        """
        self.supabase = get_supabase()
        self.days_threshold = days_threshold

    def archive_old_contents(self, dry_run: bool = False) -> Dict:
        """
        90일 이상 된 contents를 아카이브

        Args:
            dry_run: True면 실제 아카이브 안 하고 미리보기만

        Returns:
            {
                'contents_archived': int,
                'perceptions_archived': int,
                'dry_run': bool,
                'threshold_date': str
            }
        """
        threshold_date = datetime.now() - timedelta(days=self.days_threshold)

        if dry_run:
            # Dry run: 아카이브 대상만 조회
            contents = self.supabase.table('contents').select('id, title, published_at').eq('archived', False).lt('published_at', threshold_date.isoformat()).execute().data

            return {
                'contents_archived': len(contents),
                'perceptions_archived': 0,  # Would need to count
                'dry_run': True,
                'threshold_date': threshold_date.isoformat(),
                'preview': contents[:10]  # First 10 for preview
            }

        # 실제 아카이브: RPC 함수 사용
        result = self.supabase.rpc('archive_old_contents', {
            'days_threshold': self.days_threshold
        }).execute()

        if result.data and len(result.data) > 0:
            row = result.data[0]
            return {
                'contents_archived': row['archived_count'],
                'perceptions_archived': row['perception_count'],
                'dry_run': False,
                'threshold_date': threshold_date.isoformat()
            }
        else:
            return {
                'contents_archived': 0,
                'perceptions_archived': 0,
                'dry_run': False,
                'threshold_date': threshold_date.isoformat()
            }

    def restore_content(self, content_id: str) -> bool:
        """
        아카이브된 content를 복구

        Args:
            content_id: 복구할 content ID

        Returns:
            복구 성공 여부
        """
        result = self.supabase.rpc('restore_content', {
            'content_id_param': content_id
        }).execute()

        return result.data if result.data else False

    def restore_period(self, start_date: str, end_date: str) -> int:
        """
        특정 기간의 아카이브된 contents를 복구

        Args:
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)

        Returns:
            복구된 contents 수
        """
        # 해당 기간의 archived contents 조회
        contents = self.supabase.table('contents').select('id').eq('archived', True).gte('published_at', start_date).lte('published_at', end_date).execute().data

        restored_count = 0
        for content in contents:
            if self.restore_content(content['id']):
                restored_count += 1

        return restored_count

    def get_archive_stats(self) -> Dict:
        """
        아카이브 통계 조회

        Returns:
            {
                'active_contents': int,
                'archived_contents': int,
                'active_0_30_days': int,
                'active_30_60_days': int,
                'active_60_90_days': int,
                'total_perceptions': int,
                'active_perceptions': int,
                'archived_perceptions': int
            }
        """
        result = self.supabase.rpc('get_archive_stats').execute()

        if result.data and len(result.data) > 0:
            row = result.data[0]
            return {
                'active_contents': row['active_contents_count'],
                'archived_contents': row['archived_contents_count'],
                'active_0_30_days': row['active_0_30_days'],
                'active_30_60_days': row['active_30_60_days'],
                'active_60_90_days': row['active_60_90_days'],
                'total_perceptions': row['total_perceptions'],
                'active_perceptions': row['active_perceptions'],
                'archived_perceptions': row['archived_perceptions']
            }
        else:
            return {}

    def get_active_contents(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Active contents 조회 (archived = false)

        Args:
            limit: 최대 개수

        Returns:
            Contents 리스트
        """
        query = self.supabase.table('contents').select('*').eq('archived', False).order('published_at', desc=True)

        if limit:
            query = query.limit(limit)

        result = query.execute()
        return result.data if result.data else []

    def get_archived_contents(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Archived contents 조회

        Args:
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            limit: 최대 개수

        Returns:
            Archived contents 리스트
        """
        query = self.supabase.table('contents').select('*').eq('archived', True).order('archived_at', desc=True)

        if start_date:
            query = query.gte('published_at', start_date)
        if end_date:
            query = query.lte('published_at', end_date)
        if limit:
            query = query.limit(limit)

        result = query.execute()
        return result.data if result.data else []

    def hard_delete_old_archives(self, days_threshold: int = 365) -> int:
        """
        오래된 아카이브를 완전 삭제 (주의!)

        Args:
            days_threshold: 아카이브된 지 며칠 이상 된 것을 삭제할지

        Returns:
            삭제된 contents 수
        """
        threshold_date = datetime.now() - timedelta(days=days_threshold)

        # 먼저 삭제 대상 조회
        contents = self.supabase.table('contents').select('id').eq('archived', True).lt('archived_at', threshold_date.isoformat()).execute().data

        if not contents:
            return 0

        content_ids = [c['id'] for c in contents]

        # Layered perceptions 먼저 삭제 (foreign key)
        self.supabase.table('layered_perceptions').delete().in_('content_id', content_ids).execute()

        # Contents 삭제
        self.supabase.table('contents').delete().in_('id', content_ids).execute()

        return len(content_ids)
