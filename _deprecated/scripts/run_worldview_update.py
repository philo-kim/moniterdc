"""
WorldviewUpdater 실행 테스트
"""

import asyncio
import sys
sys.path.insert(0, '/Users/taehyeonkim/dev/minjoo/moniterdc')

from engines.analyzers.worldview_updater import WorldviewUpdater

async def main():
    print("="*70)
    print("세계관 업데이트 시스템 테스트")
    print("="*70)

    updater = WorldviewUpdater()

    # 1. 일상 업데이트
    print("\n\n【1. 일상 업데이트】")
    daily_stats = await updater.daily_update()
    print(f"\n결과: {daily_stats}")

    # 2. 임계값 확인
    print("\n\n【2. 임계값 확인】")
    rebuild_stats = await updater.check_and_rebuild_if_needed()
    print(f"\n결과: {rebuild_stats}")

    # 3. 새 세계관 발견
    print("\n\n【3. 새 세계관 발견】")
    new_wv_stats = await updater.detect_and_create_new_worldviews()
    print(f"\n결과: {new_wv_stats}")

    # 4. 주간 업데이트 (optional - 주석 처리)
    # print("\n\n【4. 주간 업데이트】")
    # weekly_stats = await updater.weekly_update()
    # print(f"\n결과: {weekly_stats}")

    print("\n\n" + "="*70)
    print("전체 업데이트 완료")
    print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
