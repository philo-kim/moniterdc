'use client'

/**
 * 세계관 상세 페이지
 *
 * 6가지 반박 논리 구성 요소:
 * 1. 논리적 결함 (Logical Flaws)
 * 2. 팩트체크 (Fact Checks)
 * 3. 대안적 해석 (Alternative Interpretations)
 * 4. 역사적 수정 (Historical Corrections)
 * 5. 감정적 이해 (Emotional Understanding)
 * 6. 대화 가이드 (Dialogue Guide)
 */

import { useParams } from 'next/navigation'
import useSWR from 'swr'
import Link from 'next/link'
import {
  AlertTriangle,
  CheckCircle,
  Lightbulb,
  History,
  Heart,
  MessageCircle,
  ArrowLeft,
  Target,
  TrendingUp,
  ExternalLink,
  FileText
} from 'lucide-react'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

interface ParsedFrame {
  category: string
  subcategory: string
  narrative: {
    summary: string
    examples?: Array<{
      case: string
      dc_interpretation: string
      normal_interpretation: string
      gap: string
    }>
    logic_chain: string
    historical_context?: string
  }
  metadata: {
    core: {
      primary_subject: string
      primary_attribute: string
      primary_action: string
    }
    interpretation_frame: {
      historical_lens?: {
        reference_period: string
        reference_events: string[]
        projection_logic: string
      }
      causal_chain: string[]
      slippery_slope?: {
        trigger: string
        escalation: string
        endpoint: string
      }
    }
    emotional_drivers: {
      primary: string
      secondary: string[]
      urgency_level: string
    }
    key_concepts: string[]
  }
  deconstruction?: {
    logical_flaws?: Array<{
      type: string
      description: string
      example: string
      rebuttal: string
    }>
    fact_checks?: Array<{
      claim: string
      reality: string
      evidence: string
    }>
    alternative_interpretations?: Array<{
      dc_interpretation: string
      alternative: string
      reasoning: string
    }>
    historical_corrections?: Array<{
      their_reference: string
      actual_difference: string
      context: string
    }>
    emotional_understanding?: {
      their_emotion: string
      why_they_feel: string
      empathy: string
      but: string
    }
    dialogue_guide?: {
      avoid: string[]
      effective: string[]
      example_response: string
    }
  }
}

