#!/usr/bin/env python3
"""
Enhanced Alert Sender v2.0
Logic Defense System 알림 발송 - 매칭 정보 포함
"""

import asyncio
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode
from supabase import create_client

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class AlertSenderV2:
    """향상된 알림 발송 시스템"""
    
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.processed_alerts = set()

    async def get_pending_alerts(self) -> List[Dict]:
        """발송 대기 중인 알림 가져오기 (우선순위순)"""
        try:
            # severity 순서: critical > high > medium > low
            result = self.supabase.table('alerts').select('*').is_(
                'sent_at', 'null'
            ).order('created_at', desc=False).limit(20).execute()

            alerts = result.data if result.data else []
            
            # 우선순위 정렬
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            alerts.sort(key=lambda x: (
                priority_order.get(x.get('severity', 'low'), 4),
                x.get('created_at', '')
            ))
            
            return alerts

        except Exception as e:
            logger.error(f"Error fetching pending alerts: {str(e)}")
            return []

    async def enrich_alert_with_logic_info(self, alert: Dict) -> Dict:
        """알림에 논리 정보 추가"""
        try:
            metadata = alert.get('metadata', {})
            
            # 논리 정보가 있으면 조회
            if metadata.get('logic_id'):
                logic = self.supabase.table('logic_repository').select('*').eq(
                    'id', metadata['logic_id']
                ).single().execute()
                
                if logic.data:
                    alert['logic_info'] = logic.data
            
            # 매칭 정보가 있으면 조회
            if metadata.get('match_id'):
                match = self.supabase.table('logic_matches').select(
                    '*, attack:attack_id(*), defense:defense_id(*)'
                ).eq(
                    'id', metadata['match_id']
                ).single().execute()
                
                if match.data:
                    alert['match_info'] = match.data
            
            # 공격/방어 ID로 직접 조회
            if metadata.get('attack_id'):
                attack = self.supabase.table('logic_repository').select('*').eq(
                    'id', metadata['attack_id']
                ).single().execute()
                if attack.data:
                    alert['attack_info'] = attack.data
                    
            if metadata.get('defense_id'):
                defense = self.supabase.table('logic_repository').select('*').eq(
                    'id', metadata['defense_id']
                ).single().execute()
                if defense.data:
                    alert['defense_info'] = defense.data
            
            return alert
            
        except Exception as e:
            logger.error(f"Error enriching alert: {str(e)}")
            return alert

    def format_telegram_message(self, alert: Dict) -> str:
        """텔레그램 메시지 포맷 v2.0"""
        
        severity_emoji = {
            'critical': '🚨',
            'high': '🔴',
            'medium': '🟡',
            'low': '🔵'
        }
        
        severity = alert.get('severity', 'low')
        emoji = severity_emoji.get(severity, '📌')
        
        # 기본 메시지
        message = f"{emoji} **{alert.get('title', '알림')}**\n\n"
        
        # 논리 정보가 있으면 추가
        if 'logic_info' in alert:
            logic = alert['logic_info']
            message += f"**{'🔴 공격' if logic['logic_type'] == 'attack' else '🛡️ 방어'} 논리**\n"
            message += f"📝 {logic['core_argument']}\n"
            message += f"📊 위협도: {logic.get('threat_level', 0)}/10\n"
            message += f"🏷️ 카테고리: {logic.get('category', 'other')}\n\n"
        
        # 매칭 정보가 있으면 추가
        if 'match_info' in alert:
            match = alert['match_info']
            message += f"**🔗 매칭 정보**\n"
            message += f"확신도: {match.get('match_confidence', 0):.0%}\n"
            if 'attack' in match:
                message += f"공격: {match['attack']['core_argument'][:50]}...\n"
            if 'defense' in match:
                message += f"방어: {match['defense']['core_argument'][:50]}...\n"
            message += "\n"
        
        # 공격/방어 직접 정보
        if 'attack_info' in alert and 'defense_info' in alert:
            message += "**⚔️ 공격-방어 매칭**\n"
            message += f"🔴 공격: {alert['attack_info']['core_argument'][:80]}...\n"
            message += f"🛡️ 방어: {alert['defense_info']['core_argument'][:80]}...\n"
            
            # 매칭 확신도
            metadata = alert.get('metadata', {})
            if metadata.get('confidence'):
                message += f"🎯 매칭도: {metadata['confidence']:.0%}\n"
            message += "\n"
        
        # 기본 메시지 내용
        if alert.get('message'):
            # 기존 메시지가 이미 포맷팅되어 있으면 그대로 사용
            if '공격:' in alert['message'] or '방어:' in alert['message']:
                message += alert['message']
            else:
                message += f"**상세 내용**\n{alert['message']}\n"
        
        # 알림 타입별 추가 정보
        alert_type = alert.get('alert_type', '')
        if alert_type == 'instant_match':
            message += "\n💡 **즉시 대응 가능**: 기존 방어 논리를 활용하세요"
        elif alert_type == 'auto_match':
            message += "\n🤖 **자동 매칭 완료**: AI가 최적 대응을 찾았습니다"
        elif alert_type == 'new_attack':
            message += "\n⚠️ **새로운 공격 감지**: 대응 준비가 필요합니다"
        
        # 원문 링크
        if alert.get('logic_info', {}).get('original_url'):
            message += f"\n\n🔗 [원문 보기]({alert['logic_info']['original_url']})"
        
        # 시간 정보
        created_at = alert.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                kst = dt + timedelta(hours=9)
                message += f"\n\n⏰ {kst.strftime('%Y-%m-%d %H:%M')} KST"
            except:
                pass
        
        # 해시태그
        tags = []
        if severity == 'critical':
            tags.append('#긴급')
        if alert_type:
            tags.append(f'#{alert_type}')
        if 'logic_info' in alert:
            tags.append(f"#{alert['logic_info'].get('category', 'other')}")
        
        if tags:
            message += f"\n\n{' '.join(tags)}"
        
        return message

    async def send_telegram_alert(self, alert: Dict):
        """텔레그램으로 알림 발송"""
        try:
            # 이미 처리한 알림인지 확인
            alert_id = alert.get('id')
            if alert_id in self.processed_alerts:
                return
            
            # 논리 정보 추가
            enriched_alert = await self.enrich_alert_with_logic_info(alert)
            
            # 메시지 포맷팅
            message = self.format_telegram_message(enriched_alert)
            
            # 텔레그램 발송
            await self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            
            # 발송 완료 표시
            self.supabase.table('alerts').update({
                'sent_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', alert_id).execute()
            
            self.processed_alerts.add(alert_id)
            
            logger.info(f"✅ Alert sent: {alert.get('title', 'No title')[:50]}")
            
            # 높은 우선순위 알림 간 간격
            if alert.get('severity') in ['critical', 'high']:
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Error sending telegram alert: {str(e)}")
            
            # 재시도를 위해 에러 기록
            if alert.get('id'):
                self.supabase.table('alerts').update({
                    'metadata': {
                        **alert.get('metadata', {}),
                        'send_error': str(e),
                        'retry_count': alert.get('metadata', {}).get('retry_count', 0) + 1
                    }
                }).eq('id', alert['id']).execute()

    async def process_alerts(self):
        """알림 처리 메인 루프"""
        logger.info("🚀 Starting Alert Sender v2.0...")
        
        while True:
            try:
                # 대기 중인 알림 가져오기
                pending_alerts = await self.get_pending_alerts()
                
                if pending_alerts:
                    logger.info(f"📬 Found {len(pending_alerts)} pending alerts")
                    
                    for alert in pending_alerts:
                        await self.send_telegram_alert(alert)
                    
                    logger.info(f"✅ Processed {len(pending_alerts)} alerts")
                
                # 다음 체크까지 대기
                await asyncio.sleep(30)  # 30초마다 체크
                
            except KeyboardInterrupt:
                logger.info("Stopping alert sender...")
                break
            except Exception as e:
                logger.error(f"Error in alert processing loop: {str(e)}")
                await asyncio.sleep(60)  # 에러 시 1분 대기

    async def send_test_alert(self):
        """테스트 알림 발송"""
        test_alert = {
            'id': 'test-' + datetime.now().isoformat(),
            'severity': 'high',
            'title': '🧪 Logic Defense System v2.0 테스트',
            'message': '시스템이 정상 작동 중입니다.',
            'alert_type': 'test',
            'metadata': {
                'test': True,
                'version': '2.0'
            },
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        await self.send_telegram_alert(test_alert)
        logger.info("Test alert sent successfully")


async def main():
    """메인 실행 함수"""
    
    # 환경변수 체크
    if not all([SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        logger.error("Missing required environment variables")
        return
    
    sender = AlertSenderV2()
    
    # 테스트 모드 체크
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        await sender.send_test_alert()
    else:
        # 정상 실행
        await sender.process_alerts()


if __name__ == "__main__":
    asyncio.run(main())
