#!/usr/bin/env python3
"""
Test Connection Detector
"""

import asyncio
from uuid import UUID
from engines.detectors import ConnectionDetector
from engines.utils.supabase_client import get_supabase

async def test_connection_detector():
    print("🧪 Testing Connection Detector...\n")

    detector = ConnectionDetector()
    supabase = get_supabase()

    # Get a recent perception
    response = supabase.table('perceptions').select('id, perceived_subject, perceived_attribute').order('created_at', desc=True).limit(1).execute()

    if not response.data:
        print("❌ No perceptions found")
        return

    perception = response.data[0]
    perception_id = UUID(perception['id'])

    print(f"📄 Testing with perception:")
    print(f"  ID: {perception_id}")
    print(f"  Subject: {perception['perceived_subject']}")
    print(f"  Attribute: {perception['perceived_attribute']}\n")

    # Detect connections
    print("🔍 Detecting connections...")
    connection_ids = await detector.detect_connections(perception_id)

    print(f"\n✅ Detected {len(connection_ids)} connections\n")

    # Display connections
    if connection_ids:
        print("📋 Connections:")
        for i, conn_id in enumerate(connection_ids[:5], 1):  # Show first 5
            response = supabase.table('perception_connections').select('*').eq('id', str(conn_id)).execute()

            if response.data:
                c = response.data[0]
                print(f"\n  {i}. Connection {conn_id}")
                print(f"     Type: {c['connection_type']}")
                print(f"     Strength: {c['strength']}")
                print(f"     From: {c['from_perception_id']}")
                print(f"     To: {c['to_perception_id']}")

if __name__ == '__main__':
    asyncio.run(test_connection_detector())
