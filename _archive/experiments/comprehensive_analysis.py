"""
종합 분석: 3-Layer 구조 검증 및 최적화 방안

목적:
1. 기존 layered_perception_extractor.py의 3-layer 구조 검증
2. 실제 데이터로 "특정한 세계관" 추출 테스트
3. 문제점 발견 및 개선 방안 제안
"""

import asyncio
import os
import json
from openai import AsyncOpenAI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception(f"Missing env vars: URL={SUPABASE_URL is not None}, KEY={SUPABASE_KEY is not None}")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def main():
    print("=" * 80)
    print("종합 분석: 3-Layer 구조와 세계관 특정성 검증")
    print("=" * 80)

    # Step 1: 현재 데이터베이스 상태 확인
    print("\n\n[Step 1] 데이터베이스 현황 분석")
    print("-" * 80)

    # Check tables
    contents = supabase.table('contents').select('id', count='exact').execute()
    perceptions = supabase.table('perceptions').select('id', count='exact').execute()
    worldviews = supabase.table('worldviews').select('id', count='exact').execute()

    print(f"Contents: {contents.count}개")
    print(f"Perceptions: {perceptions.count}개")
    print(f"Worldviews: {worldviews.count}개")

    # Check if layered_perceptions table exists
    try:
        layered = supabase.table('layered_perceptions').select('id', count='exact').execute()
        print(f"Layered Perceptions: {layered.count}개")
        has_layered_table = True
    except:
        print(f"Layered Perceptions: ❌ 테이블 없음")
        has_layered_table = False

    # Step 2: 테스트 케이스 준비 (유심교체 사례)
    print("\n\n[Step 2] 테스트 케이스 준비: '유심교체 사건' 글")
    print("-" * 80)

    test_content = {
        "title": '"민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"',
        "body": """나경원 "민주, 지귀연 핸드폰 교체 어떻게 알았나…독재시대 예고편"
박태훈 선임기자 = 나경원 국민의힘 의원은 더불어민주당이 개인정보까지 맘대로 들춰보고 있다며 "폭주를 멈출 것"을 요구했다. 나 의원은 1일 SNS를 통해 "추미애 법사위가 어제 일방적으로 추진한 조희대 대법원장 청
naver.me
개인 사찰을 했다고 민주당이 자백한 수준
유심교체를 어떻게 알아ㅋㅋㅋㅋ미친
지들 맘에 안드는 판사 사찰하려고 통신사 협박해서 얻어낸 정보
통신사들도 요새 해킹 문제 많고
이게 진짜 맞는거냐"""
    }

    print(f"제목: {test_content['title']}")
    print(f"본문: {test_content['body'][:150]}...")

    # Step 3: 기존 Prompt 테스트 (layered_perception_extractor.py)
    print("\n\n[Step 3] 기존 3-Layer Prompt 테스트")
    print("-" * 80)

    original_prompt = f"""
다음은 DC Gallery 정치 갤러리의 글입니다:

제목: {test_content['title']}
내용: {test_content['body']}

이 글을 **3개 층위**로 분석해주세요.

⚠️ 중요: 일반론이 아닌, **이 글쓴이가 실제로 믿는 구체적인 내용**을 추출하세요.

## 1. 표면층 (Explicit Layer) - 명시적 주장
**글에서 직접 말하고 있는 것**
- 누가/무엇을 비난하는가?
- 어떤 행동/사건을 문제 삼는가?
- 구체적인 인물/조직/사건 이름 포함

## 2. 암묵층 (Implicit Layer) - 전제하는 사고
**말하지 않았지만 당연하게 여기는 것**

❌ 나쁜 예: "비공개 정보를 안다 = 불법"
✅ 좋은 예: "민주당은 통신사를 협박해서 개인정보를 얻는다"

❌ 나쁜 예: "사찰은 나쁘다"
✅ 좋은 예: "이들은 맘에 안드는 판사까지 사찰한다 (사법부 장악 시도)"

**구체적으로:**
- 누가 어떤 방법으로 무엇을 한다고 믿는가?
- 그들의 의도/목적은 무엇이라고 생각하는가?
- 어떤 패턴/전략이 있다고 보는가?

## 3. 심층 (Deep Layer) - 무의식적 믿음
**이 글쓴이 진영만의 세계관**

❌ 나쁜 예: "권력은 부패한다" (누구나 하는 말)
✅ 좋은 예: "민주당/좌파는 과거 독재정권처럼 사찰과 탄압으로 권력을 유지하려 한다"

❌ 나쁜 예: "작은 문제가 커진다"
✅ 좋은 예: "지금의 작은 사찰이 과거 독재시대처럼 전면적 감시국가로 발전한다"

**구체적으로:**
- 이 진영이 **역사를 어떻게 보는가**? (과거 사례 → 현재 연결)
- **상대편의 본질**을 어떻게 규정하는가? (민주당/좌파/중국 = ?)
- **세상의 작동 원리**를 어떻게 이해하는가? (A가 일어나면 반드시 B가 일어난다)

JSON 형식:
{{
  "explicit_claims": [
    {{
      "subject": "민주당",
      "predicate": "유심교체 정보를 불법으로 얻었다",
      "evidence_cited": "나경원 의원 SNS - 어떻게 알았나",
      "quote": "유심교체를 어떻게 알아"
    }}
  ],
  "implicit_assumptions": [
    "민주당은 통신사를 협박해서 개인 사찰용 정보를 얻는다",
    "맘에 안드는 판사를 제거하기 위해 사찰한다 (사법부 장악 시도)"
  ],
  "reasoning_gaps": [
    {{
      "from": "유심교체 정보를 알았다",
      "to": "통신사 협박으로 얻었다",
      "gap": "정상적 방법 가능성은 배제하고 즉시 불법으로 단정"
    }}
  ],
  "deep_beliefs": [
    "민주당/좌파는 과거 독재정권처럼 사찰로 반대파를 제거한다",
    "지금의 작은 사찰이 곧 전면적 감시독재 사회로 발전한다 (역사 반복)",
    "이들은 사법부까지 장악해서 완전한 권력을 차지하려 한다"
  ],
  "worldview_hints": "과거 독재 → 현재 재현, 좌파 = 독재 본성, 사법부 장악 시도"
}}
"""

    print("GPT-5 호출 중...")
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are an expert in discourse analysis. Always respond in valid JSON format."},
            {"role": "user", "content": original_prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    print("\n✅ 추출 결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Step 4: 결과 평가
    print("\n\n[Step 4] 결과 평가: '특정한 세계관' 포착 여부")
    print("-" * 80)

    evaluation_prompt = f"""
다음은 "유심교체 사건" 글에 대한 3-layer 분석 결과입니다:

{json.dumps(result, ensure_ascii=False, indent=2)}

이 분석이 **"저들의 특정한 세계관"을 포착했는지** 평가해주세요.

평가 기준:
1. **특정성 (Specificity)**: 일반론이 아닌 이 진영 특유의 시각인가?
   - ❌ "권력은 부패한다" (누구나 하는 말)
   - ✅ "민주당은 통신사 협박으로 개인정보를 얻는다" (구체적)

2. **원문 보존**: 원문의 독특한 표현이 살아있는가?
   - ❌ "개인정보 불법 취득 의혹" (추상화)
   - ✅ "유심교체를 어떻게 알아ㅋㅋㅋㅋ미친" (원문 그대로)

3. **논리 구조**: 그들만의 추론 방식이 드러나는가?
   - "유심교체 정보 알았다" → "통신사 협박" → "사법부 장악" → "독재 재현"

4. **세계관 심도**: 단순 사실 나열이 아닌 세상 작동 원리에 대한 믿음인가?

각 항목을 10점 만점으로 평가하고, 개선 방안을 제시하세요.

JSON 형식:
{{
  "specificity_score": 0-10,
  "original_text_preservation": 0-10,
  "logic_structure_clarity": 0-10,
  "worldview_depth": 0-10,
  "total_score": 0-40,
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1", "약점2"],
  "improvement_suggestions": ["개선안1", "개선안2"]
}}
"""

    print("평가 중...")
    eval_response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are an expert evaluator. Always respond in valid JSON format."},
            {"role": "user", "content": evaluation_prompt}
        ],
        response_format={"type": "json_object"}
    )

    evaluation = json.loads(eval_response.choices[0].message.content)

    print("\n📊 평가 결과:")
    print(f"  특정성 (Specificity): {evaluation['specificity_score']}/10")
    print(f"  원문 보존: {evaluation['original_text_preservation']}/10")
    print(f"  논리 구조: {evaluation['logic_structure_clarity']}/10")
    print(f"  세계관 심도: {evaluation['worldview_depth']}/10")
    print(f"  총점: {evaluation['total_score']}/40")

    print("\n✅ 강점:")
    for s in evaluation['strengths']:
        print(f"  - {s}")

    print("\n❌ 약점:")
    for w in evaluation['weaknesses']:
        print(f"  - {w}")

    print("\n💡 개선 제안:")
    for i in evaluation['improvement_suggestions']:
        print(f"  - {i}")

    # Step 5: 다른 10개 글로 일관성 테스트
    print("\n\n[Step 5] 일관성 테스트: 다른 글들에서도 '특정성' 유지되는가?")
    print("-" * 80)

    # Get 10 random posts
    sample_contents = supabase.table('contents')\
        .select('id, title, body')\
        .neq('body', '')\
        .limit(10)\
        .execute().data

    print(f"10개 글 샘플링 완료")

    scores = []
    for i, content in enumerate(sample_contents, 1):
        print(f"\n[{i}/10] {content['title'][:50]}...")

        # Extract
        test_prompt = original_prompt.replace(test_content['title'], content['title'])\
            .replace(test_content['body'], content['body'][:2000])

        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert in discourse analysis. Always respond in valid JSON format."},
                {"role": "user", "content": test_prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Quick evaluation
        eval_response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert evaluator. Respond with just a number 0-40."},
                {"role": "user", "content": f"""
이 분석이 "특정한 세계관"을 포착했는지 0-40점 평가:
{json.dumps(result, ensure_ascii=False)}

특정성(0-10) + 원문보존(0-10) + 논리구조(0-10) + 세계관심도(0-10)

JSON: {{"score": 숫자}}
"""}
            ],
            response_format={"type": "json_object"}
        )

        score = json.loads(eval_response.choices[0].message.content)['score']
        scores.append(score)
        print(f"  점수: {score}/40")

    avg_score = sum(scores) / len(scores)
    print(f"\n평균 점수: {avg_score:.1f}/40")
    print(f"점수 범위: {min(scores)} ~ {max(scores)}")

    # Step 6: 최종 진단 및 제안
    print("\n\n[Step 6] 최종 진단 및 개선 방안")
    print("=" * 80)

    diagnosis_prompt = f"""
**현재 시스템 분석 결과:**

1. 데이터베이스 현황:
   - Contents: {contents.count}개
   - Perceptions: {perceptions.count}개
   - Worldviews: {worldviews.count}개
   - Layered Perceptions: {"있음" if has_layered_table else "없음"}

2. 3-Layer Prompt 성능:
   - 테스트 케이스 점수: {evaluation['total_score']}/40
   - 10개 샘플 평균: {avg_score:.1f}/40
   - 일관성: {"높음" if max(scores) - min(scores) < 15 else "낮음"}

3. 주요 약점:
{chr(10).join(f"   - {w}" for w in evaluation['weaknesses'])}

**질문:**

유저의 핵심 요구사항은:
"저들의 특정한 세계관을 이해하고 싶다.
'유심교체를 어떻게 알아'라는 질문 자체가 그들만의 시각이다."

현재 3-layer 시스템이 이 목적을 달성하고 있는가?

만약 부족하다면:
1. **구조 문제**인가? (Layer 구조 자체가 잘못됨)
2. **Prompt 문제**인가? (지시사항이 부족/불명확)
3. **모델 한계**인가? (GPT가 특정성을 포착 못함)
4. **데이터 문제**인가? (DC 글 자체가 특정성이 부족)

그리고 최선의 해결 방안은?

JSON 형식으로 종합 진단 및 제안:
{{
  "current_performance": "good/acceptable/poor",
  "root_cause": "structure/prompt/model/data",
  "detailed_diagnosis": "자세한 진단...",
  "recommended_approach": {{
    "keep": ["유지할 것들"],
    "fix": ["수정할 것들"],
    "add": ["추가할 것들"]
  }},
  "concrete_next_steps": [
    {{
      "step": "1단계 작업",
      "action": "구체적 액션",
      "expected_improvement": "기대 효과"
    }}
  ]
}}
"""

    print("종합 진단 중...")
    final_response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are a senior system architect. Provide deep analysis."},
            {"role": "user", "content": diagnosis_prompt}
        ],
        response_format={"type": "json_object"}
    )

    diagnosis = json.loads(final_response.choices[0].message.content)

    print(f"\n현재 성능: {diagnosis['current_performance'].upper()}")
    print(f"근본 원인: {diagnosis['root_cause'].upper()}")

    print(f"\n📋 진단:")
    print(diagnosis['detailed_diagnosis'])

    print(f"\n✅ 유지할 것:")
    for k in diagnosis['recommended_approach']['keep']:
        print(f"  - {k}")

    print(f"\n🔧 수정할 것:")
    for f in diagnosis['recommended_approach']['fix']:
        print(f"  - {f}")

    print(f"\n➕ 추가할 것:")
    for a in diagnosis['recommended_approach']['add']:
        print(f"  - {a}")

    print(f"\n\n📍 구체적 Next Steps:")
    for step in diagnosis['concrete_next_steps']:
        print(f"\n{step['step']}")
        print(f"  액션: {step['action']}")
        print(f"  기대효과: {step['expected_improvement']}")

    # Save results
    output = {
        "database_status": {
            "contents": contents.count,
            "perceptions": perceptions.count,
            "worldviews": worldviews.count,
            "has_layered_table": has_layered_table
        },
        "test_results": {
            "single_case_score": evaluation['total_score'],
            "average_score": avg_score,
            "score_range": [min(scores), max(scores)],
            "evaluation_details": evaluation
        },
        "diagnosis": diagnosis
    }

    with open('/tmp/comprehensive_analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n\n" + "=" * 80)
    print("✅ 분석 완료. 결과 저장: /tmp/comprehensive_analysis_result.json")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
