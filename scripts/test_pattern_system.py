"""
Test Pattern Management System

Tests:
1. Pattern creation
2. Similarity matching with different thresholds
3. Pattern reinforcement
4. Pattern decay
5. Dead pattern cleanup
"""

import sys
import os
from datetime import datetime, timedelta
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.analyzers import PatternManager
from engines.utils.supabase_client import get_supabase


def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def test_pgvector():
    """Test 1: Verify pgvector extension is enabled"""
    print_section("Test 1: Verify pgvector Extension")

    supabase = get_supabase()

    try:
        # Try to query worldview_patterns table
        result = supabase.table('worldview_patterns').select('*').limit(1).execute()
        print("✅ worldview_patterns table exists and is accessible")
        print(f"   Current pattern count: {len(result.data)}")
        return True
    except Exception as e:
        print(f"❌ Error accessing worldview_patterns table: {str(e)}")
        return False


def test_pattern_creation():
    """Test 2: Create patterns at different layers"""
    print_section("Test 2: Pattern Creation")

    pm = PatternManager()
    supabase = get_supabase()

    # Get a test worldview
    result = supabase.table('worldviews').select('id, title').limit(1).execute()
    if not result.data or len(result.data) == 0:
        print("❌ No worldviews found in database")
        return None

    test_worldview_id = result.data[0]['id']
    test_worldview_title = result.data[0]['title']

    print(f"Using test worldview: {test_worldview_title}")
    print(f"Worldview ID: {test_worldview_id}\n")

    # Create test patterns
    test_patterns = {
        'surface': '테스트 사건: 오늘 댓글 조작 발견됨',
        'implicit': '테스트 전제: 조직적 댓글부대가 존재한다',
        'deep': '테스트 믿음: 외세가 한국을 조종한다'
    }

    created_ids = {}

    for layer, text in test_patterns.items():
        try:
            pattern_id = pm.create_pattern(test_worldview_id, layer, text)
            created_ids[layer] = pattern_id
            print(f"✅ Created {layer} pattern: {pattern_id[:8]}...")
            print(f"   Text: {text}")
        except Exception as e:
            print(f"❌ Failed to create {layer} pattern: {str(e)}")

    return {
        'worldview_id': test_worldview_id,
        'worldview_title': test_worldview_title,
        'pattern_ids': created_ids,
        'pattern_texts': test_patterns
    }


def test_similarity_matching(test_data):
    """Test 3: Test similarity matching with layer-specific thresholds"""
    print_section("Test 3: Similarity Matching")

    if not test_data:
        print("❌ Skipping (no test data)")
        return

    pm = PatternManager()
    worldview_id = test_data['worldview_id']

    # Test similar texts (should match)
    similar_texts = {
        'surface': '테스트 사건: 오늘 댓글 조작이 발견되었음',  # Very similar
        'implicit': '테스트 전제: 조직적인 댓글부대가 활동한다',  # Similar
        'deep': '테스트 믿음: 외세의 한국 조종'  # Similar core meaning
    }

    # Test different texts (should NOT match)
    different_texts = {
        'surface': '완전히 다른 사건: 경제 뉴스 발표됨',
        'implicit': '다른 전제: 정부가 투명하게 운영된다',
        'deep': '다른 믿음: 한국은 자주적으로 운영된다'
    }

    print("Testing SIMILAR texts (should match):")
    for layer, text in similar_texts.items():
        matched = pm.find_similar_pattern(worldview_id, layer, text)
        threshold = pm.SIMILARITY_THRESHOLDS[layer]

        if matched:
            print(f"✅ {layer:8s} matched (threshold: {threshold})")
            print(f"   Query: {text}")
            print(f"   Match: {matched['text']}")
            print(f"   Similarity: {matched.get('similarity', 'N/A')}")
        else:
            print(f"⚠️  {layer:8s} did NOT match (threshold: {threshold})")
            print(f"   Query: {text}")

    print("\nTesting DIFFERENT texts (should NOT match):")
    for layer, text in different_texts.items():
        matched = pm.find_similar_pattern(worldview_id, layer, text)
        threshold = pm.SIMILARITY_THRESHOLDS[layer]

        if matched:
            print(f"⚠️  {layer:8s} matched (unexpected!)")
            print(f"   Query: {text}")
            print(f"   Match: {matched['text']}")
        else:
            print(f"✅ {layer:8s} correctly did NOT match (threshold: {threshold})")
            print(f"   Query: {text}")


