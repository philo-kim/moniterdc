#!/usr/bin/env python3
"""
Claude를 사용한 보안 정리 작업 검증 스크립트

목표:
- 지금까지 진행한 보안 정리 작업들을 Claude로 재검증
- 놓친 보안 이슈 확인
- Claude의 분석력과 GPT 비교
"""

import os
import asyncio
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Claude client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_anthropic_api_key_here":
    print("❌ ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    print("   https://console.anthropic.com/에서 API 키를 발급받아 .env 파일에 추가하세요.")
    exit(1)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent

# 검증할 작업 항목들
VERIFICATION_TASKS = [
    {
        "id": 1,
        "name": "하드코딩된 키 제거 검증",
        "description": "4개 파일에서 API 키가 완전히 제거되었는지 확인",
        "files": [
            "_archive/validation_scripts/experimental_worldview_research.py",
            "_archive/validation_scripts/comprehensive_frame_simulation.py",
            "_archive/validation_scripts/real_data_worldview_experiments.py",
            "check_worldview_data.py"
        ]
    },
    {
        "id": 2,
        "name": ".gitignore 점검",
        "description": ".gitignore가 민감한 파일들을 충분히 차단하는지 검증",
        "files": [".gitignore"]
    },
    {
        "id": 3,
        "name": "환경변수 사용 패턴 검증",
        "description": "수정된 파일들이 올바른 환경변수 사용 패턴을 따르는지 확인",
        "files": [
            "_archive/validation_scripts/experimental_worldview_research.py",
            "check_worldview_data.py"
        ]
    },
    {
        "id": 4,
        "name": "추가 보안 위험 탐지",
        "description": "GPT가 놓쳤을 수 있는 다른 보안 이슈 발견",
        "files": [".", ".github/workflows/"]  # 전체 스캔
    }
]


async def read_file_safe(file_path: Path) -> str:
    """파일을 안전하게 읽기 (존재하지 않으면 빈 문자열)"""
    try:
        if file_path.is_file():
            return file_path.read_text(encoding='utf-8')
        return f"[파일이 존재하지 않음: {file_path}]"
    except Exception as e:
        return f"[파일 읽기 오류: {e}]"


async def verify_with_claude(task: dict) -> dict:
    """Claude를 사용해 특정 작업 검증"""

    print(f"\n{'='*80}")
    print(f"Task {task['id']}: {task['name']}")
    print(f"{'='*80}")

    # 파일 내용 수집
    file_contents = {}
    for file_path in task['files']:
        full_path = PROJECT_ROOT / file_path

        if full_path.is_dir():
            # 디렉토리인 경우 yml 파일들 스캔
            file_contents[file_path] = "Directory listing:\n"
            for yml_file in full_path.rglob("*.yml"):
                content = await read_file_safe(yml_file)
                file_contents[str(yml_file.relative_to(PROJECT_ROOT))] = content
        else:
            content = await read_file_safe(full_path)
            file_contents[file_path] = content

    # Claude에게 검증 요청
    prompt = f"""당신은 보안 전문가입니다. 다음 작업에 대한 검증을 수행해주세요:

## 작업 정보
- **작업명**: {task['name']}
- **설명**: {task['description']}

## 검토할 파일들
"""

    for file_path, content in file_contents.items():
        prompt += f"\n### {file_path}\n```\n{content[:3000]}{'...' if len(content) > 3000 else ''}\n```\n"

    prompt += """

## 검증 요청사항
1. 위 파일들의 보안 상태를 철저히 분석해주세요
2. 발견된 문제점을 구체적으로 나열해주세요
3. 추가 권장사항이 있다면 제시해주세요
4. 전반적인 평가 (안전함/주의필요/위험함)를 제공해주세요

JSON 형식으로 응답해주세요:
{
    "status": "SAFE" | "WARNING" | "CRITICAL",
    "issues_found": ["issue1", "issue2", ...],
    "recommendations": ["rec1", "rec2", ...],
    "summary": "전반적인 평가 요약"
}
"""

    print(f"📤 Claude에게 검증 요청 중...")

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Claude Sonnet 4.5
            max_tokens=4096,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        print(f"📥 Claude 응답 받음")

        # JSON 파싱 시도
        try:
            # JSON 블록 추출
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]
            else:
                json_str = response_text

            result = json.loads(json_str)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 텍스트 그대로 반환
            result = {
                "status": "WARNING",
                "issues_found": [],
                "recommendations": [],
                "summary": response_text
            }

        # 결과 출력
        print(f"\n상태: {result.get('status', 'UNKNOWN')}")

        if result.get('issues_found'):
            print(f"\n🔴 발견된 문제점:")
            for issue in result['issues_found']:
                print(f"  - {issue}")

        if result.get('recommendations'):
            print(f"\n💡 권장사항:")
            for rec in result['recommendations']:
                print(f"  - {rec}")

        print(f"\n📝 요약:")
        print(f"  {result.get('summary', 'N/A')}")

        return {
            "task": task,
            "result": result,
            "raw_response": response_text
        }

    except Exception as e:
        print(f"❌ Claude 검증 중 오류: {e}")
        return {
            "task": task,
            "result": {
                "status": "ERROR",
                "issues_found": [str(e)],
                "recommendations": [],
                "summary": f"검증 중 오류 발생: {e}"
            },
            "raw_response": ""
        }


async def main():
    """메인 실행 함수"""

    print("=" * 80)
    print("Claude 보안 검증 시스템")
    print("=" * 80)
    print(f"프로젝트: {PROJECT_ROOT}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"검증 작업 수: {len(VERIFICATION_TASKS)}")

    # 모든 작업 검증
    results = []
    for task in VERIFICATION_TASKS:
        result = await verify_with_claude(task)
        results.append(result)
        await asyncio.sleep(1)  # API rate limit 고려

    # 최종 보고서 생성
    print("\n" + "=" * 80)
    print("최종 검증 결과")
    print("=" * 80)

    critical_count = sum(1 for r in results if r['result']['status'] == 'CRITICAL')
    warning_count = sum(1 for r in results if r['result']['status'] == 'WARNING')
    safe_count = sum(1 for r in results if r['result']['status'] == 'SAFE')

    print(f"\n📊 통계:")
    print(f"  - 위험 (CRITICAL): {critical_count}")
    print(f"  - 주의 (WARNING): {warning_count}")
    print(f"  - 안전 (SAFE): {safe_count}")

    # 결과 저장
    output_file = PROJECT_ROOT / f"_claude_security_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과 저장: {output_file}")

    # 전체 평가
    if critical_count > 0:
        print("\n🔴 결론: 즉시 조치가 필요한 보안 문제가 발견되었습니다!")
    elif warning_count > 0:
        print("\n🟡 결론: 일부 개선이 권장됩니다.")
    else:
        print("\n🟢 결론: 보안 정리 작업이 잘 수행되었습니다!")


if __name__ == "__main__":
    asyncio.run(main())
