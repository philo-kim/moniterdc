'use client'

import React, { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import {
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  ExternalLink,
  Send,
  Award,
  Link as LinkIcon,
  AlertCircle
} from 'lucide-react'

interface AttackLogic {
  id: string
  core_argument: string
  keywords: string[]
  threat_level: number
  created_at: string
  original_url?: string
  original_title?: string
  original_content?: string
  context_issue?: string
  distortion_pattern?: string
  counter_count?: number
}

interface CounterArgument {
  id: string
  content: string
  source_type: 'article' | 'video' | 'tweet' | 'text' | 'other'
  source_url?: string
  author_name: string
  upvotes: number
  downvotes: number
  quality_score: number
  is_best: boolean
  is_verified: boolean
  created_at: string
}

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export default function AttacksWithComments() {
  const [attacks, setAttacks] = useState<AttackLogic[]>([])
  const [selectedAttack, setSelectedAttack] = useState<AttackLogic | null>(null)
  const [counters, setCounters] = useState<CounterArgument[]>([])
  const [relatedLogics, setRelatedLogics] = useState<AttackLogic[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // 새 댓글 입력 상태
  const [newComment, setNewComment] = useState({
    content: '',
    source_type: 'text' as const,
    source_url: '',
    author_name: ''
  })

  // 투표한 댓글 ID 저장 (로컬스토리지)
  const [votedComments, setVotedComments] = useState<Record<string, 1 | -1>>({})

  useEffect(() => {
    // 로컬스토리지에서 투표 기록 불러오기
    const stored = localStorage.getItem('voted_comments')
    if (stored) {
      setVotedComments(JSON.parse(stored))
    }
    fetchAttacks()
  }, [])

  const fetchAttacks = async () => {
    setIsLoading(true)
    try {
      const { data, error } = await supabase
        .from('attack_logic_with_counters')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50)

      if (error) throw error
      setAttacks(data || [])
    } catch (error) {
      console.error('Error fetching attacks:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchCounters = async (attackId: string) => {
    try {
      const { data, error } = await supabase.rpc('get_counter_arguments_for_attack', {
        p_attack_id: attackId,
        p_limit: 100
      })

      if (error) throw error
      setCounters(data || [])
    } catch (error) {
      console.error('Error fetching counters:', error)
    }
  }

  const fetchRelatedLogics = async (attackId: string) => {
    try {
      // 선택된 공격의 벡터 임베딩을 가져와서 유사한 논리 검색
      const { data: currentAttack } = await supabase
        .from('logic_repository')
        .select('vector_embedding')
        .eq('id', attackId)
        .single()

      if (currentAttack?.vector_embedding) {
        const { data, error } = await supabase.rpc('find_similar_logic', {
          query_embedding: currentAttack.vector_embedding,
          match_threshold: 0.7,
          match_count: 5,
          logic_type_filter: 'attack'
        })

        if (error) throw error
        // 자기 자신 제외
        setRelatedLogics((data || []).filter((logic: any) => logic.id !== attackId))
      }
    } catch (error) {
      console.error('Error fetching related logics:', error)
    }
  }

  const handleAttackClick = (attack: AttackLogic) => {
    setSelectedAttack(attack)
    fetchCounters(attack.id)
    fetchRelatedLogics(attack.id)
  }

  const handleSubmitComment = async () => {
    if (!selectedAttack || !newComment.content.trim()) return

    try {
      const { error } = await supabase
        .from('counter_arguments')
        .insert({
          attack_id: selectedAttack.id,
          content: newComment.content,
          source_type: newComment.source_type,
          source_url: newComment.source_url || null,
          author_name: newComment.author_name || 'Anonymous'
        })

      if (error) throw error

      // 성공 시 초기화 및 새로고침
      setNewComment({ content: '', source_type: 'text', source_url: '', author_name: '' })
      fetchCounters(selectedAttack.id)
      fetchAttacks() // counter_count 업데이트
    } catch (error) {
      console.error('Error submitting comment:', error)
      alert('댓글 작성 실패: ' + error)
    }
  }

  const handleVote = async (counterId: string, voteType: 1 | -1) => {
    // 고유 식별자 (IP 대신 브라우저 fingerprint)
    const voterId = localStorage.getItem('voter_id') || crypto.randomUUID()
    if (!localStorage.getItem('voter_id')) {
      localStorage.setItem('voter_id', voterId)
    }

    try {
      const { data, error } = await supabase.rpc('vote_counter_argument', {
        p_counter_argument_id: counterId,
        p_voter_identifier: voterId,
        p_vote_type: voteType
      })

      if (error) throw error

      // 투표 기록 업데이트
      const newVotes = { ...votedComments }
      if (data.action === 'removed') {
        delete newVotes[counterId]
      } else {
        newVotes[counterId] = voteType
      }
      setVotedComments(newVotes)
      localStorage.setItem('voted_comments', JSON.stringify(newVotes))

      // 댓글 목록 새로고침
      if (selectedAttack) {
        fetchCounters(selectedAttack.id)
      }
    } catch (error) {
      console.error('Error voting:', error)
    }
  }

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'article': return '📰'
      case 'video': return '🎥'
      case 'tweet': return '🐦'
      default: return '💬'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-400">로딩 중...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">🎯 공격 논리 모니터링</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 좌측: 공격 논리 목록 */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">최근 공격 논리 ({attacks.length})</h2>

            {attacks.map((attack) => (
              <div
                key={attack.id}
                onClick={() => handleAttackClick(attack)}
                className={`p-4 rounded-lg cursor-pointer transition-all ${
                  selectedAttack?.id === attack.id
                    ? 'bg-red-900/30 border-2 border-red-500'
                    : 'bg-gray-800 hover:bg-gray-700'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className="font-medium">{attack.core_argument}</p>
                    <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                      <span className={`px-2 py-1 rounded ${
                        attack.threat_level >= 8 ? 'bg-red-600' :
                        attack.threat_level >= 5 ? 'bg-yellow-600' : 'bg-gray-600'
                      }`}>
                        위협도 {attack.threat_level}
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageSquare size={14} />
                        {attack.counter_count || 0}개 대응
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 mt-2">
                  {attack.keywords?.slice(0, 5).map((keyword, i) => (
                    <span key={i} className="text-xs px-2 py-1 bg-gray-700 rounded">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* 우측: 댓글 (대응 논리) */}
          <div className="space-y-4">
            {selectedAttack ? (
              <>
                {/* 원본 게시글 맥락 */}
                <div className="bg-gray-800 p-4 rounded-lg mb-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-yellow-500">📋 원본 게시글 맥락</h3>
                    {selectedAttack.original_url && (
                      <a
                        href={selectedAttack.original_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1"
                      >
                        <ExternalLink size={14} />
                        원문 보기
                      </a>
                    )}
                  </div>

                  {selectedAttack.original_title && (
                    <p className="text-sm font-medium mb-2 text-gray-300">
                      제목: {selectedAttack.original_title}
                    </p>
                  )}

                  {selectedAttack.original_content && (
                    <div className="bg-gray-900 p-3 rounded text-xs text-gray-400 max-h-40 overflow-y-auto">
                      {selectedAttack.original_content}
                    </div>
                  )}

                  <div className="mt-3 pt-3 border-t border-gray-700 space-y-2">
                    <p className="text-sm text-red-400">
                      <span className="font-semibold">🎯 AI 분석 핵심 논리:</span> {selectedAttack.core_argument}
                    </p>

                    {selectedAttack.context_issue && (
                      <p className="text-sm text-blue-400">
                        <span className="font-semibold">📰 관련 이슈:</span> {selectedAttack.context_issue}
                      </p>
                    )}

                    {selectedAttack.distortion_pattern && (
                      <p className="text-sm text-orange-400">
                        <span className="font-semibold">⚠️ 왜곡 패턴:</span> {selectedAttack.distortion_pattern}
                      </p>
                    )}
                  </div>
                </div>

                <div className="bg-gray-800 p-4 rounded-lg sticky top-6">
                  <h2 className="text-xl font-semibold mb-2">대응 논리 작성</h2>

                  {/* 새 댓글 작성 */}
                  <div className="space-y-3 mb-4">
                    <textarea
                      value={newComment.content}
                      onChange={(e) => setNewComment({ ...newComment, content: e.target.value })}
                      placeholder="대응 논리를 작성하거나, 기사/영상 링크를 공유하세요..."
                      className="w-full bg-gray-700 text-white rounded p-3 text-sm resize-none"
                      rows={4}
                    />

                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        value={newComment.source_url}
                        onChange={(e) => setNewComment({ ...newComment, source_url: e.target.value })}
                        placeholder="링크 (선택)"
                        className="bg-gray-700 text-white rounded px-3 py-2 text-sm"
                      />
                      <input
                        type="text"
                        value={newComment.author_name}
                        onChange={(e) => setNewComment({ ...newComment, author_name: e.target.value })}
                        placeholder="이름 (선택)"
                        className="bg-gray-700 text-white rounded px-3 py-2 text-sm"
                      />
                    </div>

                    <select
                      value={newComment.source_type}
                      onChange={(e) => setNewComment({ ...newComment, source_type: e.target.value as any })}
                      className="bg-gray-700 text-white rounded px-3 py-2 text-sm w-full"
                    >
                      <option value="text">직접 작성</option>
                      <option value="article">기사</option>
                      <option value="video">영상</option>
                      <option value="tweet">트윗</option>
                      <option value="other">기타</option>
                    </select>

                    <button
                      onClick={handleSubmitComment}
                      disabled={!newComment.content.trim()}
                      className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600
                               disabled:cursor-not-allowed rounded px-4 py-2 flex items-center
                               justify-center gap-2 transition-colors"
                    >
                      <Send size={16} />
                      작성
                    </button>
                  </div>
                </div>

                {/* 관련 논리 (RAG 유사도 분석) */}
                {relatedLogics.length > 0 && (
                  <div className="bg-gray-800 p-4 rounded-lg mb-4">
                    <h3 className="text-lg font-semibold text-purple-500 mb-3">🔗 유사한 공격 논리들</h3>
                    <p className="text-xs text-gray-400 mb-3">
                      벡터 유사도 분석으로 찾은 관련 논리 (같은 맥락/패턴)
                    </p>
                    <div className="space-y-2">
                      {relatedLogics.map((logic) => (
                        <div
                          key={logic.id}
                          onClick={() => handleAttackClick(logic)}
                          className="bg-gray-900 p-3 rounded text-sm cursor-pointer hover:bg-gray-700 transition-colors"
                        >
                          <p className="text-gray-300">{logic.core_argument}</p>
                          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                            <span className={`px-2 py-1 rounded ${
                              logic.threat_level >= 8 ? 'bg-red-600' :
                              logic.threat_level >= 5 ? 'bg-yellow-600' : 'bg-gray-600'
                            }`}>
                              위협도 {logic.threat_level}
                            </span>
                            {logic.keywords?.slice(0, 3).map((kw, i) => (
                              <span key={i} className="text-gray-500">{kw}</span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 댓글 목록 */}
                <div className="space-y-3">
                  {counters.length === 0 ? (
                    <div className="text-center text-gray-400 py-8">
                      <AlertCircle className="mx-auto mb-2" size={24} />
                      <p>아직 대응 논리가 없습니다.</p>
                      <p className="text-sm mt-1">첫 번째 대응을 작성해보세요!</p>
                    </div>
                  ) : (
                    counters.map((counter) => (
                      <div
                        key={counter.id}
                        className={`p-4 rounded-lg ${
                          counter.is_best ? 'bg-yellow-900/20 border-2 border-yellow-500' : 'bg-gray-800'
                        }`}
                      >
                        {counter.is_best && (
                          <div className="flex items-center gap-1 text-yellow-500 mb-2 text-sm">
                            <Award size={16} />
                            <span className="font-semibold">베스트 대응</span>
                          </div>
                        )}

                        <div className="flex items-start gap-2 mb-2">
                          <span className="text-2xl">{getSourceIcon(counter.source_type)}</span>
                          <div className="flex-1">
                            <p className="text-sm leading-relaxed">{counter.content}</p>

                            {counter.source_url && (
                              <a
                                href={counter.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-400 hover:text-blue-300 text-xs flex items-center gap-1 mt-2"
                              >
                                <LinkIcon size={12} />
                                링크 보기
                              </a>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center justify-between text-sm text-gray-400 mt-3">
                          <span>{counter.author_name}</span>

                          <div className="flex items-center gap-3">
                            <span className="text-yellow-500">점수: {counter.quality_score.toFixed(1)}</span>

                            <button
                              onClick={() => handleVote(counter.id, 1)}
                              className={`flex items-center gap-1 ${
                                votedComments[counter.id] === 1 ? 'text-green-500' : 'text-gray-400 hover:text-green-500'
                              }`}
                            >
                              <ThumbsUp size={14} />
                              {counter.upvotes}
                            </button>

                            <button
                              onClick={() => handleVote(counter.id, -1)}
                              className={`flex items-center gap-1 ${
                                votedComments[counter.id] === -1 ? 'text-red-500' : 'text-gray-400 hover:text-red-500'
                              }`}
                            >
                              <ThumbsDown size={14} />
                              {counter.downvotes}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
            ) : (
              <div className="text-center text-gray-400 py-20">
                <MessageSquare className="mx-auto mb-4" size={48} />
                <p>좌측에서 공격 논리를 선택하세요</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}