def test_pattern_reinforcement(test_data):
    """Test 4: Pattern reinforcement"""
    print_section("Test 4: Pattern Reinforcement")

    if not test_data or 'pattern_ids' not in test_data:
        print("❌ Skipping (no test data)")
        return

    pm = PatternManager()
    supabase = get_supabase()

    # Test surface pattern (fastest decay)
    surface_id = test_data['pattern_ids'].get('surface')
    if not surface_id:
        print("❌ No surface pattern to test")
        return

    # Get initial state
    result = supabase.table('worldview_patterns').select('*').eq('id', surface_id).single().execute()
    initial = result.data

    print(f"Initial state:")
    print(f"  Strength: {initial['strength']}")
    print(f"  Appearance count: {initial['appearance_count']}")
    print(f"  Status: {initial['status']}")

    # Reinforce 3 times
    for i in range(3):
        pm.reinforce_pattern(surface_id)
        print(f"\n  After reinforcement {i+1}:")
        result = supabase.table('worldview_patterns').select('strength, appearance_count').eq('id', surface_id).single().execute()
        print(f"    Strength: {result.data['strength']}")
        print(f"    Appearance count: {result.data['appearance_count']}")

    result = supabase.table('worldview_patterns').select('*').eq('id', surface_id).single().execute()
    final = result.data

    if final['strength'] > initial['strength']:
        print(f"\n✅ Reinforcement working: {initial['strength']} → {final['strength']}")
    else:
        print(f"\n❌ Reinforcement failed: {initial['strength']} → {final['strength']}")


def test_pattern_decay(test_data):
    """Test 5: Pattern decay"""
    print_section("Test 5: Pattern Decay")

    if not test_data:
        print("❌ Skipping (no test data)")
        return

    pm = PatternManager()
    supabase = get_supabase()
    worldview_id = test_data['worldview_id']

    # Manually set last_seen to 3 days ago for surface pattern
    surface_id = test_data['pattern_ids'].get('surface')
    if surface_id:
        three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
        supabase.table('worldview_patterns').update({
            'last_seen': three_days_ago
        }).eq('id', surface_id).execute()

        print(f"Set surface pattern last_seen to 3 days ago")

        # Get before state
        result = supabase.table('worldview_patterns').select('*').eq('id', surface_id).single().execute()
        before = result.data
        print(f"Before decay: strength={before['strength']}, status={before['status']}")

    # Run decay
    print("\nRunning decay_patterns()...")
    stats = pm.decay_patterns(worldview_id)

    print(f"\nDecay Statistics:")
    for layer in ['surface', 'implicit', 'deep']:
        s = stats[layer]
        print(f"  {layer:8s}: {s['total']} total, {s['fading']} fading, {s['dead']} dead")

    # Check after state
    if surface_id:
        result = supabase.table('worldview_patterns').select('*').eq('id', surface_id).single().execute()
        after = result.data
        print(f"\nAfter decay: strength={after['strength']}, status={after['status']}")

        if after['strength'] < before['strength']:
            print(f"✅ Decay working: {before['strength']:.2f} → {after['strength']:.2f}")
        else:
            print(f"❌ Decay failed: {before['strength']:.2f} → {after['strength']:.2f}")


def test_cleanup(test_data):
    """Test 6: Dead pattern cleanup"""
    print_section("Test 6: Dead Pattern Cleanup")

    if not test_data:
        print("❌ Skipping (no test data)")
        return

    pm = PatternManager()
    supabase = get_supabase()
    worldview_id = test_data['worldview_id']

    # Create a pattern and immediately mark it as dead
    dead_pattern_id = pm.create_pattern(worldview_id, 'surface', '테스트: 삭제될 패턴')
    supabase.table('worldview_patterns').update({
        'status': 'dead',
        'strength': 0.05
    }).eq('id', dead_pattern_id).execute()

    print(f"Created dead pattern: {dead_pattern_id[:8]}...")

    # Count before cleanup
    result = supabase.table('worldview_patterns').select('*').eq('worldview_id', worldview_id).eq('status', 'dead').execute()
    before_count = len(result.data)
    print(f"Dead patterns before cleanup: {before_count}")

    # Run cleanup
    removed_count = pm.cleanup_dead_patterns(worldview_id)

    print(f"Removed {removed_count} dead patterns")

    # Count after cleanup
    result = supabase.table('worldview_patterns').select('*').eq('worldview_id', worldview_id).eq('status', 'dead').execute()
    after_count = len(result.data)
    print(f"Dead patterns after cleanup: {after_count}")

    if after_count == 0:
        print(f"✅ Cleanup working: removed all dead patterns")
    else:
        print(f"⚠️  Cleanup partial: {after_count} dead patterns remaining")


def cleanup_test_data(test_data):
    """Clean up test patterns"""
    print_section("Cleanup Test Data")

    if not test_data or 'pattern_ids' not in test_data:
        print("No test data to clean up")
        return

    supabase = get_supabase()

    for layer, pattern_id in test_data['pattern_ids'].items():
        try:
            supabase.table('worldview_patterns').delete().eq('id', pattern_id).execute()
            print(f"✅ Deleted {layer} test pattern")
        except Exception as e:
            print(f"⚠️  Failed to delete {layer} pattern: {str(e)}")


def main():
    print(f"\n{'='*80}")
    print(f"Pattern Management System Test Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # Test 1: pgvector
    if not test_pgvector():
        print("\n❌ pgvector test failed, aborting")
        return

    # Test 2: Pattern creation
    test_data = test_pattern_creation()

    if test_data:
        # Test 3: Similarity matching
        test_similarity_matching(test_data)

        # Test 4: Reinforcement
        test_pattern_reinforcement(test_data)

        # Test 5: Decay
        test_pattern_decay(test_data)

        # Test 6: Cleanup
        test_cleanup(test_data)

        # Clean up test data
        cleanup_test_data(test_data)

    print_section("Test Suite Complete")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == '__main__':
    main()
