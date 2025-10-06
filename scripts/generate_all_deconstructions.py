#!/usr/bin/env python3
"""
Generate deconstructions for all worldviews

Batch process to create deconstruction strategies for all worldviews
"""

import asyncio
from engines.deconstructors import DeconstructionEngine

async def main():
    """Generate deconstructions for all worldviews"""

    print("=" * 70)
    print("🔧 Generating Deconstructions for All Worldviews")
    print("=" * 70)
    print()

    engine = DeconstructionEngine()

    # Deconstruct all worldviews
    stats = await engine.deconstruct_all_worldviews(force=False)

    print()
    print("=" * 70)
    print("✅ Batch Deconstruction Complete!")
    print("=" * 70)
    print()
    print(f"Total worldviews: {stats.get('total', 0)}")
    print(f"Processed: {stats.get('processed', 0)}")
    print(f"Skipped (already exist): {stats.get('skipped', 0)}")
    print(f"Failed: {stats.get('failed', 0)}")
    print()

if __name__ == '__main__':
    asyncio.run(main())
