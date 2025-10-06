"""
실제 분석 결과의 유의미성 검증
"""
from engines.utils.supabase_client import get_supabase
import json

supabase = get_supabase()

# Get all worldviews with their deconstruction
worldviews = supabase.table('worldviews').select('*').execute()

print('=' * 80)
print('현재 시스템이 탐지한 세계관과 분석 결과')
print('=' * 80)

for wv in worldviews.data:
    print('\n' + '=' * 80)
    print(f'세계관: {wv["title"]}')
    print(f'프레임: {wv["frame"]}')
    print(f'관련 글: {wv["total_perceptions"]}개')
    print(f'강도: {wv["strength_overall"]}')

    # Get sample perceptions
    perception_ids = wv.get('perception_ids', [])[:5]
    if perception_ids:
        perceptions = supabase.table('perceptions').select('perceived_subject, perceived_attribute, claims').in_('id', perception_ids).execute()
        print(f'\n주요 인식 샘플 (5개):')
        for i, p in enumerate(perceptions.data, 1):
            print(f'  {i}. {p["perceived_subject"]} = {p["perceived_attribute"]}')
            if p.get('claims'):
                claims_text = p["claims"][:150] if len(p["claims"]) > 150 else p["claims"]
                print(f'     주장: {claims_text}')

    # Deconstruction analysis
    dec = wv.get('deconstruction')
    if dec:
        print(f'\n📊 해체 분석:')
        flaws = dec.get('flaws', [])
        print(f'  탐지된 결함: {len(flaws)}개')
        for flaw in flaws:
            print(f'    - [{flaw["severity"]}] {flaw["type"]}: {flaw["description"]}')

        counter = dec.get('counter_narrative', '')
        if counter:
            print(f'\n  대안 서사:')
            print(f'    {counter[:300]}...' if len(counter) > 300 else f'    {counter}')

        rebuttals = dec.get('key_rebuttals', [])
        if rebuttals:
            print(f'\n  핵심 반박 ({len(rebuttals)}개):')
            for i, reb in enumerate(rebuttals[:2], 1):
                print(f'    {i}. {reb}')

    print('=' * 80)

# Get actual content samples
print('\n\n' + '=' * 80)
print('원본 컨텐츠 샘플 (실제 DC 글)')
print('=' * 80)

contents = supabase.table('contents').select('title, body, url').limit(5).execute()
for i, content in enumerate(contents.data, 1):
    print(f'\n--- 글 #{i} ---')
    print(f'제목: {content["title"]}')
    print(f'본문: {content["body"][:200]}...')
    print(f'URL: {content["url"]}')
