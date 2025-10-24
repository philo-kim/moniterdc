"""
Apply SQL migrations manually through Python

Since we don't have supabase CLI with Docker, we'll execute SQL directly
"""

import requests
import os

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ycmcsdbxnpmthekzyppl.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')

# Read migration files
with open('supabase/migrations/201_create_layered_perceptions.sql', 'r') as f:
    migration_201 = f.read()

with open('supabase/migrations/202_create_belief_patterns.sql', 'r') as f:
    migration_202 = f.read()

print("="*80)
print("마이그레이션 적용")
print("="*80)

print("\nSupabase Dashboard SQL Editor에서 다음 SQL을 실행해주세요:")
print("\n1. layered_perceptions 테이블 생성:")
print("-"*80)
print(migration_201)
print("\n2. belief_patterns 테이블 생성:")
print("-"*80)
print(migration_202)

print("\n="*80)
print("완료 후 Enter를 눌러주세요...")
input()

print("✅ 마이그레이션 완료로 간주합니다")
