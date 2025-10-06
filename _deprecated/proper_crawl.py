"""
제대로 된 크롤링: 본문 포함 50-100개 수집
"""
import asyncio
from engines.collectors.content_collector import ContentCollector

async def main():
    collector = ContentCollector()

    print('=' * 80)
    print('DC 입갤 본문 포함 크롤링')
    print('=' * 80)

    # 여러 갤러리에서 수집 (다양성 확보)
    galleries = [
        ('uspolitics', True, 50),   # 미국정치 갤러리 (기존 사용)
    ]

    total_collected = 0

    for gallery, is_mgallery, limit in galleries:
        print(f'\n[{gallery}] 크롤링 시작... (목표: {limit}개)')

        try:
            content_ids = await collector.collect(
                'dc_gallery',
                gallery=gallery,
                limit=limit,
                concept_only=True,
                is_mgallery=is_mgallery
            )

            print(f'✅ {len(content_ids)}개 수집 완료')
            total_collected += len(content_ids)

        except Exception as e:
            print(f'❌ 오류: {e}')
            import traceback
            traceback.print_exc()

    print(f'\n{"=" * 80}')
    print(f'총 {total_collected}개 글 수집 완료')
    print(f'{"=" * 80}')

if __name__ == '__main__':
    asyncio.run(main())
