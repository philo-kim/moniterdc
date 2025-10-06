"""
Phase 2: Supabase SQL 직접 실행

Supabase Management API를 통해 SQL 실행
"""

import os
import requests

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

# Supabase SQL API endpoint (프로젝트 ID 추출)
project_id = SUPABASE_URL.split('//')[1].split('.')[0]

print("="*80)
print("Phase 2: DB 스키마 생성 (SQL 직접 실행)")
print("="*80)

# 마이그레이션 SQL 읽기
with open('supabase/migrations/201_create_layered_perceptions.sql', 'r') as f:
    migration_201 = f.read()

with open('supabase/migrations/202_create_belief_patterns.sql', 'r') as f:
    migration_202 = f.read()

print("\n⚠️ Supabase Management API 키가 필요합니다.")
print("하지만 보안상 anon key로는 CREATE TABLE 불가능합니다.")
print("\n대안: Supabase Dashboard SQL Editor 사용")
print("="*80)

print("\n다음 URL을 브라우저에서 열고 SQL을 실행하세요:")
print(f"https://supabase.com/dashboard/project/{project_id}/sql/new")

print("\n\n=== 실행할 SQL 1/2 ===")
print(migration_201)

print("\n\n=== 실행할 SQL 2/2 ===")
print(migration_202)

print("\n="*80)
print("SQL 실행 완료 후:")
print("  python3 phase2_verify_schema.py")
print("="*80)
