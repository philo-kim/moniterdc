"""
81개 글 깊이 읽고 실제 세계관 찾기
"""
from engines.utils.supabase_client import get_supabase
import re

supabase = get_supabase()

print('=' * 80)
print('81개 글 깊이 분석: 실제 머릿속 세계관 찾기')
print('=' * 80)

# Get all contents
contents = supabase.table('contents').select('title, body').execute()

# 키워드로 그룹핑
groups = {
    '민주당/이재명 관련': [],
    '좌파/극좌 관련': [],
    '중국/짱개 관련': [],
    '윤석열/대통령 관련': [],
    '시위/집회 관련': [],
    '김현지/대통령실 관련': [],
    '기타': []
}

for c in contents.data:
    title = c['title']
    body = c['body']
    text = title + ' ' + body

    if any(k in text for k in ['민주', '이재명', '더불어']):
        groups['민주당/이재명 관련'].append(c)
    elif any(k in text for k in ['좌파', '극좌', '빨갱이']):
        groups['좌파/극좌 관련'].append(c)
    elif any(k in text for k in ['중국', '짱개', '조선족', 'BYD']):
        groups['중국/짱개 관련'].append(c)
    elif any(k in text for k in ['윤석열', '윤카', '대통령']):
        groups['윤석열/대통령 관련'].append(c)
    elif any(k in text for k in ['시위', '집회', '자유대학']):
        groups['시위/집회 관련'].append(c)
    elif any(k in text for k in ['김현지', '강훈식', '대통령실']):
        groups['김현지/대통령실 관련'].append(c)
    else:
        groups['기타'].append(c)

print('\n주제별 글 분포:')
for theme, items in groups.items():
    print(f'  {theme}: {len(items)}개')

# 각 그룹의 실제 내용 분석
print('\n' + '=' * 80)
print('각 그룹의 실제 내용 (본문 읽기)')
print('=' * 80)

for theme, items in groups.items():
    if len(items) == 0 or theme == '기타':
        continue

    print(f'\n### {theme} ({len(items)}개 글)')
    print('-' * 80)

    # 샘플 3개 본문 출력
    for i, item in enumerate(items[:3], 1):
        print(f'\n[글 {i}] {item["title"]}')
        body = item['body'][:300] if len(item['body']) > 300 else item['body']
        print(f'본문: {body}...')
        print()

print('\n' + '=' * 80)
print('이 글들에서 읽히는 실제 세계관')
print('=' * 80)
print("""
읽어보니 이들이 실제로 믿고 있는 것:

1. "우파 = 애국 / 좌파 = 무관심" 프레임
   - 자유대학 시위에 참여하는 건 우파만
   - 좌파들은 국가 위기에도 무관심
   - "좌파들은 도대체 어디서 뭐함?"

2. "민주당 = 독재 + 사찰" 프레임
   - 민주당이 개인정보 사찰
   - "독재시대 예고편"
   - 권력 남용

3. "중국 = 위협" 프레임
   - 중국인 무비자 = 위험
   - 조선족 몰려옴
   - 아동실종, 장기밀매

4. "윤석열 = 선견지명" 프레임
   - "몇 수 앞을 내다보신"
   - 트럼프와의 관계
   - 올바른 방향

5. "이재명 = 무능 + 범죄" 프레임
   - 영어 못함
   - "개 미친 소리"
   - 부정적 이미지

이것들이 서로 연결되어 하나의 일관된 세계관 형성
""")
