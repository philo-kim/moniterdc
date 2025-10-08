'use client'

import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  ArrowLeft,
  FileText,
  ExternalLink,
  AlertCircle,
  Layers,
  Eye,
  Brain,
  Heart,
  AlertTriangle
} from 'lucide-react'

interface ExplicitClaim {
  subject: string
  predicate: string
  evidence_cited: string
  quote: string
}

interface ReasoningGap {
  from: string
  to: string
  gap: string
}

interface LayeredPerception {
  id: string
  content_id: string
  explicit_claims: ExplicitClaim[]
  implicit_assumptions: string[]
  reasoning_gaps: ReasoningGap[]
  deep_beliefs: string[]
  worldview_hints: string
  created_at: string
}

interface Content {
  id: string
  title: string
  body: string
  source_url: string
  published_at: string | null
  created_at: string
}

interface ParsedFrame {
  priority?: 'high' | 'medium' | 'low'
  category: string
  subcategory: string
  description: string
  metadata?: {
    merged_from?: string[]
    estimated_count?: number
  }
}

function PriorityBadge({ priority }: { priority?: 'high' | 'medium' | 'low' }) {
  if (!priority) return null

  const config = {
    high: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-300',
      label: '긴급 대응 필요'
    },
    medium: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      border: 'border-yellow-300',
      label: '주의 필요'
    },
    low: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      border: 'border-green-300',
      label: '모니터링'
    }
  }

  const style = config[priority]

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold border-2 ${style.bg} ${style.text} ${style.border}`}>
      {style.label}
    </span>
  )
}

export default function WorldviewDetailPage() {
  const params = useParams()
  const id = params.id as string

  const [worldview, setWorldview] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true)
        const res = await fetch(`/api/worldviews/${id}`)
        if (!res.ok) {
          throw new Error('Failed to fetch worldview')
        }
        const data = await res.json()
        setWorldview(data)
        setError(null)
      } catch (err) {
        setError(err as Error)
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [id])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent mb-4"></div>
          <p className="text-slate-600">데이터 로딩 중...</p>
        </div>
      </div>
    )
  }

  if (error || !worldview) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 font-semibold">공격 유형을 불러올 수 없습니다</p>
          <Link href="/" className="text-blue-600 hover:underline mt-2 inline-block">
            목록으로 돌아가기
          </Link>
        </div>
      </div>
    )
  }

  const frame: ParsedFrame = JSON.parse(worldview.frame)
  const layeredPerceptions: LayeredPerception[] = worldview.layered_perceptions || []
  const contents: Content[] = worldview.contents || []

  // Group layered perceptions by content
  const perceptionsByContent = new Map<string, LayeredPerception[]>()
  layeredPerceptions.forEach((lp) => {
    if (lp.content_id) {
      if (!perceptionsByContent.has(lp.content_id)) {
        perceptionsByContent.set(lp.content_id, [])
      }
      perceptionsByContent.get(lp.content_id)!.push(lp)
    }
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          공격 유형 목록으로 돌아가기
        </Link>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-6">
          <div className="mb-4">
            <div className="flex items-center gap-3 mb-4">
              <PriorityBadge priority={frame.priority} />
              <p className="text-sm text-slate-600">{frame.category}</p>
            </div>
            <h1 className="text-3xl font-bold text-slate-900 mb-4">
              {worldview.title}
            </h1>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-lg text-blue-900 leading-relaxed">
              {worldview.description || frame.description}
            </p>
            <div className="mt-3 pt-3 border-t border-blue-300 flex items-center gap-6 text-sm">
              {worldview.core_subject && (
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-blue-700">핵심 대상:</span>
                  <span className="text-blue-900">{worldview.core_subject}</span>
                </div>
              )}
              {worldview.overall_valence && (
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-blue-700">전체 감정:</span>
                  <span className={`px-2 py-0.5 rounded ${
                    worldview.overall_valence === 'negative' ? 'bg-red-100 text-red-800' :
                    worldview.overall_valence === 'positive' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {worldview.overall_valence === 'negative' ? '부정' :
                     worldview.overall_valence === 'positive' ? '긍정' : '중립'}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600">분석된 글</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {layeredPerceptions.length}개
              </p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600">원본 글</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {contents.length}개
              </p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600">통합 전 worldview</p>
              <p className="text-2xl font-bold text-purple-600 mt-1">
                {frame.metadata?.merged_from?.length || 1}개
              </p>
            </div>
          </div>
        </div>

        {/* Source Contents with 3-Layer Analysis */}
        {contents.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="h-5 w-5 text-blue-600" />
              <h2 className="text-xl font-bold text-slate-900">
                원본 글 및 3층 구조 분석 ({contents.length}개)
              </h2>
            </div>
            <p className="text-sm text-slate-600 mb-6">
              이 공격 유형이 발견된 DC Gallery 글들과 3층 심층 분석 결과입니다
            </p>
            <div className="space-y-6">
              {contents.map((content) => {
                const contentPerceptions = perceptionsByContent.get(content.id) || []
                const dateToUse = content.published_at || content.created_at
                const publishedDate = dateToUse
                  ? new Date(dateToUse).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })
                  : '날짜 미상'

                return (
                  <div
                    key={content.id}
                    className="border-2 border-slate-200 rounded-lg p-5 hover:shadow-lg transition-shadow"
                  >
                    {/* Content Header */}
                    <div className="flex items-start justify-between gap-4 mb-4">
                      <div className="flex-1">
                        <h3 className="font-bold text-lg text-slate-900 mb-2">
                          {content.title}
                        </h3>
                        {content.body && (
                          <p className="text-sm text-slate-600 mb-3 line-clamp-2">
                            {content.body.substring(0, 200)}...
                          </p>
                        )}
                        <div className="flex items-center gap-4 text-xs text-slate-500">
                          <span>{publishedDate}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <Layers className="h-3 w-3" />
                            {contentPerceptions.length}개 분석
                          </span>
                        </div>
                      </div>
                      <a
                        href={content.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm font-medium"
                      >
                        <span>원문 보기</span>
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>

                    {/* 3-Layer Analysis */}
                    {contentPerceptions.length > 0 && (
                      <div className="mt-4 pt-4 border-t-2 border-slate-200 space-y-4">
                        {contentPerceptions.slice(0, 1).map((lp, idx) => (
                          <div key={idx} className="space-y-4">
                            {/* Layer 1: Explicit Claims */}
                            {lp.explicit_claims && lp.explicit_claims.length > 0 && (
                              <div className="bg-blue-50 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-3">
                                  <Eye className="h-5 w-5 text-blue-600" />
                                  <h4 className="font-bold text-blue-900">
                                    표면층 (Explicit) - 명시적 주장
                                  </h4>
                                </div>
                                <div className="space-y-3">
                                  {lp.explicit_claims.map((claim, i) => (
                                    <div key={i} className="bg-white rounded p-3">
                                      <div className="font-semibold text-slate-900 mb-1">
                                        {claim.subject}: <span className="font-normal">{claim.predicate}</span>
                                      </div>
                                      {claim.quote && (
                                        <blockquote className="text-sm text-slate-600 italic border-l-2 border-blue-300 pl-3 mt-2">
                                          &ldquo;{claim.quote}&rdquo;
                                        </blockquote>
                                      )}
                                      {claim.evidence_cited && (
                                        <div className="text-xs text-slate-500 mt-2">
                                          근거: {claim.evidence_cited}
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Layer 2: Implicit Assumptions */}
                            {lp.implicit_assumptions && lp.implicit_assumptions.length > 0 && (
                              <div className="bg-orange-50 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-3">
                                  <Brain className="h-5 w-5 text-orange-600" />
                                  <h4 className="font-bold text-orange-900">
                                    암묵층 (Implicit) - 전제하는 사고
                                  </h4>
                                </div>
                                <ul className="space-y-2">
                                  {lp.implicit_assumptions.map((assumption, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-orange-900">
                                      <span className="text-orange-600 mt-1">▸</span>
                                      <span>{assumption}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Reasoning Gaps (논리 비약) */}
                            {lp.reasoning_gaps && lp.reasoning_gaps.length > 0 && (
                              <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
                                <div className="flex items-center gap-2 mb-3">
                                  <AlertTriangle className="h-5 w-5 text-red-600" />
                                  <h4 className="font-bold text-red-900">
                                    논리 비약 (Reasoning Gaps) - 반박 포인트
                                  </h4>
                                </div>
                                <div className="space-y-3">
                                  {lp.reasoning_gaps.map((gap, i) => (
                                    <div key={i} className="bg-white rounded p-3 border border-red-200">
                                      <div className="space-y-2">
                                        <div className="flex items-start gap-2">
                                          <span className="text-xs font-semibold text-slate-500 mt-0.5">FROM:</span>
                                          <p className="text-sm text-slate-700 flex-1">{gap.from}</p>
                                        </div>
                                        <div className="flex items-center justify-center">
                                          <div className="text-red-600 text-lg">↓</div>
                                        </div>
                                        <div className="flex items-start gap-2">
                                          <span className="text-xs font-semibold text-slate-500 mt-0.5">TO:</span>
                                          <p className="text-sm text-slate-700 flex-1">{gap.to}</p>
                                        </div>
                                        <div className="mt-3 pt-3 border-t border-red-200">
                                          <div className="flex items-start gap-2">
                                            <span className="text-xs font-semibold text-red-600 mt-0.5">GAP:</span>
                                            <p className="text-sm text-red-900 font-medium flex-1">{gap.gap}</p>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Layer 3: Deep Beliefs */}
                            {lp.deep_beliefs && lp.deep_beliefs.length > 0 && (
                              <div className="bg-purple-50 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-3">
                                  <Heart className="h-5 w-5 text-purple-600" />
                                  <h4 className="font-bold text-purple-900">
                                    심층 (Deep) - 무의식적 믿음
                                  </h4>
                                </div>
                                <ul className="space-y-2">
                                  {lp.deep_beliefs.map((belief, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-purple-900">
                                      <span className="text-purple-600 mt-1">●</span>
                                      <span className="font-medium">{belief}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Worldview Hints */}
                            {lp.worldview_hints && (
                              <div className="bg-slate-50 rounded-lg p-4">
                                <div className="text-xs font-medium text-slate-600 mb-2">
                                  세계관 힌트:
                                </div>
                                <p className="text-sm text-slate-700 italic">
                                  {lp.worldview_hints}
                                </p>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Empty State */}
        {contents.length === 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
            <AlertCircle className="h-12 w-12 text-yellow-600 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">
              아직 원본 글 데이터가 연결되지 않았습니다
            </h3>
            <p className="text-yellow-800">
              데이터 수집 프로세스를 실행하여 원본 글을 연결하세요
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