export default function WorldviewDetailPage() {
  const params = useParams()
  const id = params.id as string

  const { data: worldview, error, isLoading } = useSWR(
    `/api/worldviews/${id}`,
    fetcher
  )

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-600">로딩 중...</div>
      </div>
    )
  }

  if (error || !worldview) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-red-600">세계관을 불러올 수 없습니다</div>
      </div>
    )
  }

  const frame: ParsedFrame = JSON.parse(worldview.frame)
  const dec = frame.deconstruction || {}
  const perceptions = worldview.perceptions || []
  const contents = worldview.contents || []

  // Group perceptions by content
  const perceptionsByContent = new Map<string, any[]>()
  perceptions.forEach((p: any) => {
    if (p.content_id) {
      if (!perceptionsByContent.has(p.content_id)) {
        perceptionsByContent.set(p.content_id, [])
      }
      perceptionsByContent.get(p.content_id)!.push(p)
    }
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          세계관 지도로 돌아가기
        </Link>

        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-6">
          <div className="mb-4">
            <p className="text-sm text-slate-600 mb-2">{frame.category}</p>
            <h1 className="text-3xl font-bold text-slate-900 mb-4">
              {frame.subcategory}
            </h1>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-lg text-blue-900 leading-relaxed">
              {frame.narrative.summary}
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600">분석된 인식</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {worldview.total_perceptions || 0}
              </p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600">핵심 감정</p>
              <p className="text-2xl font-bold text-orange-600 mt-1">
                {frame.metadata.emotional_drivers.primary}
              </p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600">긴급도</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {frame.metadata.emotional_drivers.urgency_level}
              </p>
            </div>
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600">반박 준비</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {dec.logical_flaws ? '완료' : '미완'}
              </p>
            </div>
          </div>
        </div>

        {/* Logic Chain */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Target className="h-5 w-5 text-purple-600" />
            <h2 className="text-xl font-bold text-slate-900">논리 연쇄</h2>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <p className="font-mono text-purple-900">{frame.narrative.logic_chain}</p>
          </div>
        </div>

        {/* Source Contents */}
        {contents.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="h-5 w-5 text-blue-600" />
              <h2 className="text-xl font-bold text-slate-900">
                원본 글 ({contents.length}개)
              </h2>
            </div>
            <p className="text-sm text-slate-600 mb-4">
              이 세계관이 발견된 실제 DC Gallery 글들입니다
            </p>
            <div className="space-y-3">
              {contents.map((content: any) => {
                const contentPerceptions = perceptionsByContent.get(content.id) || []
                const publishedDate = content.published_at
                  ? new Date(content.published_at).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })
                  : '날짜 미상'

                return (
                  <div
                    key={content.id}
                    className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-slate-900 mb-2">
                          {content.title}
                        </h3>
                        {content.body && (
                          <p className="text-sm text-slate-600 mb-3 line-clamp-2">
                            {content.body.substring(0, 150)}...
                          </p>
                        )}
                        <div className="flex items-center gap-4 text-xs text-slate-500">
                          <span>{publishedDate}</span>
                          <span>•</span>
                          <span>{contentPerceptions.length}개 인식 추출</span>
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

                    {/* Show perceptions from this content */}
                    {contentPerceptions.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-200">
                        <p className="text-xs font-medium text-slate-700 mb-2">
                          이 글에서 추출된 인식:
                        </p>
                        <div className="space-y-2">
                          {contentPerceptions.slice(0, 2).map((perc: any, idx: number) => (
                            <div
                              key={idx}
                              className="bg-slate-50 rounded p-2 text-xs"
                            >
                              <p className="text-slate-700 mb-1">
                                <span className="font-medium">명시적 주장:</span>{' '}
                                {Array.isArray(perc.explicit_claims) && perc.explicit_claims[0]?.quote
                                  ? perc.explicit_claims[0].quote.substring(0, 80) + '...'
                                  : '(내용 없음)'}
                              </p>
                              <p className="text-slate-600">
                                <span className="font-medium">심층 믿음:</span>{' '}
                                {Array.isArray(perc.deep_beliefs) && perc.deep_beliefs[0]?.belief
                                  ? perc.deep_beliefs[0].belief.substring(0, 80) + '...'
                                  : '(내용 없음)'}
                              </p>
                            </div>
                          ))}
                          {contentPerceptions.length > 2 && (
                            <p className="text-xs text-slate-500 italic">
                              +{contentPerceptions.length - 2}개 더...
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Examples */}
        {frame.narrative.examples && frame.narrative.examples.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <h2 className="text-xl font-bold text-slate-900">구체적 사례</h2>
            </div>
            <div className="space-y-4">
              {frame.narrative.examples.map((ex, idx) => (
                <div key={idx} className="border border-slate-200 rounded-lg p-4">
                  <h3 className="font-semibold text-slate-900 mb-3">{ex.case}</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-red-50 border border-red-200 rounded p-3">
                      <p className="text-xs text-red-600 font-medium mb-1">DC 해석</p>
                      <p className="text-sm text-red-900">{ex.dc_interpretation}</p>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded p-3">
                      <p className="text-xs text-green-600 font-medium mb-1">일반 해석</p>
                      <p className="text-sm text-green-900">{ex.normal_interpretation}</p>
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-slate-600">
                    <span className="font-medium">차이점:</span> {ex.gap}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Deconstruction Sections */}
        {dec.logical_flaws && (
          <>
            {/* 1. Logical Flaws */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <h2 className="text-xl font-bold text-slate-900">1. 논리적 결함</h2>
              </div>
              <div className="space-y-4">
                {dec.logical_flaws.map((flaw, idx) => (
                  <div key={idx} className="border border-red-200 rounded-lg p-4 bg-red-50">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-red-900">{flaw.type}</h3>
                    </div>
                    <p className="text-sm text-red-800 mb-3">{flaw.description}</p>
                    <div className="bg-white rounded p-3 mb-3 border border-red-200">
                      <p className="text-xs text-red-600 font-medium mb-1">예시</p>
                      <p className="text-sm text-slate-800">{flaw.example}</p>
                    </div>
                    <div className="bg-green-50 rounded p-3 border border-green-200">
                      <p className="text-xs text-green-600 font-medium mb-1">반박</p>
                      <p className="text-sm text-green-900">{flaw.rebuttal}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 2. Fact Checks */}
            {dec.fact_checks && dec.fact_checks.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <h2 className="text-xl font-bold text-slate-900">2. 팩트체크</h2>
                </div>
                <div className="space-y-4">
                  {dec.fact_checks.map((check, idx) => (
                    <div key={idx} className="border border-slate-200 rounded-lg p-4">
                      <div className="mb-3">
                        <p className="text-xs text-red-600 font-medium mb-1">주장</p>
                        <p className="text-sm text-slate-800 bg-red-50 p-2 rounded border border-red-200">
                          {check.claim}
                        </p>
                      </div>
                      <div className="mb-3">
                        <p className="text-xs text-green-600 font-medium mb-1">현실</p>
                        <p className="text-sm text-slate-800 bg-green-50 p-2 rounded border border-green-200">
                          {check.reality}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-blue-600 font-medium mb-1">근거</p>
                        <p className="text-sm text-slate-600 bg-blue-50 p-2 rounded border border-blue-200">
                          {check.evidence}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 3. Alternative Interpretations */}
            {dec.alternative_interpretations && dec.alternative_interpretations.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <Lightbulb className="h-5 w-5 text-yellow-600" />
                  <h2 className="text-xl font-bold text-slate-900">3. 대안적 해석</h2>
                </div>
                <div className="space-y-4">
                  {dec.alternative_interpretations.map((alt, idx) => (
                    <div key={idx} className="border border-slate-200 rounded-lg p-4">
                      <div className="grid grid-cols-2 gap-4 mb-3">
                        <div>
                          <p className="text-xs text-red-600 font-medium mb-1">DC 해석</p>
                          <p className="text-sm text-slate-800 bg-red-50 p-2 rounded border border-red-200">
                            {alt.dc_interpretation}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-green-600 font-medium mb-1">대안 해석</p>
                          <p className="text-sm text-slate-800 bg-green-50 p-2 rounded border border-green-200">
                            {alt.alternative}
                          </p>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-blue-600 font-medium mb-1">논리적 근거</p>
                        <p className="text-sm text-slate-700 bg-blue-50 p-2 rounded border border-blue-200">
                          {alt.reasoning}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 4. Historical Corrections */}
            {dec.historical_corrections && dec.historical_corrections.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <History className="h-5 w-5 text-purple-600" />
                  <h2 className="text-xl font-bold text-slate-900">4. 역사적 수정</h2>
                </div>
                <div className="space-y-4">
                  {dec.historical_corrections.map((corr, idx) => (
                    <div key={idx} className="border border-slate-200 rounded-lg p-4">
                      <div className="mb-3">
                        <p className="text-xs text-slate-600 font-medium mb-1">그들이 참조하는 역사</p>
                        <p className="text-sm text-slate-800 bg-slate-50 p-2 rounded border border-slate-200">
                          {corr.their_reference}
                        </p>
                      </div>
                      <div className="mb-3">
                        <p className="text-xs text-blue-600 font-medium mb-1">실제 차이점</p>
                        <p className="text-sm text-slate-800 bg-blue-50 p-2 rounded border border-blue-200">
                          {corr.actual_difference}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-green-600 font-medium mb-1">맥락</p>
                        <p className="text-sm text-slate-700 bg-green-50 p-2 rounded border border-green-200">
                          {corr.context}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 5. Emotional Understanding */}
            {dec.emotional_understanding && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <Heart className="h-5 w-5 text-pink-600" />
                  <h2 className="text-xl font-bold text-slate-900">5. 감정적 이해</h2>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                      <p className="text-xs text-orange-600 font-medium mb-1">그들의 감정</p>
                      <p className="text-lg font-semibold text-orange-900 mb-2">
                        {dec.emotional_understanding.their_emotion}
                      </p>
                      <p className="text-sm text-orange-800">
                        {dec.emotional_understanding.why_they_feel}
                      </p>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-xs text-blue-600 font-medium mb-1">공감</p>
                      <p className="text-sm text-blue-900">
                        {dec.emotional_understanding.empathy}
                      </p>
                    </div>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-xs text-green-600 font-medium mb-1">하지만</p>
                    <p className="text-sm text-green-900">
                      {dec.emotional_understanding.but}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* 6. Dialogue Guide */}
            {dec.dialogue_guide && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <MessageCircle className="h-5 w-5 text-blue-600" />
                  <h2 className="text-xl font-bold text-slate-900">6. 대화 가이드</h2>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <p className="text-xs text-red-600 font-medium mb-2">피해야 할 표현</p>
                      <ul className="space-y-1">
                        {dec.dialogue_guide.avoid.map((item, idx) => (
                          <li key={idx} className="text-sm text-red-900 flex items-start gap-2">
                            <span className="text-red-600">×</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <p className="text-xs text-green-600 font-medium mb-2">효과적인 접근</p>
                      <ul className="space-y-1">
                        {dec.dialogue_guide.effective.map((item, idx) => (
                          <li key={idx} className="text-sm text-green-900 flex items-start gap-2">
                            <span className="text-green-600">✓</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="bg-blue-50 border-l-4 border-blue-600 rounded-lg p-4">
                    <p className="text-xs text-blue-600 font-medium mb-2">예시 응답</p>
                    <p className="text-sm text-blue-900 leading-relaxed">
                      &ldquo;{dec.dialogue_guide.example_response}&rdquo;
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* No Deconstruction */}
        {!dec.logical_flaws && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-yellow-600 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">
              반박 논리가 아직 생성되지 않았습니다
            </h3>
            <p className="text-yellow-800">
              scripts/generate_deconstruction.py를 실행하여 반박 논리를 생성하세요
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
