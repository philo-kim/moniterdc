"""
Telegram Bot Module
실시간 알림 및 상호작용 봇
"""

import os
import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
from dotenv import load_dotenv

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram.constants import ParseMode
from supabase import create_client, Client

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
TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# 알림 설정
ENABLE_TELEGRAM_ALERTS = os.getenv('ENABLE_TELEGRAM_ALERTS', 'true').lower() == 'true'
ALERT_BATCH_INTERVAL = 300  # 5분 (일반 알림 배치 간격)
CRITICAL_ALERT_DELAY = 10   # 10초 (긴급 알림 지연)

# 이모지 매핑
SEVERITY_EMOJI = {
    'critical': '🚨',
    'high': '🔴',
    'medium': '🟡',
    'low': '🔵',
    'info': 'ℹ️'
}

CATEGORY_EMOJI = {
    'policy': '📋',
    'election': '🗳️',
    'scandal': '💣',
    'opinion': '💭',
    'other': '📌'
}


class TelegramAlertBot:
    """텔레그램 알림 봇"""
    
    def __init__(self):
        """봇 초기화"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.bot = self.application.bot
        self.alert_queue = []
        self.is_running = False
        
        # 핸들러 등록
        self._register_handlers()
    
    def _register_handlers(self):
        """명령어 핸들러 등록"""
        # 명령어 핸들러
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("stats", self.cmd_stats))
        self.application.add_handler(CommandHandler("recent", self.cmd_recent))
        self.application.add_handler(CommandHandler("mute", self.cmd_mute))
        self.application.add_handler(CommandHandler("unmute", self.cmd_unmute))
        self.application.add_handler(CommandHandler("cost", self.cmd_cost))
        
        # 콜백 쿼리 핸들러 (인라인 버튼)
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """시작 명령어"""
        welcome_message = """
🎯 *DC갤러리 정치 모니터링 봇*

24시간 정치 갤러리를 모니터링하고 중요 이슈를 실시간으로 알려드립니다.

*주요 기능:*
• 실시간 이슈 감지 및 알림
• AI 기반 중요도 분석
• 감성 및 프레임 분석
• 대응 전략 제안

*명령어:*
/help - 도움말
/status - 시스템 상태
/stats - 통계 정보
/recent - 최근 중요 게시글
/cost - 오늘 API 비용
/mute - 알림 일시 중지
/unmute - 알림 재개

_Powered by GPT-5 Series_
"""
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """도움말 명령어"""
        help_text = """
📚 *도움말*

*알림 레벨:*
🚨 *긴급 (Critical)*: 즉시 대응 필요
🔴 *높음 (High)*: 1시간 내 확인 필요
🟡 *중간 (Medium)*: 당일 확인 권장
🔵 *낮음 (Low)*: 모니터링 대상
ℹ️ *정보 (Info)*: 참고 사항

*알림 설정:*
• 긴급 알림: 즉시 전송
• 중요 알림: 5분 내 전송
• 일반 알림: 30분 배치 전송

*버튼 기능:*
• 📊 상세보기: 전체 분석 결과
• ✅ 확인: 알림 확인 처리
• 🔗 원문: DC갤러리 원문 링크

*문의:* @your_admin_id
"""
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """시스템 상태 확인"""
        try:
            # 최근 크롤링 정보
            recent_posts = self.supabase.table('posts').select('*').order(
                'crawled_at', desc=True
            ).limit(1).execute()
            
            # 대기 중인 작업
            pending_jobs = self.supabase.table('job_queue').select('id').eq(
                'job_status', 'queued'
            ).execute()
            
            # 오늘 알림 수
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
            today_alerts = self.supabase.table('alerts').select('id').gte(
                'created_at', today_start.isoformat()
            ).execute()
            
            # 시스템 상태 메시지
            last_crawl = "Never"
            if recent_posts.data:
                crawl_time = datetime.fromisoformat(recent_posts.data[0]['crawled_at'].replace('Z', '+00:00'))
                time_diff = datetime.now(timezone.utc) - crawl_time
                last_crawl = f"{int(time_diff.total_seconds() / 60)}분 전"
            
            status_message = f"""
