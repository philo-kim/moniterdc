"""
기존 contents의 누락된 메타데이터 업데이트

published_at이 NULL이거나 metadata에 조회수/댓글수가 없는 글들을
다시 크롤링해서 메타데이터를 업데이트합니다.
"""

import asyncio
from engines.utils.supabase_client import get_supabase
from engines.adapters.dc_gallery_adapter import DCGalleryAdapter
from dateutil import parser as date_parser

async def update_metadata():
    supabase = get_supabase()
    adapter = DCGalleryAdapter()

    print("=" * 80)
    print("기존 contents 메타데이터 업데이트")
    print("=" * 80)
    print()

    # published_at이 NULL인 글 찾기
    print("🔍 published_at이 NULL인 글 조회 중...")

    all_contents = []
    page_size = 1000
    offset = 0

    while True:
        result = supabase.table('contents')\
            .select('id, source_url, metadata')\
            .is_('published_at', 'null')\
            .range(offset, offset + page_size - 1)\
            .execute()

        if not result.data:
            break

        all_contents.extend(result.data)

        if len(result.data) < page_size:
            break

        offset += page_size

    total = len(all_contents)
    print(f"총 {total:,}개 글의 메타데이터 업데이트 필요")
    print()

    if total == 0:
        print("✅ 모든 글이 이미 메타데이터를 가지고 있습니다.")
        return

    updated = 0
    failed = 0

    for i, content in enumerate(all_contents, 1):
        try:
            url = content['source_url']
            content_id = content['id']

            # 진행 상황 출력
            if i % 100 == 0 or i == 1:
                print(f"[{i:,}/{total:,}] 처리 중... (성공: {updated}, 실패: {failed})")

            # 메타데이터 크롤링
            post_data = await adapter.fetch_post_content(url)

            if not post_data.get('body'):
                failed += 1
                continue

            # published_at 파싱
            published_at = None
            if post_data.get('published_at'):
                try:
                    dt = date_parser.parse(post_data['published_at'])
                    published_at = dt.isoformat()
                except:
                    pass

            # metadata 업데이트
            metadata = content.get('metadata', {}) or {}
            metadata.update({
                'author': post_data.get('author'),
                'view_count': post_data.get('view_count'),
                'comment_count': post_data.get('comment_count'),
                'recommend_count': post_data.get('recommend_count')
            })

            # DB 업데이트
            update_data = {
                'metadata': metadata
            }

            if published_at:
                update_data['published_at'] = published_at

            supabase.table('contents')\
                .update(update_data)\
                .eq('id', content_id)\
                .execute()

            updated += 1

            # Rate limiting (초당 10개)
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"\n❌ 오류 ({url}): {e}")
            failed += 1
            continue

    print()
    print("=" * 80)
    print("완료")
    print("=" * 80)
    print(f"성공: {updated:,}개")
    print(f"실패: {failed:,}개")
    print("=" * 80)

if __name__ == '__main__':
    asyncio.run(update_metadata())
