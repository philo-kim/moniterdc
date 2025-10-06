#!/usr/bin/env python3
"""
Re-cluster existing logics by political_frame
This script re-analyzes existing logics to extract political frames
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client
from openai import AsyncOpenAI

load_dotenv()

async def main():
    print("🔄 Re-clustering by political frames...")

    # Initialize clients
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # 1. Clear existing clusters
    print("\n1️⃣ Clearing existing clusters...")
    supabase.table('logic_clusters').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    supabase.table('logic_repository').update({'cluster_id': None}).neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print("✅ Clusters cleared")

    # 2. Get all logics
    print("\n2️⃣ Fetching all logics...")
    result = supabase.table('logic_repository').select('*').order('created_at', desc=True).execute()
    logics = result.data
    print(f"Found {len(logics)} logics")

    # 3. Re-analyze each logic to extract political_frame
    print("\n3️⃣ Re-analyzing logics to extract political frames...")

    updated_count = 0
    skipped_count = 0

    for i, logic in enumerate(logics, 1):
        print(f"\n[{i}/{len(logics)}] Processing: {logic['original_title'][:50]}...")

        # Skip if already has political_frame
        if logic.get('political_frame'):
            print(f"  ℹ️  Already has frame: {logic['political_frame']}")
            skipped_count += 1
            continue

        try:
            # Re-analyze with GPT
            response = await openai_client.chat.completions.create(
                model=os.getenv('GPT_ANALYSIS_MODEL', 'gpt-5-mini'),
                messages=[
                    {
                        'role': 'system',
                        'content': '''당신은 한국 정치 논리 분석 전문가입니다. DC갤러리 개념글을 분석하여 **이 글이 어떤 정치적 프레임/내러티브를 구성하는지** 파악하세요.

**핵심 목적**: 이 글이 어떤 **왜곡된 세계관**을 만들어내는 데 기여하는가?

정치적 프레임/내러티브 예시:
- "민주당=친중=국가안보위협" → 중국인무비자, 중국인도망, 간첩의혹, 친중외교 등의 글들이 이 프레임 구성
- "이재명=범죄자=민주당붕괴" → 김혜경쇼핑, 대장동의혹, 위증교사 등의 글들이 이 프레임 구성
- "윤석열=국가수호자" → 안보강화, 북한대응, 동맹강화 등의 글들이 이 프레임 구성
- "한국언론=편파=조작" → KBS편파, MBC왜곡, 언론개혁필요 등의 글들이 이 프레임 구성

다음 JSON 구조로만 응답하세요:
{
  "political_frame": "이 글이 구성하는 정치적 프레임/내러티브 (예: 민주당=친중=안보위협, 이재명=범죄자, 윤석열=국가수호자, 한국언론=편파)",
  "context_issue": "구체적 이슈/사건 (예: 중국인무비자, 김혜경쇼핑, KBS편파보도)"
}

**중요**:
- political_frame: 여러 글들이 공유할 수 있는 **큰 내러티브/세계관**
- context_issue: 이 글이 다루는 **구체적 사건/이슈**
- 같은 political_frame을 가진 글들은 다른 context_issue를 다루더라도 같은 왜곡된 세계관을 구성함'''
                    },
                    {
                        'role': 'user',
                        'content': f'제목: {logic["original_title"]}\n\n본문: {logic["original_content"][:1000]}'
                    }
                ]
            )

            analysis_text = response.choices[0].message.content.strip()

            # JSON 추출
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()

            analysis = json.loads(analysis_text)

            political_frame = analysis.get('political_frame')
            context_issue = analysis.get('context_issue')

            if not political_frame:
                print(f"  ⚠️  No political frame identified")
                continue

            # Update logic
            supabase.table('logic_repository').update({
                'political_frame': political_frame,
                'context_issue': context_issue or logic.get('context_issue')
            }).eq('id', logic['id']).execute()

            print(f"  ✅ Frame: {political_frame}")
            print(f"     Issue: {context_issue}")

            updated_count += 1

            # Rate limiting
            await asyncio.sleep(1)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    print(f"\n✅ Re-analysis complete!")
    print(f"   Updated: {updated_count}")
    print(f"   Skipped: {skipped_count}")

    # 4. Re-cluster by political_frame
    print("\n4️⃣ Re-clustering by political frames...")

    result = supabase.table('logic_repository').select('*').not_.is_('political_frame', 'null').order('created_at', desc=True).execute()
    logics_with_frames = result.data

    cluster_map = {}  # political_frame -> cluster_id

    for logic in logics_with_frames:
        frame = logic['political_frame']

        if frame not in cluster_map:
            # Create new cluster
            cluster_result = supabase.table('logic_clusters').insert({
                'cluster_name': frame,
                'political_frame': frame,
                'context_issue': logic.get('context_issue'),
                'common_distortion_pattern': logic.get('distortion_pattern'),
                'logic_count': 0,
                'first_seen': logic['created_at'],
                'last_seen': logic['created_at']
            }).execute()

            cluster_map[frame] = cluster_result.data[0]['id']
            print(f"  🆕 Created cluster: {frame}")

        # Assign logic to cluster
        cluster_id = cluster_map[frame]
        supabase.table('logic_repository').update({
            'cluster_id': cluster_id
        }).eq('id', logic['id']).execute()

        # Update cluster stats
        supabase.table('logic_clusters').update({
            'logic_count': supabase.table('logic_repository').select('id', count='exact').eq('cluster_id', cluster_id).execute().count,
            'last_seen': logic['created_at']
        }).eq('id', cluster_id).execute()

    print(f"\n✅ Re-clustering complete!")
    print(f"   Total clusters: {len(cluster_map)}")
    print(f"   Logics clustered: {len(logics_with_frames)}")

    # 5. Show cluster stats
    print("\n📊 Cluster Statistics:")
    for frame, cluster_id in sorted(cluster_map.items(), key=lambda x: x[0]):
        count = supabase.table('logic_repository').select('id', count='exact').eq('cluster_id', cluster_id).execute().count
        print(f"   {frame}: {count}개")

if __name__ == '__main__':
    asyncio.run(main())