📊 *시스템 상태*

🕒 마지막 크롤링: {last_crawl}
📝 대기 중인 분석: {len(pending_jobs.data) if pending_jobs.data else 0}건
🔔 오늘 알림: {len(today_alerts.data) if today_alerts.data else 0}건
✅ 봇 상태: 정상 작동 중

_업데이트: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_
"""
            await update.message.reply_text(
                status_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in status command: {str(e)}")
            await update.message.reply_text("❌ 상태 조회 중 오류가 발생했습니다.")
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """통계 정보"""
        try:
            # 24시간 통계
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            
            # 게시글 통계
            posts_stats = self.supabase.table('posts').select('gallery_type').gte(
                'created_at', yesterday.isoformat()
            ).execute()
            
            # 갤러리별 집계
            gallery_counts = {}
            if posts_stats.data:
                for post in posts_stats.data:
                    gallery = post['gallery_type']
                    gallery_counts[gallery] = gallery_counts.get(gallery, 0) + 1
            
            # 중요 게시글
            important_posts = self.supabase.table('analysis_results').select('*').gte(
                'importance_score', 7
            ).gte(
                'created_at', yesterday.isoformat()
            ).execute()
            
            # 통계 메시지
            stats_message = f"""
📈 *24시간 통계*

*게시글 수집:*
• 민주당: {gallery_counts.get('minjoo', 0)}건
• 국민의힘: {gallery_counts.get('kukmin', 0)}건
• 정치일반: {gallery_counts.get('politics', 0)}건
• *총합:* {sum(gallery_counts.values())}건

*AI 분석:*
• 중요 게시글: {len(important_posts.data) if important_posts.data else 0}건
• 평균 중요도: {sum(p['importance_score'] for p in (important_posts.data or [])) / max(len(important_posts.data or [1]), 1):.1f}/10

_기준: 최근 24시간_
"""
            await update.message.reply_text(
                stats_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in stats command: {str(e)}")
            await update.message.reply_text("❌ 통계 조회 중 오류가 발생했습니다.")
    
    async def cmd_recent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """최근 중요 게시글"""
        try:
            # 최근 중요 게시글 조회
            recent = self.supabase.table('posts').select(
                '*, analysis_results!inner(*)'
            ).gte(
                'analysis_results.importance_score', 7
            ).order(
                'created_at', desc=True
            ).limit(5).execute()
            
            if not recent.data:
                await update.message.reply_text("최근 중요 게시글이 없습니다.")
                return
            
            message = "*🔥 최근 중요 게시글*\n\n"
            
            for post in recent.data:
                analysis = post.get('analysis_results', [{}])[0]
                importance = analysis.get('importance_score', 0)
                sentiment = analysis.get('sentiment_label', 'unknown')
                
                message += f"*{importance}/10* | {post['title'][:30]}{'...' if len(post['title']) > 30 else ''}\n"
                message += f"감성: {sentiment} | 추천: {post['recommends']} | 댓글: {post['comments_count']}\n"
                message += f"[원문 보기]({post['post_url']})\n\n"
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error in recent command: {str(e)}")
            await update.message.reply_text("❌ 조회 중 오류가 발생했습니다.")
    
    async def cmd_cost(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """오늘 API 비용 조회"""
        try:
            today = datetime.now(timezone.utc).date()
            
            # 오늘 총 비용
            total_cost = self.supabase.rpc('get_daily_cost_total', {
                'target_date': str(today)
            }).execute()
            
            # 모델별 비용
            model_costs = self.supabase.table('api_costs').select(
                'model, cost_usd'
            ).eq(
                'date', str(today)
            ).execute()
            
            # 모델별 집계
            model_summary = {}
            if model_costs.data:
                for record in model_costs.data:
                    model = record['model']
                    cost = float(record['cost_usd'])
                    model_summary[model] = model_summary.get(model, 0) + cost
            
            # 비용 메시지
            cost_message = f"""
💰 *오늘 API 비용*

