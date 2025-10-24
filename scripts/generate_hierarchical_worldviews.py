#!/usr/bin/env python3
"""
계층적 세계관 생성 스크립트

1단계: 기존 worldview들을 V1+로 상위 세계관 재생성
2단계: 각 상위 세계관마다 V14로 하위 세계관 생성
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from openai import AsyncOpenAI
from supabase import create_client

# Supabase & OpenAI 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# V1+ 프롬프트 (상위 세계관 생성)
PROMPT_V1_PLUS = """
기존 세계관: "{old_title}"

이 세계관에 속한 perception 샘플:
{perception_samples}

**임무: 이 세계관을 "그들의 언어"로 표현하세요**

현재 제목은 분석자의 언어입니다 ("~로 해석", "~으로 귀결").
그들의 언어로 바꾸세요: 그들이 믿는 진실로 표현.

**원칙**:
1. 그들의 확신: "~이다", "~한다" (단정)
2. 완전한 문장: 주어 + 동사 + 목적어
3. 18-25자 길이
4. 강력한 동사: 사찰, 조작, 악용, 왜곡 등

**예시**:
❌ "민주당/좌파의 정보 파악 → 즉시 불법 사찰·장악으로 해석"
✅ "민주당은 불법 사찰로 국민을 감시한다"

JSON 형식으로 반환:
{{
  "title": "새로운 제목 (그들의 언어)",
  "theme_keywords": ["핵심", "키워드", "3-5개"]
}}
"""

# V14 프롬프트 (하위 세계관 생성)
PROMPT_V14 = """
상위 세계관: "{parent_title}"
주제 키워드: {theme_keywords}

이 세계관에 속한 데이터:
{perception_data}

**임무: 구체적 하위 세계관 생성**

상위는 포괄적, 하위는 구체적 사례입니다.

**필수 요구사항**:
1. 완전한 문장 (주어 + 동사 + 목적어)
2. 그들의 확신 ("~한다", "~했다" 단정)
3. 구체적 고유명사 (사람, 장소, 사건)
4. 주제 키워드 포함
5. 모호 표현 금지 ("특정", "일부", "어떤")

**좋은 예시**:
✅ "민주당은 통신사를 협박해 지귀연을 사찰했다"
✅ "짱깨 매크로부대가 게시물 삭제 요청으로 여론을 조작한다"
✅ "법무부장관은 페이스북으로 정치적 보복을 정당화한다"

JSON 배열 형식:
[
  {{
    "title": "완전한 문장",
    "subject": "누가",
    "object": "무엇을",
    "action": "어떻게 동사하는가",
    "is_sentence": true
  }}
]

품질 > 개수. 구체적이지 않으면 생성하지 마세요.
"""


async def generate_parent_worldview(old_worldview: dict, perception_samples: list) -> dict:
    """V1+: 상위 세계관 생성"""

    # perception 샘플 텍스트 생성
    sample_text = ""
    for i, p in enumerate(perception_samples[:10], 1):
        explicit = p.get('explicit_claims', '')
        if isinstance(explicit, list):
            explicit = ' / '.join(str(x) for x in explicit if x)
        sample_text += f"{i}. {explicit[:100]}...\n"

    prompt = PROMPT_V1_PLUS.format(
        old_title=old_worldview['title'],
        perception_samples=sample_text
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 세계관을 '그들의 언어'로 표현하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        content = content.strip()

        result = json.loads(content)
        return result

    except Exception as e:
        print(f"Error generating parent worldview: {e}")
        return None


async def generate_child_worldviews(parent_title: str, theme_keywords: list, perceptions: list) -> list:
    """V14: 하위 세계관 생성"""

    # perception 데이터 포매팅
    perception_text = ""
    for i, p in enumerate(perceptions[:20], 1):
        explicit = p.get('explicit_claims', '')
        deep = p.get('deep_beliefs', '')

        if isinstance(explicit, list):
            explicit = ' / '.join(str(x) for x in explicit if x)
        if isinstance(deep, list):
            deep = ' / '.join(str(x) for x in deep if x)

        if not explicit and not deep:
            continue

        perception_text += f"\n[사례 {i}]\n"
        if explicit:
            perception_text += f"명시적: {explicit}\n"
        if deep:
            perception_text += f"깊은 믿음: {deep}\n"

    if not perception_text:
        return []

    prompt = PROMPT_V14.format(
        parent_title=parent_title,
        theme_keywords=', '.join(theme_keywords),
        perception_data=perception_text
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 구체적 사례를 문장으로 표현하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
        content = content.strip()

        children = json.loads(content)
        return children

    except Exception as e:
        print(f"Error generating child worldviews: {e}")
        return []


async def main():
    """메인 실행 함수"""

    print("=" * 80)
    print("계층적 세계관 생성")
    print("=" * 80)
    print()

    # 1. 기존 worldview 가져오기
    print("1단계: 기존 세계관 로드")
    response = supabase.table('worldviews').select('id, title').eq('archived', False).execute()
    old_worldviews = response.data

    print(f"✅ {len(old_worldviews)}개 기존 세계관 발견")
    print()

    results = []

    for old_wv in old_worldviews:
        print("=" * 80)
        print(f"처리 중: {old_wv['title'][:60]}...")
        print("=" * 80)
        print()

        # 2. 해당 세계관의 perception 가져오기
        links = supabase.table('perception_worldview_links')\
            .select('perception_id')\
            .eq('worldview_id', old_wv['id'])\
            .limit(20)\
            .execute()

        if not links.data:
            print("⚠️  연결된 perception 없음, 건너뜀")
            print()
            continue

        perception_ids = [link['perception_id'] for link in links.data]
        perceptions = supabase.table('layered_perceptions')\
            .select('*')\
            .in_('id', perception_ids)\
            .execute()

        print(f"✅ {len(perceptions.data)}개 perception 로드")

        # 3. V1+로 상위 세계관 생성
        print("📝 V1+ 실행 중 (상위 세계관)...")
        parent = await generate_parent_worldview(old_wv, perceptions.data)

        if not parent:
            print("❌ 상위 세계관 생성 실패")
            print()
            continue

        print(f"✅ 상위: {parent['title']}")
        print(f"   키워드: {', '.join(parent['theme_keywords'])}")
        print()

        # 4. V14로 하위 세계관 생성
        print("📝 V14 실행 중 (하위 세계관)...")
        children = await generate_child_worldviews(
            parent['title'],
            parent['theme_keywords'],
            perceptions.data
        )

        print(f"✅ {len(children)}개 하위 세계관 생성:")
        for i, child in enumerate(children, 1):
            print(f"   {i}. {child.get('title', '')}")
        print()

        results.append({
            'old_worldview_id': old_wv['id'],
            'old_title': old_wv['title'],
            'parent': parent,
            'children': children,
            'perception_count': len(perceptions.data)
        })

    # 5. 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'_hierarchical_worldviews_{timestamp}.json'

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print("전체 요약")
    print("=" * 80)
    print()
    print(f"총 {len(results)}개 세계관 처리")
    total_children = sum(len(r['children']) for r in results)
    print(f"총 {total_children}개 하위 세계관 생성")
    print()
    print(f"✅ 결과 저장: {filename}")
    print()
    print("다음 단계:")
    print("1. 결과 검토")
    print("2. DB 스키마 마이그레이션 적용")
    print("3. DB에 상위/하위 세계관 삽입")


if __name__ == '__main__':
    asyncio.run(main())
