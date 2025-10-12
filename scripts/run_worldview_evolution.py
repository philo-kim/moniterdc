"""
세계관 진화 사이클 실행 스크립트

주기적으로 실행 (예: 매주 일요일):
1. 최근 perception 분석
2. 새 세계관 추출
3. 변화 감지
4. 자동 또는 수동 승인 후 적용
"""

import asyncio
import json
from datetime import datetime
from engines.analyzers.worldview_evolution_engine import WorldviewEvolutionEngine


async def main():
    print("="*80)
    print("세계관 진화 사이클")
    print(f"실행 시각: {datetime.now().isoformat()}")
    print("="*80)

    engine = WorldviewEvolutionEngine()

    # Run evolution cycle
    report = await engine.run_evolution_cycle(sample_size=200)

    # Save report
    report_filename = f"_evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 리포트 저장: {report_filename}")

    # Print summary
    print("\n" + "="*80)
    print("실행 결과")
    print("="*80)
    print(f"\n변화 감지: {'예' if report['changes_detected'] else '아니오'}")
    print(f"요약: {report['summary']}")
    print(f"\n신규 세계관: {report['new_count']}개")
    print(f"소멸 세계관: {report['disappeared_count']}개")
    print(f"진화 세계관: {report['evolved_count']}개")
    print(f"유지 세계관: {report['stable_count']}개")

    if report['changes_detected']:
        print("\n⚠️  유의미한 변화가 감지되었습니다.")
        print("   리포트를 검토하고 필요시 추가 조치를 취하세요.")
    else:
        print("\n✅ 세계관이 안정적으로 유지되고 있습니다.")


if __name__ == "__main__":
    asyncio.run(main())