*총 비용:* ${float(total_cost.data or 0):.4f}
*일일 한도:* ${os.getenv('DAILY_COST_LIMIT_USD', '5.0')}

*모델별 비용:*
"""
            for model, cost in model_summary.items():
                cost_message += f"• {model}: ${cost:.4f}\n"
            
            remaining = float(os.getenv('DAILY_COST_LIMIT_USD', '5.0')) - float(total_cost.data or 0)
            cost_message += f"\n*남은 한도:* ${remaining:.4f}"
            
            if remaining < 1:
                cost_message += "\n\n⚠️ *경고: 일일 한도가 거의 소진되었습니다!*"
            
            await update.message.reply_text(
                cost_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in cost command: {str(e)}")
            await update.message.reply_text("❌ 비용 조회 중 오류가 발생했습니다.")
    
    async def cmd_mute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """알림 일시 중지"""
        # 여기서는 간단히 메시지만 표시
        # 실제로는 사용자별 설정을 DB에 저장해야 함
        await update.message.reply_text(
            "🔇 알림이 일시 중지되었습니다.\n/unmute 명령어로 다시 시작할 수 있습니다."
        )
    
    async def cmd_unmute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """알림 재개"""
        await update.message.reply_text(
            "🔊 알림이 재개되었습니다."
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """인라인 버튼 콜백 처리"""
        query = update.callback_query
        await query.answer()
        
        data = query.data.split(':')
        action = data[0]
        
        if action == 'ack':
            # 알림 확인 처리
            alert_id = data[1]
            try:
                self.supabase.table('alerts').update({
                    'acknowledged': True,
                    'acknowledged_by': str(query.from_user.id),
                    'acknowledged_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', alert_id).execute()
                
                await query.edit_message_text(
                    query.message.text + "\n\n✅ _확인 완료_",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error acknowledging alert: {str(e)}")
        
        elif action == 'detail':
            # 상세 정보 표시
            post_id = data[1]
            try:
                result = self.supabase.table('analysis_results').select('*').eq(
                    'post_id', post_id
                ).execute()
                
                if result.data:
                    analysis = result.data[0]
                    detail_text = f"""
📊 *상세 분석 결과*

*감성 점수:* {analysis.get('sentiment_score', 0):.2f}
*감성 레이블:* {analysis.get('sentiment_label', 'unknown')}
*위험도:* {analysis.get('risk_level', 'unknown')}

*키워드:*
{', '.join(analysis.get('keywords', []))}

*카테고리:*
{analysis.get('classification', {}).get('category', 'unknown')}

