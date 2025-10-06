#!/usr/bin/env python3
"""
Test Worldview Mechanisms - Verify cognitive biases, formation phases, and structural flaws
"""

import asyncio
from engines.utils.supabase_client import get_supabase
import json

async def test_mechanisms():
    print("=" * 70)
    print("🧪 Testing Worldview Mechanisms")
    print("=" * 70)
    print()

    supabase = get_supabase()

    # Get all worldviews
    response = supabase.table('worldviews').select('*').execute()

    if not response.data:
        print("❌ No worldviews found")
        return

    for i, w in enumerate(response.data, 1):
        print(f"{'='*70}")
        print(f"Worldview {i}: {w['title']}")
        print(f"{'='*70}")
        print()

        # Formation Phases
        print("📅 Formation Phases:")
        phases = w.get('formation_phases', [])
        if phases:
            for phase in phases:
                print(f"  - {phase.get('phase', 'unknown')}: {phase.get('perception_count', 0)} perceptions")
                print(f"    {phase.get('description', '')}")
                if 'tactics' in phase:
                    print(f"    Tactics: {', '.join(phase['tactics'])}")
        else:
            print("  (No phases detected)")
        print()

        # Cognitive Mechanisms
        print("🧠 Cognitive Mechanisms:")
        mechanisms = w.get('cognitive_mechanisms', [])
        if mechanisms:
            for mech in mechanisms:
                print(f"  - {mech.get('name', 'unknown')} ({mech.get('type', '')})")
                print(f"    {mech.get('description', '')}")
                print(f"    Vulnerability: {mech.get('vulnerability', '')}")
                if 'strength' in mech:
                    print(f"    Strength: {mech['strength']:.2f}")
        else:
            print("  (No mechanisms detected)")
        print()

        # Structural Flaws
        print("⚠️  Structural Flaws:")
        flaws = w.get('structural_flaws', [])
        if flaws:
            for flaw in flaws:
                print(f"  - {flaw.get('name', 'unknown')} ({flaw.get('type', '')})")
                print(f"    {flaw.get('description', '')}")
                print(f"    Counter: {flaw.get('counter', '')}")
        else:
            print("  (No flaws detected)")
        print()

if __name__ == '__main__':
    asyncio.run(test_mechanisms())
