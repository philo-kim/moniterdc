import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def quick_test():
    sample_text = """
제목: 민주, 지귀연 핸드폰 교체 어떻게 알았나
본문: 유심교체를 어떻게 알았냐? 사찰 아니면 불가능하다
"""

    print('='*80)
    print('GPT-5-mini vs GPT-5 성능 비교')
    print('='*80)

    # GPT-5-mini 테스트
    print('\n🔵 GPT-5-mini 분석 중...')
    mini_response = await client.chat.completions.create(
        model='gpt-5-mini',
        messages=[
            {'role': 'system', 'content': '정치 담론을 분석하세요.'},
            {'role': 'user', 'content': f'{sample_text}\n\n이 글에서 deep beliefs를 3개 추출하세요.'}
        ]
    )

    print(f'\n[GPT-5-mini 결과]')
    print(mini_response.choices[0].message.content[:300])
    print(f'\n토큰: {mini_response.usage.total_tokens}')
    mini_cost = mini_response.usage.total_tokens / 1000 * 0.0001
    print(f'비용: ${mini_cost:.6f}')

    # GPT-5 테스트
    print('\n\n🟢 GPT-5 분석 중...')
    full_response = await client.chat.completions.create(
        model='gpt-5',
        messages=[
            {'role': 'system', 'content': '정치 담론을 분석하세요.'},
            {'role': 'user', 'content': f'{sample_text}\n\n이 글에서 deep beliefs를 3개 추출하세요.'}
        ]
    )

    print(f'\n[GPT-5 결과]')
    print(full_response.choices[0].message.content[:300])
    print(f'\n토큰: {full_response.usage.total_tokens}')
    full_cost = full_response.usage.total_tokens / 1000 * 0.003
    print(f'비용: ${full_cost:.6f}')

    # 비교
    print('\n' + '='*80)
    print('📊 비교 결과')
    print('='*80)
    cost_ratio = full_cost/mini_cost if mini_cost > 0 else 0
    print(f'\n비용 차이: {cost_ratio:.1f}x')
    print(f'월 예상 비용 (100개/일):')
    print(f'  GPT-5-mini: ${mini_cost * 100 * 30:.2f}')
    print(f'  GPT-5: ${full_cost * 100 * 30:.2f}')

asyncio.run(quick_test())
