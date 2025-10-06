#!/usr/bin/env python3
"""
Test political frame clustering with existing data
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    print("🧪 Testing Political Frame Clustering\n")

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    # Get logics that already have political_frame
    result = supabase.table('logic_repository').select('political_frame, context_issue').not_.is_('political_frame', 'null').execute()
    logics = result.data

    print(f"📊 Found {len(logics)} logics with political_frame\n")

    # Group by political_frame
    frames = {}
    for logic in logics:
        frame = logic['political_frame']
        if frame not in frames:
            frames[frame] = []
        frames[frame].append(logic.get('context_issue', 'N/A'))

    # Display frames and their issues
    print(f"🎯 Unique Political Frames: {len(frames)}\n")

    for frame, issues in sorted(frames.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n📍 {frame}")
        print(f"   논리 수: {len(issues)}")
        if issues:
            unique_issues = set([i for i in issues if i and i != 'N/A'])
            if unique_issues:
                print(f"   관련 이슈: {', '.join(list(unique_issues)[:5])}")

    # Check clusters
    print("\n" + "="*60)
    print("🔗 Current Clusters\n")

    clusters_result = supabase.table('logic_clusters').select('political_frame, logic_count').execute()
    clusters = clusters_result.data

    print(f"Total clusters: {len(clusters)}\n")

    for cluster in sorted(clusters, key=lambda x: x['logic_count'], reverse=True):
        print(f"• {cluster['political_frame']}: {cluster['logic_count']}개")

if __name__ == '__main__':
    main()