"""
LangChain RAG System for Logic Defense
이 시스템은 정치 논리 분석 및 매칭을 위한 RAG(Retrieval Augmented Generation)을 구현합니다.
"""

import os
import asyncio
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from dotenv import load_dotenv
import logging

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage

from supabase import create_client, Client
from pydantic import BaseModel, Field

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class LogicAnalysisResult(BaseModel):
    """논리 분석 결과 스키마"""
    core_argument: str = Field(description="핵심 논리를 한 문장으로")
    keywords: List[str] = Field(description="주요 키워드 3-5개")
    ai_classification: str = Field(description="공격적/방어적/중립적")
    evidence_quality: int = Field(description="증거 품질 점수 (1-10)")
    threat_level: int = Field(description="위협 수준 (1-10)")
    effectiveness_score: int = Field(description="효과성 점수 (1-10)")
    counter_strategies: List[str] = Field(description="대응 전략 2-3개")

class RAGLogicSystem:
    """LangChain 기반 논리 분석 및 매칭 시스템"""
    
    def __init__(self):
        """시스템 초기화"""
        # Supabase 클라이언트
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # OpenAI 임베딩 모델 (최신 모델 사용)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=OPENAI_API_KEY
        )
        
        # LLM 모델 설정 (GPT-4o 사용, GPT-5는 아직 없음)
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            openai_api_key=OPENAI_API_KEY
        )
        
        # 벡터 스토어는 나중에 초기화 (테이블 스키마 문제로 인해)
        self.vector_store = None
        
        # 텍스트 분할기
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "]
        )
        
        # RAG 체인 초기화
        self.rag_chain = self._init_rag_chain()
        
        # 분석 체인 초기화
        self.analysis_chain = self._init_analysis_chain()
        
        logger.info("RAG Logic System initialized successfully")
    
    def _init_vector_store(self) -> SupabaseVectorStore:
        """Supabase 벡터 스토어 초기화"""
        return SupabaseVectorStore(
            client=self.supabase,
            embedding=self.embeddings,
            table_name="logic_repository",
            query_name="match_logic_documents",
            chunk_size=500
        )
    
    def _init_analysis_chain(self):
        """논리 분석 체인 초기화"""
        
        # JSON 출력 파서
        output_parser = JsonOutputParser(pydantic_object=LogicAnalysisResult)
        
        # 프롬프트 템플릿
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 정치 논리 분석 전문가입니다. 
            주어진 텍스트를 분석하여 핵심 논리를 추출하고, 공격/방어 성향을 판단하며, 
            효과적인 대응 전략을 제시해야 합니다.
            
            분석 기준:
            1. 핵심 논리: 글의 중심 주장을 한 문장으로 요약
            2. 키워드: 핵심 개념이나 인물, 사건 등 3-5개
            3. 분류: 공격적(비판/공격), 방어적(옹호/변호), 중립적(정보/분석)
            4. 증거 품질: 사실 기반 정도 (1-10)
            5. 위협 수준: 정치적 파급력 (1-10)
            6. 효과성: 논리의 설득력 (1-10)
            7. 대응 전략: 이 논리에 대응하는 2-3가지 전략
            
            {format_instructions}"""),
            ("human", "{text}")
        ])
        
        # 체인 구성 - format_instructions 자동 추가
        chain = (
            RunnablePassthrough.assign(
                format_instructions=lambda x: output_parser.get_format_instructions()
            )
            | prompt
            | self.llm
            | output_parser
        )

        return chain
    
    def _init_rag_chain(self):
        """RAG 체인 초기화"""
        
        # 컨텍스트 검색을 위한 프롬프트
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", """주어진 대화 기록과 최신 사용자 질문을 바탕으로,
            독립적으로 이해될 수 있는 질문을 재구성하세요.
            대화 기록이 관련이 없다면 원래 질문을 그대로 사용하세요."""),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        # 답변 생성 프롬프트
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 정치 논리 대응 전문가입니다.
            
            검색된 컨텍스트를 바탕으로 질문에 답변하세요.
            컨텍스트에는 과거 유사한 논리들과 그에 대한 성공적인 대응 사례가 포함되어 있습니다.
            
            답변 시 다음을 포함하세요:
            1. 유사한 과거 사례 언급
            2. 효과적인 대응 논리
            3. 구체적인 실행 방안
            4. 예상 반응과 추가 대응
            
            컨텍스트:
            {context}"""),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        # 리트리버 생성
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # History-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )
        
        # Document chain
        question_answer_chain = create_stuff_documents_chain(
            self.llm, qa_prompt
        )
        
        # RAG chain
        rag_chain = create_retrieval_chain(
            history_aware_retriever, 
            question_answer_chain
        )
        
        return rag_chain
    
    async def analyze_logic(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        텍스트의 논리를 분석하고 벡터 DB에 저장
        
        Args:
            text: 분석할 텍스트
            metadata: 추가 메타데이터 (출처, 작성자 등)
        
        Returns:
            분석 결과 딕셔너리
        """
        try:
            # 1. 텍스트 분석
            analysis_result = await self.analysis_chain.ainvoke({"text": text})
            
            # 2. 문서 생성
            doc_content = f"""
            핵심 논리: {analysis_result['core_argument']}
            키워드: {', '.join(analysis_result['keywords'])}
            원문: {text[:500]}...
            """
            
            document = Document(
                page_content=doc_content,
                metadata={
                    **metadata,
                    **analysis_result,
                    "analyzed_at": datetime.now(timezone.utc).isoformat(),
                    "original_text": text
                }
            )
            
            # 3. 벡터 DB에 저장
            ids = await self.vector_store.aadd_documents([document])
            
            # 4. Supabase 테이블에도 저장
            logic_data = {
                "logic_type": metadata.get("logic_type", "unknown"),
                "source_gallery": metadata.get("source_gallery"),
                "core_argument": analysis_result["core_argument"],
                "keywords": analysis_result["keywords"],
                "ai_classification": analysis_result["ai_classification"],
                "evidence_quality": analysis_result["evidence_quality"],
                "threat_level": analysis_result["threat_level"],
                "effectiveness_score": analysis_result["effectiveness_score"],
                "original_content": text,
                "original_url": metadata.get("url"),
                "is_active": True
            }
            
            result = self.supabase.table('logic_repository').insert(logic_data).execute()
            
            logger.info(f"Logic analyzed and stored: {analysis_result['core_argument'][:50]}...")
            
            return {
                "analysis": analysis_result,
                "vector_id": ids[0] if ids else None,
                "db_id": result.data[0]['id'] if result.data else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing logic: {e}")
            raise
    
    async def find_counter_logic(
        self, 
        attack_text: str, 
        chat_history: List = None
    ) -> Dict[str, Any]:
        """
        공격 논리에 대한 방어 논리를 찾고 대응 전략 생성
        
        Args:
            attack_text: 공격 논리 텍스트
            chat_history: 대화 기록 (선택사항)
        
        Returns:
            대응 논리와 전략
        """
        try:
            # 대화 기록 준비
            if chat_history is None:
                chat_history = []
            
            # RAG 체인 실행
            response = await self.rag_chain.ainvoke({
                "input": f"""
                다음 공격 논리에 대한 효과적인 대응 방법을 찾아주세요:
                
                {attack_text}
                
                과거 유사한 사례와 성공적인 대응 전략을 참고하여 구체적인 방안을 제시해주세요.
                """,
                "chat_history": chat_history
            })
            
            # 유사 문서 직접 검색
            similar_docs = await self.vector_store.asimilarity_search(
                attack_text,
                k=3,
                filter={"logic_type": "defense"}
            )
            
            return {
                "answer": response["answer"],
                "similar_defenses": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in similar_docs
                ],
                "context_used": response.get("context", [])
            }
            
        except Exception as e:
            logger.error(f"Error finding counter logic: {e}")
            raise
    
    async def update_effectiveness(
        self, 
        logic_id: str, 
        success: bool, 
        feedback: str = None
    ):
        """
        논리의 효과성 점수 업데이트 (실제 사용 결과 반영)
        
        Args:
            logic_id: 논리 ID
            success: 성공 여부
            feedback: 피드백 (선택사항)
        """
        try:
            # 현재 데이터 가져오기
            result = self.supabase.table('logic_repository').select("*").eq('id', logic_id).execute()
            
            if not result.data:
                logger.error(f"Logic not found: {logic_id}")
                return
            
            current_data = result.data[0]
            
            # 사용 횟수 증가
            usage_count = current_data.get('usage_count', 0) + 1
            success_count = current_data.get('success_count', 0) + (1 if success else 0)
            
            # 효과성 점수 재계산 (베이지안 평균)
            base_score = current_data.get('effectiveness_score', 5)
            new_score = ((base_score * 10) + (success_count * 10)) / (10 + usage_count)
            
            # 업데이트
            update_data = {
                'usage_count': usage_count,
                'success_count': success_count,
                'effectiveness_score': min(10, max(1, int(new_score))),
                'last_used_at': datetime.now(timezone.utc).isoformat()
            }
            
            if feedback:
                # 피드백을 별도 테이블에 저장하거나 JSON 필드에 추가
                update_data['feedback'] = feedback
            
            self.supabase.table('logic_repository').update(update_data).eq('id', logic_id).execute()
            
            logger.info(f"Updated effectiveness for logic {logic_id}: {new_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating effectiveness: {e}")
    
    async def batch_process_posts(
        self, 
        posts: List[Dict[str, Any]], 
        logic_type: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """
        여러 게시글을 배치로 처리
        
        Args:
            posts: 게시글 리스트
            logic_type: 논리 타입 (attack/defense)
        
        Returns:
            처리 결과 리스트
        """
        results = []
        
        for post in posts:
            try:
                result = await self.analyze_logic(
                    text=post.get('content', '') or post.get('title', ''),
                    metadata={
                        'logic_type': logic_type,
                        'source_gallery': post.get('gallery_id'),
                        'url': post.get('url'),
                        'author': post.get('author'),
                        'post_id': post.get('id')
                    }
                )
                results.append(result)
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing post {post.get('id')}: {e}")
                continue
        
        return results
    
    async def get_trending_topics(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        최근 트렌딩 토픽 분석
        
        Args:
            days: 분석할 일수
        
        Returns:
            트렌딩 토픽 리스트
        """
        try:
            # 최근 데이터 조회
            from datetime import timedelta
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            result = self.supabase.table('logic_repository') \
                .select("keywords, ai_classification, effectiveness_score") \
                .gte('created_at', cutoff_date) \
                .execute()
            
            # 키워드 집계
            keyword_counts = {}
            for item in result.data:
                for keyword in item.get('keywords', []):
                    if keyword not in keyword_counts:
                        keyword_counts[keyword] = {
                            'count': 0,
                            'avg_effectiveness': 0,
                            'classifications': {}
                        }
                    keyword_counts[keyword]['count'] += 1
                    keyword_counts[keyword]['avg_effectiveness'] += item.get('effectiveness_score', 5)
                    
                    classification = item.get('ai_classification', 'unknown')
                    if classification not in keyword_counts[keyword]['classifications']:
                        keyword_counts[keyword]['classifications'][classification] = 0
                    keyword_counts[keyword]['classifications'][classification] += 1
            
            # 평균 계산 및 정렬
            trending = []
            for keyword, data in keyword_counts.items():
                if data['count'] > 1:  # 최소 2회 이상 언급된 키워드만
                    trending.append({
                        'keyword': keyword,
                        'count': data['count'],
                        'avg_effectiveness': data['avg_effectiveness'] / data['count'],
                        'dominant_classification': max(data['classifications'], key=data['classifications'].get),
                        'trend_score': data['count'] * (data['avg_effectiveness'] / data['count'] / 10)
                    })
            
            # 트렌드 스코어로 정렬
            trending.sort(key=lambda x: x['trend_score'], reverse=True)
            
            return trending[:10]  # 상위 10개
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []

# 싱글톤 인스턴스
_rag_system = None

def get_rag_system() -> RAGLogicSystem:
    """RAG 시스템 싱글톤 인스턴스 반환"""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGLogicSystem()
    return _rag_system

# 테스트 코드
if __name__ == "__main__":
    async def test_rag_system():
        """RAG 시스템 테스트"""
        rag = get_rag_system()
        
        # 테스트 텍스트
        test_attack = """
        현 정부의 경제 정책은 완전히 실패했다. 
        물가는 치솟고 서민들의 삶은 더욱 어려워졌다. 
        이는 무능한 정책 결정의 결과다.
        """
        
        test_defense = """
        글로벌 경제 위기 속에서도 우리나라는 선방하고 있다.
        OECD 국가 중 성장률 상위권을 유지하며,
        고용률도 역대 최고 수준을 기록하고 있다.
        """
        
        # 1. 논리 분석
        print("=== 공격 논리 분석 ===")
        attack_result = await rag.analyze_logic(
            test_attack,
            metadata={'logic_type': 'attack', 'source_gallery': 'test'}
        )
        print(json.dumps(attack_result['analysis'], indent=2, ensure_ascii=False))
        
        print("\n=== 방어 논리 분석 ===")
        defense_result = await rag.analyze_logic(
            test_defense,
            metadata={'logic_type': 'defense', 'source_gallery': 'test'}
        )
        print(json.dumps(defense_result['analysis'], indent=2, ensure_ascii=False))
        
        # 2. 대응 논리 찾기
        print("\n=== 대응 논리 검색 ===")
        counter = await rag.find_counter_logic(test_attack)
        print(f"대응 전략: {counter['answer'][:500]}...")
        
        # 3. 트렌딩 토픽
        print("\n=== 트렌딩 토픽 ===")
        trending = await rag.get_trending_topics(7)
        for topic in trending[:5]:
            print(f"- {topic['keyword']}: {topic['count']}회, 효과성 {topic['avg_effectiveness']:.1f}")
    
    # 실행
    asyncio.run(test_rag_system())
