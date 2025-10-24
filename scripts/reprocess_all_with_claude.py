#!/usr/bin/env python3
"""
Complete Data Reprocessing with Claude Sonnet 4.5

이 스크립트는 전체 데이터를 Claude로 재처리합니다:
1. 456개 contents → Claude Baseline으로 3-layer perception 재추출
2. 재추출된 perceptions → Claude StepByStep으로 5 mechanisms 추출
3. 200 recent perceptions → Claude Data-Driven으로 worldviews 재발견
4. Adaptive Matching으로 perception-worldview 재연결

Usage:
    python3 scripts/reprocess_all_with_claude.py
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers.layered_perception_extractor import LayeredPerceptionExtractor
from engines.analyzers.reasoning_structure_extractor import ReasoningStructureExtractor
from engines.analyzers.worldview_evolution_engine import WorldviewEvolutionEngine
from engines.analyzers.mechanism_matcher import MechanismMatcher
from engines.utils.supabase_client import get_supabase


async def main():
    supabase = get_supabase()

    print("=" * 80)
    print("Complete Data Reprocessing with Claude Sonnet 4.5")
    print("=" * 80)
    print()
    sys.stdout.flush()

    # Step 0: Check current state
    print("📊 Step 0: Checking current database state...")
    sys.stdout.flush()

    contents_result = supabase.table('contents').select('id', count='exact').execute()
    total_contents = contents_result.count
    print(f"   Total contents: {total_contents}")
    print()
    sys.stdout.flush()

    # Step 1: Archive existing worldviews
    print("📦 Step 1: Archiving existing worldviews...")
    sys.stdout.flush()

    archive_result = supabase.table('worldviews').update({
        'archived': True
    }).eq('archived', False).execute()
    print(f"   Archived {len(archive_result.data)} worldviews")
    print()
    sys.stdout.flush()

    # Step 2: Delete existing perception-worldview links
    print("🗑️  Step 2: Deleting existing perception-worldview links...")
    sys.stdout.flush()

    delete_result = supabase.table('perception_worldview_links').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"   Deleted all existing links")
    print()
    sys.stdout.flush()

    # Step 3: Delete existing perceptions
    print("🗑️  Step 3: Deleting existing perceptions...")
    sys.stdout.flush()

    delete_perceptions = supabase.table('layered_perceptions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"   Deleted all existing perceptions")
    print()
    sys.stdout.flush()

    # Step 4: Reprocess all contents with Claude
    print("🔄 Step 4: Reprocessing all contents with Claude...")
    print(f"   Phase 1: 3-layer perception (Baseline)")
    print(f"   Phase 2: Reasoning structure (StepByStep)")
    print(f"   Processing {total_contents} contents...")
    print()
    sys.stdout.flush()

    perception_extractor = LayeredPerceptionExtractor()
    structure_extractor = ReasoningStructureExtractor()

    # Fetch all contents
    contents = supabase.table('contents').select('*').order('published_at', desc=True).execute().data

    processed = 0
    failed = 0

    for i, content in enumerate(contents, 1):
        try:
            print(f"   [{i}/{total_contents}] {content['id'][:8]}...", end=" ")
            sys.stdout.flush()

            # Phase 1: perception (already includes mechanisms from GPT code)
            # Phase 2: structure (standalone - creates its own perception)
            perception_id = await structure_extractor.extract(content)

            processed += 1
            print(f"✅")
            sys.stdout.flush()

            # Progress checkpoint every 50 items
            if i % 50 == 0:
                print()
                print(f"   🔄 Checkpoint: {i}/{total_contents} ({i/total_contents*100:.1f}%)")
                print(f"   📊 Success: {processed}, Failed: {failed}")
                print()
                sys.stdout.flush()

        except Exception as e:
            failed += 1
            error_msg = str(e)[:100]
            print(f"❌ {error_msg}")
            sys.stdout.flush()
            continue

    print()
    print(f"✅ Step 4 Complete: {processed} processed, {failed} failed")
    print()
    sys.stdout.flush()

    # Step 5: Rediscover worldviews with Claude Data-Driven
    print("🔍 Step 5: Rediscovering worldviews with Claude Data-Driven...")
    sys.stdout.flush()

    evolution_engine = WorldviewEvolutionEngine()

    # Fetch 200 recent perceptions
    recent_perceptions = supabase.table('layered_perceptions').select('*').order('created_at', desc=True).limit(200).execute().data
    print(f"   Analyzing {len(recent_perceptions)} recent perceptions...")
    sys.stdout.flush()

    worldviews = await evolution_engine._consolidate_worldviews(recent_perceptions)

    # Save new worldviews
    new_worldview_ids = []
    for wv in worldviews:
        # Build frame structure from individual components
        frame = {
            'actor': wv.get('actor', {}),
            'core_mechanisms': wv.get('core_mechanisms', []),
            'logic_pattern': wv.get('logic_pattern', {}),
            'statistical_basis': wv.get('statistical_basis', {})
        }

        result = supabase.table('worldviews').insert({
            'title': wv['title'],
            'description': wv.get('description', ''),
            'frame': frame,
            'core_subject': wv.get('actor', {}).get('subject', ''),
            'core_attributes': wv.get('core_mechanisms', []),
            'version': 2,
            'archived': False,
            'total_perceptions': 0
        }).execute()

        new_worldview_ids.append(result.data[0]['id'])

    print(f"   ✅ Created {len(worldviews)} new worldviews")
    print()
    sys.stdout.flush()

    # Step 6: Re-link perceptions to worldviews with Adaptive Matching
    print("🔗 Step 6: Linking perceptions to worldviews with Adaptive Matching...")
    sys.stdout.flush()

    matcher = MechanismMatcher()

    all_perceptions = supabase.table('layered_perceptions').select('*').execute().data
    active_worldviews = supabase.table('worldviews').select('*').eq('archived', False).execute().data

    print(f"   Matching {len(all_perceptions)} perceptions to {len(active_worldviews)} worldviews...")
    sys.stdout.flush()

    total_links = 0
    for perception in all_perceptions:
        links = matcher.match_perception_to_worldviews(perception, active_worldviews)
        total_links += len(links)

    print(f"   ✅ Created {total_links} perception-worldview links")
    print()
    sys.stdout.flush()

    # Step 7: Update worldview perception counts
    print("📊 Step 7: Updating worldview perception counts...")
    sys.stdout.flush()

    for worldview in active_worldviews:
        links = supabase.table('perception_worldview_links').select('id', count='exact').eq('worldview_id', worldview['id']).execute()
        count = links.count

        supabase.table('worldviews').update({
            'total_perceptions': count
        }).eq('id', worldview['id']).execute()

    print(f"   ✅ Updated perception counts for {len(active_worldviews)} worldviews")
    print()
    sys.stdout.flush()

    # Final report
    print("=" * 80)
    print("🎉 Complete Data Reprocessing FINISHED")
    print("=" * 80)
    print()
    print(f"📊 Final Statistics:")
    print(f"   Contents processed: {processed}/{total_contents} ({processed/total_contents*100:.1f}%)")
    print(f"   Failed: {failed}")
    print(f"   New worldviews: {len(worldviews)}")
    print(f"   Total links: {total_links}")
    if len(all_perceptions) > 0:
        print(f"   Avg links per perception: {total_links/len(all_perceptions):.2f}")
    print()
    print("✅ All data has been reprocessed with Claude Sonnet 4.5!")
    print()
    sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
