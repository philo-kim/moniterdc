#!/usr/bin/env python3
"""
Migrate existing logic_repository data to new system
228 logics → contents → perceptions → connections
"""

import asyncio
import os
from datetime import datetime
from uuid import UUID
from dotenv import load_dotenv

from engines.utils.supabase_client import get_supabase
from engines.extractors.perception_extractor_simple import SimplePerceptionExtractor
from engines.detectors import ConnectionDetector

load_dotenv()

async def migrate_logic_repository():
    """Migrate all logic_repository data to new system"""

    print("=" * 70)
    print("🔄 Starting Migration: logic_repository → new system")
    print("=" * 70)
    print()

    supabase = get_supabase()
    extractor = SimplePerceptionExtractor()
    detector = ConnectionDetector()

    # 1. Get all existing logics
    print("📥 Step 1: Fetching existing logic_repository data...")
    response = supabase.table('logic_repository').select('*').execute()

    if not response.data:
        print("❌ No data found in logic_repository")
        return

    logics = response.data
    print(f"✅ Found {len(logics)} logics to migrate")
    print()

    # Statistics
    stats = {
        'total_logics': len(logics),
        'migrated_contents': 0,
        'extracted_perceptions': 0,
        'detected_connections': 0,
        'skipped': 0,
        'errors': 0
    }

    # 2. Migrate each logic
    print("=" * 70)
    print("📋 Step 2: Migrating logics to contents...")
    print("=" * 70)
    print()

    content_ids = []

    for i, logic in enumerate(logics, 1):
        try:
            print(f"[{i}/{len(logics)}] Migrating logic {logic['id'][:8]}...")

            # Check if already migrated
            existing = supabase.table('contents')\
                .select('id')\
                .eq('source_url', logic.get('original_url', ''))\
                .execute()

            if existing.data:
                print(f"  ⏭️  Already migrated, skipping")
                stats['skipped'] += 1
                content_ids.append(UUID(existing.data[0]['id']))
                continue

            # Create content from logic
            content_data = {
                'source_type': 'dc_gallery',
                'source_url': logic.get('original_url', f"migrated_{logic['id']}"),
                'source_id': logic.get('original_post_num', logic['id']),
                'title': logic.get('original_title', '(제목 없음)'),
                'body': logic.get('original_content', ''),
                'metadata': {
                    'gallery': logic.get('source_gallery', 'unknown'),
                    'migrated_from': 'logic_repository',
                    'original_id': logic['id'],
                    'logic_type': logic.get('logic_type', 'attack'),
                    'frame': logic.get('frame', ''),
                    'target': logic.get('target', '')
                },
                'base_credibility': 0.2,
                'published_at': logic.get('created_at', datetime.now().isoformat())
            }

            response = supabase.table('contents').insert(content_data).execute()

            if response.data:
                content_id = UUID(response.data[0]['id'])
                content_ids.append(content_id)
                stats['migrated_contents'] += 1
                print(f"  ✅ Created content {content_id}")
            else:
                print(f"  ❌ Failed to create content")
                stats['errors'] += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            stats['errors'] += 1

    print()
    print(f"📊 Contents Migration Summary:")
    print(f"  Total: {stats['total_logics']}")
    print(f"  Migrated: {stats['migrated_contents']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")
    print()

    # 3. Extract perceptions
    print("=" * 70)
    print("🔍 Step 3: Extracting perceptions from migrated contents...")
    print("=" * 70)
    print()

    all_perception_ids = []

    for i, content_id in enumerate(content_ids, 1):
        try:
            print(f"[{i}/{len(content_ids)}] Extracting from content {str(content_id)[:8]}...")

            perception_ids = await extractor.extract(content_id)

            if perception_ids:
                all_perception_ids.extend(perception_ids)
                stats['extracted_perceptions'] += len(perception_ids)
                print(f"  ✅ Extracted {len(perception_ids)} perceptions")
            else:
                print(f"  ⚠️  No perceptions extracted")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            stats['errors'] += 1

    print()
    print(f"📊 Perception Extraction Summary:")
    print(f"  Total perceptions: {stats['extracted_perceptions']}")
    print()

    # 4. Detect connections
    print("=" * 70)
    print("🔗 Step 4: Detecting connections between perceptions...")
    print("=" * 70)
    print()

    all_connection_ids = set()

    for i, perception_id in enumerate(all_perception_ids, 1):
        try:
            if i % 10 == 0 or i == 1:
                print(f"[{i}/{len(all_perception_ids)}] Processing perception {str(perception_id)[:8]}...")

            connection_ids = await detector.detect_connections(perception_id)

            if connection_ids:
                all_connection_ids.update(connection_ids)

        except Exception as e:
            if i % 10 == 0:
                print(f"  ❌ Error: {e}")

    stats['detected_connections'] = len(all_connection_ids)

    print()
    print(f"📊 Connection Detection Summary:")
    print(f"  Total connections: {stats['detected_connections']}")
    print()

    # Final Summary
    print("=" * 70)
    print("✅ Migration Complete!")
    print("=" * 70)
    print()
    print("📊 Final Statistics:")
    print(f"  Logics processed: {stats['total_logics']}")
    print(f"  Contents created: {stats['migrated_contents']}")
    print(f"  Perceptions extracted: {stats['extracted_perceptions']}")
    print(f"  Connections detected: {stats['detected_connections']}")
    print(f"  Errors: {stats['errors']}")
    print()

    return stats

async def verify_migration():
    """Verify migration results"""

    print("=" * 70)
    print("🔍 Verifying Migration...")
    print("=" * 70)
    print()

    supabase = get_supabase()

    # Check counts
    logics = supabase.table('logic_repository').select('id', count='exact').execute()
    contents = supabase.table('contents').select('id', count='exact').execute()
    perceptions = supabase.table('perceptions').select('id', count='exact').execute()
    connections = supabase.table('perception_connections').select('id', count='exact').execute()

    print("📊 Database State:")
    print(f"  logic_repository: {logics.count}")
    print(f"  contents: {contents.count}")
    print(f"  perceptions: {perceptions.count}")
    print(f"  connections: {connections.count}")
    print()

    # Check migrated contents
    migrated = supabase.table('contents')\
        .select('id')\
        .eq('metadata->>migrated_from', 'logic_repository')\
        .execute()

    print(f"✅ Migrated contents: {len(migrated.data) if migrated.data else 0}")
    print()

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        asyncio.run(verify_migration())
    else:
        asyncio.run(migrate_logic_repository())
