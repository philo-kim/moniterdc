#!/usr/bin/env python3
"""
Complete Phase 1 Test - Full Integration with Real OpenAI API
"""

import asyncio
from engines.pipeline import AnalysisPipeline
from engines.utils.supabase_client import get_supabase

async def test_complete_phase1():
    print("=" * 70)
    print("🚀 PHASE 1 COMPLETE TEST - Real OpenAI API Integration")
    print("=" * 70)
    print()

    # Use real OpenAI extractor (not simple)
    pipeline = AnalysisPipeline(use_simple_extractor=False)
    supabase = get_supabase()

    # Get initial stats
    print("📊 Initial System State:")
    initial_stats = await pipeline.get_pipeline_stats()
    for key, value in initial_stats.items():
        print(f"  {key}: {value}")
    print()

    # Get a few existing contents to test
    response = supabase.table('contents').select('id, title').limit(3).execute()

    if not response.data:
        print("❌ No contents found. Run content collection first.")
        return

    from uuid import UUID
    content_ids = [UUID(item['id']) for item in response.data]

    print(f"📥 Testing with {len(content_ids)} existing contents:")
    for i, item in enumerate(response.data, 1):
        print(f"  {i}. {item['title']}")
    print()

    # Stage 1: Perception Extraction with Real GPT-4
    print("=" * 70)
    print("🔍 Stage 1: Perception Extraction (GPT-4o-mini)")
    print("=" * 70)

    try:
        extraction_result = await pipeline.run_extraction(content_ids)

        print(f"\n✅ Extraction Complete:")
        print(f"  Perceptions extracted: {extraction_result['count']}")

        if extraction_result['perception_ids']:
            # Show sample perception
            first_pid = extraction_result['perception_ids'][0]
            p_response = supabase.table('perceptions').select('*').eq('id', str(first_pid)).execute()

            if p_response.data:
                p = p_response.data[0]
                print(f"\n📋 Sample Perception:")
                print(f"  Subject: {p['perceived_subject']}")
                print(f"  Attribute: {p['perceived_attribute']}")
                print(f"  Valence: {p['perceived_valence']}")
                print(f"  Claims: {p['claims']}")
                print(f"  Emotions: {p['emotions']}")
                print(f"  Embedding: [{len(p['perception_embedding'])} dimensions]")

                # Verify embedding is not all zeros
                embedding = p['perception_embedding']
                if all(v == 0.0 for v in embedding):
                    print(f"  ⚠️  WARNING: Embedding is all zeros (mock data)")
                else:
                    print(f"  ✅ Embedding is real (non-zero values)")
                    print(f"     Sample: [{embedding[0]:.6f}, {embedding[1]:.6f}, {embedding[2]:.6f}, ...]")

    except Exception as e:
        print(f"\n❌ Extraction Failed: {e}")
        print(f"\nℹ️  If you see quota errors, make sure:")
        print(f"   1. OpenAI API key is updated in .env")
        print(f"   2. Account has sufficient credits")
        print(f"   3. Billing is active")
        return

    if not extraction_result['perception_ids']:
        print("❌ No perceptions extracted")
        return

    # Stage 2: Connection Detection with Vector Similarity
    print("\n" + "=" * 70)
    print("🔗 Stage 2: Connection Detection (Vector Similarity)")
    print("=" * 70)

    connection_result = await pipeline.run_connection(extraction_result['perception_ids'])

    print(f"\n✅ Connection Detection Complete:")
    print(f"  Connections detected: {connection_result['count']}")

    if connection_result['connection_ids']:
        # Show connection types
        conn_types = {}
        for conn_id in connection_result['connection_ids'][:20]:  # Sample first 20
            c_response = supabase.table('perception_connections').select('connection_type').eq('id', str(conn_id)).execute()
            if c_response.data:
                conn_type = c_response.data[0]['connection_type']
                conn_types[conn_type] = conn_types.get(conn_type, 0) + 1

        print(f"\n📊 Connection Types Distribution:")
        for conn_type, count in conn_types.items():
            print(f"  {conn_type}: {count}")

    # Final stats
    print("\n" + "=" * 70)
    print("📊 FINAL SYSTEM STATE")
    print("=" * 70)

    final_stats = await pipeline.get_pipeline_stats()
    for key, value in final_stats.items():
        old_value = initial_stats.get(key, 0)
        diff = value - old_value
        symbol = "+" if diff > 0 else ""
        print(f"  {key}: {value} ({symbol}{diff})")

    print("\n" + "=" * 70)
    print("✅ PHASE 1 COMPLETE - All Components Working with Real OpenAI API")
    print("=" * 70)
    print("\n✨ Next Steps:")
    print("  - Phase 2: Worldview Detection & Mechanism Analysis")
    print("  - Phase 3: Deconstruction Engine & Dashboard UI")

if __name__ == '__main__':
    asyncio.run(test_complete_phase1())
