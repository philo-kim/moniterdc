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
  AlertCircle,
  TrendingUp,
  Clock,
  FileText
} from 'lucide-react'

interface Logic {
  id: string
  core_argument: string
  keywords: string[]
  threat_level: number
  distortion_pattern?: string
  original_title?: string
  original_content?: string
  original_url?: string
  created_at: string
}

interface Cluster {
  cluster_id: string
  cluster_name: string
  political_frame?: string
  context_issue: string
  common_distortion_pattern?: string
  logic_count: number
  threat_level_avg: number
  first_seen: string
  last_seen: string
  logics: Logic[]
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
  created_at: string
}

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export default function ClustersView() {
  const [clusters, setClusters] = useState<Cluster[]>([])
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null)
  const [selectedLogic, setSelectedLogic] = useState<Logic | null>(null)
  const [counters, setCounters] = useState<CounterArgument[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // 새 댓글 입력
  const [newComment, setNewComment] = useState({
    content: '',
    source_type: 'text' as const,
    source_url: '',
    author_name: ''
  })

  // 투표 기록
  const [votedComments, setVotedComments] = useState<Record<string, 1 | -1>>({})

  useEffect(() => {
    const stored = localStorage.getItem('voted_comments')
    if (stored) {
      setVotedComments(JSON.parse(stored))
    }
    fetchClusters()
  }, [])

  const fetchClusters = async () => {
    setIsLoading(true)
    try {
      const { data, error } = await supabase
        .from('cluster_with_logics')
        .select('*')
        .order('last_seen', { ascending: false })

      if (error) throw error
      setClusters(data || [])
    } catch (error) {
      console.error('Error fetching clusters:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchCounters = async (logicId: string) => {
    try {
      const { data, error } = await supabase.rpc('get_counter_arguments_for_attack', {
        p_attack_id: logicId,
        p_limit: 100
      })

      if (error) throw error
      setCounters(data || [])
    } catch (error) {
      console.error('Error fetching counters:', error)
    }
  }

  const handleClusterClick = (cluster: Cluster) => {
    setSelectedCluster(cluster)
    setSelectedLogic(null)
    setCounters([])
  }

  const handleLogicClick = (logic: Logic) => {
    setSelectedLogic(logic)
    fetchCounters(logic.id)
  }

  const handleSubmitComment = async () => {
    if (!selectedLogic || !newComment.content.trim()) return

    try {
      const { error } = await supabase
        .from('counter_arguments')
        .insert({
          attack_id: selectedLogic.id,
          content: newComment.content,
          source_type: newComment.source_type,
          source_url: newComment.source_url || null,
          author_name: newComment.author_name || 'Anonymous'
        })

      if (error) throw error

      setNewComment({ content: '', source_type: 'text', source_url: '', author_name: '' })
      fetchCounters(selectedLogic.id)
    } catch (error) {
      console.error('Error submitting comment:', error)
      alert('댓글 작성 실패: ' + error)
    }
  }

  const handleVote = async (counterId: string, voteType: 1 | -1) => {
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

      const newVotes = { ...votedComments }
      if (data.action === 'removed') {
        delete newVotes[counterId]
      } else {
        newVotes[counterId] = voteType
      }
      setVotedComments(newVotes)
      localStorage.setItem('voted_comments', JSON.stringify(newVotes))

      if (selectedLogic) {
        fetchCounters(selectedLogic.id)
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
        <h1 className="text-3xl font-bold mb-6">🔍 논리 맥락 분석 시스템</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 좌측: 클러스터 목록 (이슈별) */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">📊 이슈별 논리 클러스터 ({clusters.length})</h2>

            {clusters.map((cluster) => (
              <div
                key={cluster.cluster_id}
                onClick={() => handleClusterClick(cluster)}
                className={`p-4 rounded-lg cursor-pointer transition-all ${
                  selectedCluster?.cluster_id === cluster.cluster_id
                    ? 'bg-purple-900/30 border-2 border-purple-500'
                    : 'bg-gray-800 hover:bg-gray-700'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    {/* 정치적 프레임 (메인) */}
                    <h3 className="font-bold text-lg text-red-400 mb-1">
                      🎯 {cluster.political_frame || cluster.cluster_name}
                    </h3>

                    {/* 구체적 이슈들 */}
                    {cluster.context_issue && (
                      <p className="text-sm text-gray-400 mb-2">
                        📌 {cluster.context_issue}
                      </p>
                    )}

                    <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                      <span className="flex items-center gap-1">
                        <FileText size={14} />
                        {cluster.logic_count}개 논리
                      </span>
                      <span className={`px-2 py-1 rounded ${
                        cluster.threat_level_avg >= 8 ? 'bg-red-600' :
                        cluster.threat_level_avg >= 5 ? 'bg-yellow-600' : 'bg-gray-600'
                      }`}>
                        평균 위협도 {cluster.threat_level_avg.toFixed(1)}
                      </span>
                    </div>
                  </div>
                </div>

                {cluster.common_distortion_pattern && (
                  <p className="text-xs text-orange-400 mt-2">
                    ⚠️ {cluster.common_distortion_pattern}
                  </p>
                )}

                <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                  <Clock size={12} />
                  최근: {new Date(cluster.last_seen).toLocaleDateString('ko-KR')}
                </div>
              </div>
            ))}
          </div>

          {/* 중앙: 선택된 클러스터의 논리들 (시간순) */}
          <div className="space-y-4">
            {selectedCluster ? (
              <>
                <div className="bg-gray-800 p-4 rounded-lg sticky top-6">
                  <h2 className="text-xl font-bold mb-2 text-red-400">
                    🎯 {selectedCluster.political_frame || selectedCluster.cluster_name}
                  </h2>
                  {selectedCluster.context_issue && (
                    <p className="text-sm text-gray-400 mb-2">
                      📌 관련 이슈: {selectedCluster.context_issue}
                    </p>
                  )}
                  <p className="text-sm text-gray-400">
                    {selectedCluster.logic_count}개의 논리가 시간순으로 정렬됨
                  </p>
                  {selectedCluster.common_distortion_pattern && (
                    <p className="text-sm text-orange-400 mt-2">
                      ⚠️ 공통 패턴: {selectedCluster.common_distortion_pattern}
                    </p>
                  )}
                </div>

                {/* 논리 목록 (시간순) */}
                <div className="space-y-3">
                  {selectedCluster.logics.map((logic, index) => (
                    <div
                      key={logic.id}
                      onClick={() => handleLogicClick(logic)}
                      className={`p-4 rounded-lg cursor-pointer transition-all ${
                        selectedLogic?.id === logic.id
                          ? 'bg-blue-900/30 border-2 border-blue-500'
                          : 'bg-gray-800 hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-start gap-2 mb-2">
                        <span className="text-xs text-gray-500">#{index + 1}</span>
                        <div className="flex-1">
                          <p className="text-sm font-medium">{logic.core_argument}</p>
                          <div className="flex items-center gap-2 mt-2 text-xs text-gray-400">
                            <span className={`px-2 py-1 rounded ${
                              logic.threat_level >= 8 ? 'bg-red-600' :
                              logic.threat_level >= 5 ? 'bg-yellow-600' : 'bg-gray-600'
                            }`}>
                              위협도 {logic.threat_level}
                            </span>
                            <Clock size={12} />
                            {new Date(logic.created_at).toLocaleString('ko-KR', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </div>
                        </div>
                      </div>

                      {logic.distortion_pattern && (
                        <p className="text-xs text-orange-400 mt-2">
                          왜곡: {logic.distortion_pattern}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center text-gray-400 py-20">
                <TrendingUp className="mx-auto mb-4" size={48} />
                <p>좌측에서 이슈/맥락을 선택하세요</p>
              </div>
            )}
          </div>

          {/* 우측: 선택된 논리의 상세 + 대응 */}
          <div className="space-y-4">
            {selectedLogic ? (
              <>
                {/* 원본 게시글 */}
                <div className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-yellow-500">📋 원본 게시글</h3>
                    {selectedLogic.original_url && (
                      <a
                        href={selectedLogic.original_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1"
                      >
                        <ExternalLink size={14} />
                        원문
                      </a>
                    )}
                  </div>

                  {selectedLogic.original_title && (
                    <p className="text-sm font-medium mb-2 text-gray-300">
                      {selectedLogic.original_title}
                    </p>
                  )}

                  {selectedLogic.original_content && (
                    <div className="bg-gray-900 p-3 rounded text-xs text-gray-400 max-h-40 overflow-y-auto">
                      {selectedLogic.original_content}
                    </div>
                  )}

                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <p className="text-sm text-red-400">
                      <span className="font-semibold">🎯 핵심:</span> {selectedLogic.core_argument}
                    </p>
                  </div>
                </div>

                {/* 대응 논리 작성 */}
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3">💬 대응 작성</h3>

                  <div className="space-y-3">
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

                {/* 대응 댓글 목록 */}
                <div className="space-y-3">
                  {counters.length === 0 ? (
                    <div className="text-center text-gray-400 py-8 bg-gray-800 rounded-lg">
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
                <p>중앙에서 논리를 선택하세요</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}