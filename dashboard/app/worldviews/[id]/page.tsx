'use client'

import { useParams } from 'next/navigation'
import useSWR from 'swr'
import Link from 'next/link'
import {
  ArrowLeft,
  Target,
  FileText,
  ExternalLink,
  AlertCircle,
  TrendingUp
} from 'lucide-react'

const fetcher = (url: string) => fetch(url).then((res) => res.json())

interface Perception {
  id: string
  content_id: string
  perceived_subject: string
  perceived_attribute: string
  perceived_valence: 'positive' | 'negative' | 'neutral'
  claims: string[]
  keywords: string[]
  emotions: string[]
  credibility: number
  confidence: number
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

function ValenceBadge({ valence }: { valence: string }) {
  const config = {
    positive: { bg: 'bg-green-100', text: 'text-green-800', label: '긍정' },
    negative: { bg: 'bg-red-100', text: 'text-red-800', label: '부정' },
    neutral: { bg: 'bg-gray-100', text: 'text-gray-800', label: '중립' }
  }

  const style = config[valence as keyof typeof config] || config.neutral

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${style.bg} ${style.text}`}>
      {style.label}
    </span>
  )
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
  const perceptions: Perception[] = worldview.perceptions || []
  const contents: Content[] = worldview.contents || []

  // Group perceptions by content
  const perceptionsByContent = new Map<string, Perception[]>()
  perceptions.forEach((p) => {
    if (p.content_id) {
      if (!perceptionsByContent.has(p.content_id)) {
        perceptionsByContent.set(p.content_id, [])
      }
      perceptionsByContent.get(p.content_id)!.push(p)
    }
  })

  // 감정/키워드 통계
  const emotionCounts = new Map<string, number>()
  const keywordCounts = new Map<string, number>()

  perceptions.forEach(p => {
    p.emotions?.forEach(emotion => {
      emotionCounts.set(emotion, (emotionCounts.get(emotion) || 0) + 1)
    })
    p.keywords?.forEach(keyword => {
      keywordCounts.set(keyword, (keywordCounts.get(keyword) || 0) + 1)
    })
  })

  const topEmotions = Array.from(emotionCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  const topKeywords = Array.from(keywordCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-5xl mx-auto px-6 py-8">
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
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600">분석된 공격</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">
                {worldview.total_perceptions || 0}개
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

        {/* 주요 감정 */}
        {topEmotions.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-5 w-5 text-orange-600" />
              <h2 className="text-xl font-bold text-slate-900">주요 감정</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {topEmotions.map(([emotion, count]) => (
                <span
                  key={emotion}
                  className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium"
                >
                  {emotion} ({count})
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 주요 키워드 */}
        {topKeywords.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Target className="h-5 w-5 text-purple-600" />
              <h2 className="text-xl font-bold text-slate-900">주요 키워드</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {topKeywords.map(([keyword, count]) => (
                <span
                  key={keyword}
                  className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                >
                  {keyword} ({count})
                </span>
              ))}
            </div>
          </div>
        )}

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
              이 공격 유형이 발견된 실제 DC Gallery 글들입니다
            </p>
            <div className="space-y-3">
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
                          이 글에서 추출된 인식 ({contentPerceptions.length}개):
                        </p>
                        <div className="space-y-2">
                          {contentPerceptions.slice(0, 3).map((perc, idx) => (
                            <div
                              key={idx}
                              className="bg-slate-50 rounded p-3"
                            >
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-semibold text-slate-900">
                                      {perc.perceived_subject}
                                    </span>
                                    <ValenceBadge valence={perc.perceived_valence} />
                                  </div>
                                  <p className="text-sm text-slate-600">
                                    {perc.perceived_attribute}
                                  </p>
                                </div>
                              </div>

                              {perc.claims && perc.claims.length > 0 && (
                                <div className="mt-2">
                                  <p className="text-xs font-medium text-slate-600 mb-1">주장:</p>
                                  <ul className="space-y-1">
                                    {perc.claims.map((claim, i) => (
                                      <li key={i} className="text-sm text-slate-700">
                                        • {claim}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              <div className="mt-2 flex flex-wrap gap-1">
                                {perc.emotions?.slice(0, 3).map((emotion, i) => (
                                  <span
                                    key={i}
                                    className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded text-xs"
                                  >
                                    {emotion}
                                  </span>
                                ))}
                                {perc.keywords?.slice(0, 4).map((keyword, i) => (
                                  <span
                                    key={i}
                                    className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs"
                                  >
                                    {keyword}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))}
                          {contentPerceptions.length > 3 && (
                            <p className="text-xs text-slate-500 italic">
                              +{contentPerceptions.length - 3}개 더...
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
