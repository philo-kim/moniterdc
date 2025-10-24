"""
자동 수집 스크립트 (GitHub Actions용)

10분마다 실행되며:
1. DB에서 가장 큰 글 번호 확인
2. 그보다 큰 번호의 새 글만 수집 (메타데이터 포함)

Note: 3개월 lifecycle은 daily_maintenance.py에서 처리됨
"""

import asyncio
import re
from datetime import datetime, timedelta, timezone
from engines.adapters.dc_gallery_adapter import DCGalleryAdapter
from engines.utils.supabase_client import get_supabase
from dateutil import parser as date_parser


async def main():
    print("=" * 80)
    print(f"Auto Collection - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    adapter = DCGalleryAdapter()
    supabase = get_supabase()

    # Step 1: DB에서 가장 큰 글 번호 찾기
    print("🔍 DB에서 최대 글 번호 확인 중...")

    all_contents = supabase.table('contents').select('source_url').execute()

    max_no = 0
    for content in all_contents.data:
        match = re.search(r'no=(\d+)', content['source_url'])
        if match:
            no = int(match.group(1))
            if no > max_no:
                max_no = no

    print(f"현재 최대 글 번호: no={max_no:,}")
    print()

    # Step 2: DC에서 최신 100개 글 가져와서 max_no보다 큰 것만 수집
    print("📥 새 글 확인 중...")

    raw_posts = await adapter.fetch(
        gallery='uspolitics',
        limit=100,
        concept_only=True,
        is_mgallery=True
    )

    # max_no보다 큰 글만 필터링
    new_posts = []
    for post in raw_posts:
        post_no = int(post['post_num'])
        if post_no > max_no:
            new_posts.append(post)

    print(f"새 글 발견: {len(new_posts)}개")

    if not new_posts:
        print("✅ 수집할 새 글 없음")
    else:
        # Step 3: 새 글 수집 및 메타데이터 포함 저장
        print()
        print("💾 새 글 저장 중...")

        saved_count = 0
        for post in new_posts:
            try:
                # 중복 체크
                existing = supabase.table('contents')\
                    .select('id')\
                    .eq('source_url', post['url'])\
                    .execute()

                if existing.data:
                    continue

                # 전체 content + metadata 가져오기
                post_data = await adapter.fetch_post_content(post['url'])

                if not post_data.get('body'):
                    continue

                # published_at 파싱
                published_at = None
                if post_data.get('published_at'):
                    try:
                        dt = date_parser.parse(post_data['published_at'])
                        published_at = dt.isoformat()
                    except:
                        pass

                # metadata 구성
                metadata = {
                    'gallery': 'uspolitics',
                    'post_num': post['post_num'],
                    'author': post_data.get('author'),
                    'view_count': post_data.get('view_count'),
                    'comment_count': post_data.get('comment_count'),
                    'recommend_count': post_data.get('recommend_count')
                }

                # DB 저장
                data = {
                    'source_type': 'dc_gallery',
                    'source_url': post['url'],
                    'source_id': post['post_num'],
                    'title': post['title'],
                    'body': post_data['body'],
                    'metadata': metadata,
                    'base_credibility': 0.2,
                    'published_at': published_at,
                    'collected_at': datetime.now(timezone.utc).isoformat(),
                    'is_active': True
                }

                supabase.table('contents').insert(data).execute()
                saved_count += 1

                print(f"  저장: no={post['post_num']} - {post['title'][:30]}")

            except Exception as e:
                print(f"  오류 (no={post['post_num']}): {e}")
                continue

        print()
        print(f"✅ 새 글 {saved_count}개 저장 완료")

    print()

    # Step 2: 통계 출력
    print("=" * 80)
    print("현재 통계")
    print("=" * 80)

    total_contents = supabase.table('contents').select('id', count='exact').execute()
    total_perceptions = supabase.table('layered_perceptions').select('id', count='exact').execute()

    print(f"총 Contents: {total_contents.count:,}개")
    print(f"총 Perceptions: {total_perceptions.count:,}개")

    if new_posts:
        print(f"새로 수집: {saved_count}개")

    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
