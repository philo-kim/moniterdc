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
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Users
} from 'lucide-react'
import { InterpretationComparison } from '@/components/worldviews/InterpretationComparison'
import { LogicChainVisualizer } from '@/components/worldviews/LogicChainVisualizer'
import { MechanismMatchingExplanation } from '@/components/worldviews/MechanismMatchingExplanation'
import { MechanismList, type MechanismType } from '@/components/worldviews/MechanismBadge'

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

interface Actor {
  subject: string
  purpose: string
  methods: string[]
}

interface LayeredPerception {
  id: string
  content_id: string
  explicit_claims: ExplicitClaim[] | string[]  // Support both old and new formats
  implicit_assumptions: string[]
  reasoning_gaps?: ReasoningGap[]
  deep_beliefs: string[]
  worldview_hints?: string
  mechanisms?: MechanismType[]
  actor?: Actor
  logic_chain?: string[]
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
  narrative?: {
    summary?: string
    examples?: Array<{
      case: string
      dc_interpretation: string
      normal_interpretation: string
      gap: string
    }>
    logic_chain?: string
  }
  metadata?: {
    merged_from?: string[]
    estimated_count?: number
  }
}

function PriorityBadge({ priority }: { priority?: 'high' | 'medium' | 'low' }) {
  if (!priority) return null

  const config = {
    high: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      border: 'border-blue-300',
      label: '이해 우선순위: 높음'
    },
    medium: {
      bg: 'bg-purple-100',
      text: 'text-purple-800',
      border: 'border-purple-300',
      label: '이해 우선순위: 중간'
    },
    low: {
      bg: 'bg-slate-100',
      text: 'text-slate-800',
      border: 'border-slate-300',
      label: '이해 우선순위: 낮음'
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
  const [showAllContents, setShowAllContents] = useState(false)
  const [expandedContentIds, setExpandedContentIds] = useState<Set<string>>(new Set())

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
          <p className="text-red-600 font-semibold">세계관 데이터를 불러올 수 없습니다</p>
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

  // Representative perception (첫 번째 것 사용)
  const representativePerception = layeredPerceptions[0]

  // Representative contents (대표 사례 5개)
  const representativeContents = contents.slice(0, 5)
  const remainingContents = contents.slice(5)
  const displayedContents = showAllContents ? contents : representativeContents

  const toggleContentExpanded = (contentId: string) => {
    setExpandedContentIds(prev => {
      const next = new Set(prev)
      if (next.has(contentId)) {
        next.delete(contentId)
      } else {
        next.add(contentId)
      }
      return next
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          세계관 지도로 돌아가기
        </Link>

        {/* Header - v2.0 사고 구조 중심 */}
        <div className="bg-gradient-to-br from-white to-slate-50 rounded-xl shadow-lg border-2 border-blue-300 p-8 mb-6">
          {/* 타이틀 */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-slate-900 mb-3">
              {worldview.title}
            </h1>
            <p className="text-lg text-slate-700 leading-relaxed">
              {worldview.description || frame.description}
            </p>
          </div>

          {/* v2.0 핵심: 메커니즘 + Actor */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* 핵심 메커니즘 */}
            {worldview.core_attributes && (worldview.core_attributes as MechanismType[]).length > 0 && (
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-5 border-2 border-purple-300">
                <h3 className="text-sm font-bold text-purple-900 mb-3 flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  사고 메커니즘 (어떻게 생각하는가)
                </h3>
                <MechanismList mechanisms={worldview.core_attributes as MechanismType[]} size="md" showTooltip={true} />
              </div>
            )}

            {/* 핵심 행위자 */}
            {worldview.core_subject && (
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-5 border-2 border-indigo-300">
                <h3 className="text-sm font-bold text-indigo-900 mb-3 flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  핵심 행위자 (누구를 주목하는가)
                </h3>
                <div className="inline-block bg-white px-6 py-3 rounded-lg border-2 border-indigo-400 shadow-sm">
                  <p className="text-2xl font-bold text-indigo-900">
                    {worldview.core_subject}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center p-4 bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-600 mb-1">분석된 담론</p>
              <p className="text-2xl font-bold text-slate-900">
                {layeredPerceptions.length}
              </p>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
              <p className="text-xs text-blue-700 mb-1">원본 글</p>
              <p className="text-2xl font-bold text-blue-900">
                {contents.length}
              </p>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200">
              <p className="text-xs text-purple-700 mb-1">버전</p>
              <p className="text-2xl font-bold text-purple-900">
                v{worldview.version || 1}.0
              </p>
            </div>
          </div>
        </div>

        {/* 🎯 핵심 구조: 세계관 레벨 논리 패턴 */}
        {worldview.logic_chain && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <h2 className="text-xl font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Brain className="h-6 w-6 text-purple-600" />
              논리 구조: 어떻게 이 생각에 도달했는가?
            </h2>
            <p className="text-sm text-slate-600 mb-6">
              {layeredPerceptions.length}개 담론에서 추출한 공통 사고 패턴
            </p>

            <div className="space-y-4">
              {/* Trigger */}
              {worldview.logic_chain.trigger && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border-2 border-blue-200">
                  <div className="flex items-start gap-3">
                    <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
                      1
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-bold text-blue-900 mb-1">출발점 (Trigger)</p>
                      <p className="text-slate-800">{worldview.logic_chain.trigger}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Skipped Verification */}
              {worldview.logic_chain.skipped_verification && worldview.logic_chain.skipped_verification.length > 0 && (
                <>
                  <div className="flex justify-center">
                    <div className="text-amber-600 text-2xl font-bold">↓</div>
                  </div>
                  <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg p-4 border-2 border-amber-300">
                    <div className="flex items-start gap-3">
                      <div className="bg-amber-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
                        ⚠
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-bold text-amber-900 mb-2">건너뛴 검증 단계</p>
                        <p className="text-xs text-amber-800 mb-3 italic">
                          이런 가능성들은 고려하지 않고 바로 결론으로 넘어갑니다
                        </p>
                        <ul className="space-y-2">
                          {worldview.logic_chain.skipped_verification.map((skip: string, i: number) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-amber-600 mt-1">▸</span>
                              <span className="text-slate-800 text-sm">{skip}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {/* Conclusion */}
              {worldview.logic_chain.conclusion && (
                <>
                  <div className="flex justify-center">
                    <div className="text-purple-600 text-2xl font-bold">↓</div>
                  </div>
                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border-2 border-purple-300">
                    <div className="flex items-start gap-3">
                      <div className="bg-purple-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
                        2
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-bold text-purple-900 mb-1">결론 (Conclusion)</p>
                        <p className="text-slate-800 font-medium">{worldview.logic_chain.conclusion}</p>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="mt-6 bg-slate-50 rounded-lg p-4 border border-slate-200">
              <p className="text-xs text-slate-600 leading-relaxed">
                💡 <strong>이 논리 구조는</strong> 개별 글 하나가 아닌, {layeredPerceptions.length}개 담론에서 반복적으로 나타나는 <strong>공통 사고 패턴</strong>입니다.
                개별 사례의 구체적인 분석은 아래 &ldquo;대표 사례&rdquo; 목록에서 확인할 수 있습니다.
              </p>
            </div>
          </div>
        )}

        {/* 🔍 해석 차이 비교 */}
        {frame.narrative?.examples && frame.narrative.examples.length > 0 && (
          <InterpretationComparison
            examples={frame.narrative.examples}
            category={frame.category}
          />
        )}

        {/* 📊 대표 사례 */}
        {contents.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <h2 className="text-xl font-bold text-slate-900">
                  대표 사례 {showAllContents ? `(전체 ${contents.length}개)` : `(${representativeContents.length}개)`}
                </h2>
              </div>
              {remainingContents.length > 0 && (
                <button
                  onClick={() => setShowAllContents(!showAllContents)}
                  className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  {showAllContents ? '대표 사례만 보기' : `전체 ${contents.length}개 보기`}
                </button>
              )}
            </div>
            <p className="text-sm text-slate-600 mb-6">
              {showAllContents
                ? '이 세계관이 발견된 모든 원본 글입니다'
                : '이 세계관을 가장 잘 보여주는 대표적인 사례들입니다'}
            </p>
            <div className="space-y-6">
              {displayedContents.map((content) => {
                const contentPerceptions = perceptionsByContent.get(content.id) || []
                const dateToUse = content.published_at || content.created_at
                const publishedDate = dateToUse
                  ? new Date(dateToUse).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })
                  : '날짜 미상'
                const isExpanded = expandedContentIds.has(content.id)

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
                      <div className="flex gap-2">
                        <a
                          href={content.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm font-medium"
                        >
                          <span>원문 보기</span>
                          <ExternalLink className="h-4 w-4" />
                        </a>
                        {contentPerceptions.length > 0 && (
                          <button
                            onClick={() => toggleContentExpanded(content.id)}
                            className="flex-shrink-0 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors flex items-center gap-2 text-sm font-medium"
                          >
                            <span>{isExpanded ? '분석 접기' : '분석 펼치기'}</span>
                            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                          </button>
                        )}
                      </div>
                    </div>

                    {/* 3-Layer Analysis */}
                    {contentPerceptions.length > 0 && isExpanded && (
                      <div className="mt-4 pt-4 border-t-2 border-slate-200 space-y-4">
                        {contentPerceptions.slice(0, 1).map((lp, idx) => (
                          <div key={idx} className="space-y-4">
                            {/* v2.0: Mechanisms & Actor */}
                            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border-2 border-purple-200">
                              <h4 className="font-bold text-purple-900 mb-3 text-sm">
                                🧠 v2.0 사고 구조 분석
                              </h4>

                              {/* Mechanisms */}
                              {lp.mechanisms && lp.mechanisms.length > 0 && (
                                <div className="mb-3">
                                  <p className="text-xs font-medium text-slate-700 mb-2">사고 메커니즘:</p>
                                  <MechanismList mechanisms={lp.mechanisms} size="sm" showTooltip={true} />
                                </div>
                              )}

                              {/* Actor */}
                              {lp.actor && (
                                <div className="bg-white rounded-lg p-3 border border-purple-200">
                                  <p className="text-xs font-bold text-purple-900 mb-2">행위자 구조:</p>
                                  <div className="space-y-1.5 text-xs">
                                    <div className="flex items-start gap-2">
                                      <span className="font-semibold text-indigo-700 min-w-[60px]">누가:</span>
                                      <span className="text-slate-900">{lp.actor.subject}</span>
                                    </div>
                                    <div className="flex items-start gap-2">
                                      <span className="font-semibold text-purple-700 min-w-[60px]">왜:</span>
                                      <span className="text-slate-900">{lp.actor.purpose}</span>
                                    </div>
                                    <div className="flex items-start gap-2">
                                      <span className="font-semibold text-blue-700 min-w-[60px]">어떻게:</span>
                                      <span className="text-slate-900">{lp.actor.methods.join(', ')}</span>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Logic Chain */}
                              {lp.logic_chain && lp.logic_chain.length > 0 && (
                                <div className="mt-3 bg-white rounded-lg p-3 border border-blue-200">
                                  <p className="text-xs font-bold text-blue-900 mb-2">사고 흐름 (Logic Chain):</p>
                                  <div className="space-y-2">
                                    {lp.logic_chain.map((step, i) => (
                                      <div key={i} className="flex items-start gap-2">
                                        <span className="text-blue-600 font-bold min-w-[20px]">{i + 1}.</span>
                                        <span className="text-xs text-slate-800">{step}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>

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
                                  {lp.explicit_claims.map((claim, i) => {
                                    // Handle both string and object formats
                                    if (typeof claim === 'string') {
                                      return (
                                        <div key={i} className="bg-white rounded p-3">
                                          <div className="text-slate-900">
                                            {claim}
                                          </div>
                                        </div>
                                      )
                                    } else {
                                      return (
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
                                      )
                                    }
                                  })}
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
                              <div className="bg-amber-50 rounded-lg p-4 border-2 border-amber-200">
                                <div className="flex items-center gap-2 mb-3">
                                  <AlertTriangle className="h-5 w-5 text-amber-600" />
                                  <h4 className="font-bold text-amber-900">
                                    논리 연결 (Reasoning Gaps) - 해석 차이 지점
                                  </h4>
                                </div>
                                <div className="space-y-3">
                                  {lp.reasoning_gaps.map((gap, i) => (
                                    <div key={i} className="bg-white rounded p-3 border border-amber-200">
                                      <div className="space-y-2">
                                        <div className="flex items-start gap-2">
                                          <span className="text-xs font-semibold text-slate-500 mt-0.5">FROM:</span>
                                          <p className="text-sm text-slate-700 flex-1">{gap.from}</p>
                                        </div>
                                        <div className="flex items-center justify-center">
                                          <div className="text-amber-600 text-lg">↓</div>
                                        </div>
                                        <div className="flex items-start gap-2">
                                          <span className="text-xs font-semibold text-slate-500 mt-0.5">TO:</span>
                                          <p className="text-sm text-slate-700 flex-1">{gap.to}</p>
                                        </div>
                                        <div className="mt-3 pt-3 border-t border-amber-200">
                                          <div className="flex items-start gap-2">
                                            <span className="text-xs font-semibold text-amber-700 mt-0.5">해석 차이:</span>
                                            <p className="text-sm text-amber-900 font-medium flex-1">{gap.gap}</p>
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