*전략:*
{json.dumps(analysis.get('strategy_json', {}), indent=2, ensure_ascii=False)[:500]}
"""
                    await self.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=detail_text,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await query.answer("분석 결과를 찾을 수 없습니다.", show_alert=True)
                    
            except Exception as e:
                logger.error(f"Error showing details: {str(e)}")
                await query.answer("오류가 발생했습니다.", show_alert=True)
    
    def format_alert_message(self, alert: Dict) -> tuple[str, Optional[InlineKeyboardMarkup]]:
        """알림 메시지 포맷팅"""
        severity = alert.get('severity', 'info')
        emoji = SEVERITY_EMOJI.get(severity, 'ℹ️')
        
        # 메시지 구성
        message = f"{emoji} *{alert.get('title', 'Unknown')}*\n\n"
        message += alert.get('message', '')
        
        # 인라인 버튼
        keyboard = []
        
        if alert.get('post_id'):
            keyboard.append([
                InlineKeyboardButton("📊 상세보기", callback_data=f"detail:{alert['post_id']}"),
                InlineKeyboardButton("✅ 확인", callback_data=f"ack:{alert.get('id', '')}")
            ])
        
        # URL이 있으면 추가
        metadata = alert.get('metadata', {})
        if metadata:
            post_url = f"https://gall.dcinside.com/board/view/?id={metadata.get('gallery')}&no={metadata.get('post_num')}"
            keyboard.append([
                InlineKeyboardButton("🔗 원문 보기", url=post_url)
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        return message, reply_markup
    
    async def send_alert(self, alert: Dict):
        """단일 알림 전송"""
        try:
            message, reply_markup = self.format_alert_message(alert)
            
            # 대상 채팅방 결정
            chat_id = TELEGRAM_CHAT_ID
            if alert.get('severity') == 'critical':
                # 긴급 알림은 관리자에게도 전송
                if TELEGRAM_ADMIN_CHAT_ID:
                    await self.bot.send_message(
                        chat_id=TELEGRAM_ADMIN_CHAT_ID,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
            
            # 메인 채팅방에 전송
            result = await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # 전송 완료 업데이트
            self.supabase.table('alerts').update({
                'sent_at': datetime.now(timezone.utc).isoformat(),
                'sent_count': alert.get('sent_count', 0) + 1
            }).eq('id', alert['id']).execute()
            
            logger.info(f"Sent {alert.get('severity')} alert: {alert.get('title')}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            return False
    
    async def process_alert_queue(self):
        """알림 큐 처리"""
        while self.is_running:
            try:
                # 미전송 알림 조회
                unsent = self.supabase.table('alerts').select('*').is_(
                    'sent_at', 'null'
                ).order(
                    'severity', desc=False  # critical 먼저
                ).order(
                    'created_at', desc=False
                ).limit(10).execute()
                
                if unsent.data:
                    for alert in unsent.data:
                        severity = alert.get('severity', 'info')
                        
                        # 심각도별 처리
                        if severity == 'critical':
                            # 즉시 전송
                            await self.send_alert(alert)
                            await asyncio.sleep(1)
                        elif severity == 'high':
                            # 5분 내 전송
                            created = datetime.fromisoformat(alert['created_at'].replace('Z', '+00:00'))
                            if (datetime.now(timezone.utc) - created).total_seconds() > 60:
                                await self.send_alert(alert)
                                await asyncio.sleep(2)
                        else:
                            # 배치 큐에 추가
                            self.alert_queue.append(alert)
                
                # 배치 알림 처리
                if len(self.alert_queue) >= 5:  # 5개 이상 쌓이면
                    await self.send_batch_alerts()
                
                await asyncio.sleep(30)  # 30초마다 체크
                
            except Exception as e:
                logger.error(f"Error processing alert queue: {str(e)}")
                await asyncio.sleep(60)
    
    async def send_batch_alerts(self):
        """배치 알림 전송"""
        if not self.alert_queue:
            return
        
        try:
            # 요약 메시지 생성
            summary = f"📋 *알림 요약* ({len(self.alert_queue)}건)\n\n"
            
            for alert in self.alert_queue[:10]:  # 최대 10개
                emoji = SEVERITY_EMOJI.get(alert.get('severity', 'info'), 'ℹ️')
                title = alert.get('title', 'Unknown')[:50]
                summary += f"{emoji} {title}\n"
            
            # 전송
            await self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=summary,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # 개별 알림 상태 업데이트
            for alert in self.alert_queue:
                self.supabase.table('alerts').update({
                    'sent_at': datetime.now(timezone.utc).isoformat(),
                    'sent_count': 1
                }).eq('id', alert['id']).execute()
            
            # 큐 비우기
            self.alert_queue.clear()
            
        except Exception as e:
            logger.error(f"Error sending batch alerts: {str(e)}")
    
    async def start(self):
        """봇 시작"""
        logger.info("Starting Telegram bot...")
        self.is_running = True
        
        # 봇 시작
        await self.application.initialize()
        await self.application.start()
        
        # 알림 처리 태스크 시작
        alert_task = asyncio.create_task(self.process_alert_queue())
        
        # 폴링 시작
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        logger.info("Telegram bot started successfully")
        
        # 대기
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
            self.is_running = False
            alert_task.cancel()
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()


async def main():
    """메인 실행 함수"""
    bot = TelegramAlertBot()
    await bot.start()


if __name__ == "__main__":
    # 환경변수 체크
    if not all([SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        logger.error("Missing required environment variables")
        exit(1)
    
    # 봇 실행
    asyncio.run(main())
