'use client'

/**
 * ConsolidatedWorldviewMap - 통합된 세계관 지도
 *
 * 24개 → 9개 통합된 worldview 표시
 * - Priority 배지 (HIGH/MEDIUM/LOW)
 * - TOP 3 기본 표시, 나머지는 접기
 * - 명확한 공격 유형 중심
 */

import { useState } from 'react'
import useSWR from 'swr'
import { ChevronDown, ChevronUp, AlertCircle, Target, TrendingUp, Shield } from 'lucide-react'
import Link from 'next/link'

interface Worldview {
  id: string
  title: string
  description: string
  frame: string
  total_perceptions: number
  strength_overall: number
}

interface ParsedFrame {
  priority: 'high' | 'medium' | 'low'
  category: string
  subcategory: string
  description: string
  metadata?: {
    merged_from: string[]
    estimated_count: number
  }
}

const fetcher = (url: string) => fetch(url).then(r => r.json())

// Priority 배지 컴포넌트
function PriorityBadge({ priority }: { priority: 'high' | 'medium' | 'low' }) {
  const styles = {
    high: 'bg-red-100 text-red-800 border-red-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    low: 'bg-green-100 text-green-800 border-green-300'
  }

  const labels = {
    high: '긴급',
    medium: '주의',
    low: '모니터링'
  }

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold border-2 ${styles[priority]}`}>
      {labels[priority]}
    </span>
  )
}

export function ConsolidatedWorldviewMap() {
  const [showAll, setShowAll] = useState(false)

  const { data, error, isLoading } = useSWR(
    '/api/worldviews?limit=100',
    fetcher,
    { refreshInterval: 30000 }
  )

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        <AlertCircle className="h-12 w-12 mx-auto mb-4" />
        <p className="font-semibold">데이터 로딩 실패</p>
        <p className="text-sm mt-2">{error.message}</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
        <p className="mt-4 text-slate-600">공격 유형 분석 로딩 중...</p>
      </div>
    )
  }

  const worldviews: Worldview[] = data?.worldviews || []

  // Parse and sort worldviews
  const parsedWorldviews = worldviews
    .map(wv => {
      try {
        const frame: ParsedFrame = JSON.parse(wv.frame)
        return {
          id: wv.id,
          title: wv.title,
          description: wv.description || frame.description,
          priority: frame.priority || 'low',
          total_perceptions: wv.total_perceptions || 0,
          strength: wv.strength_overall || 0,
          merged_count: frame.metadata?.merged_from?.length || 1
        }
      } catch (e) {
        console.error('Failed to parse worldview:', wv.id, e)
        return null
      }
    })
    .filter(Boolean) as Array<{
      id: string
      title: string
      description: string
      priority: 'high' | 'medium' | 'low'
      total_perceptions: number
      strength: number
      merged_count: number
    }>

  // Sort by priority (high > medium > low) then by perception count
  const priorityOrder = { high: 0, medium: 1, low: 2 }
  parsedWorldviews.sort((a, b) => {
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority]
    if (priorityDiff !== 0) return priorityDiff
    return b.total_perceptions - a.total_perceptions
  })

  // TOP 3 vs Rest
  const top3 = parsedWorldviews.slice(0, 3)
  const rest = parsedWorldviews.slice(3)

  const totalPerceptions = parsedWorldviews.reduce((sum, wv) => sum + wv.total_perceptions, 0)
  const highPriorityCount = parsedWorldviews.filter(wv => wv.priority === 'high').length
  const top3Percentage = top3.reduce((sum, wv) => sum + wv.total_perceptions, 0) / totalPerceptions * 100

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">공격 유형</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{parsedWorldviews.length}</p>
              <p className="text-xs text-slate-500 mt-1">24개에서 통합</p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">긴급 대응 필요</p>
              <p className="text-3xl font-bold text-red-600 mt-1">{highPriorityCount}</p>
              <p className="text-xs text-slate-500 mt-1">HIGH priority</p>
            </div>
            <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertCircle className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">분석된 공격</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{totalPerceptions}</p>
              <p className="text-xs text-slate-500 mt-1">perception 수</p>
            </div>
            <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">TOP 3 집중도</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">{Math.round(top3Percentage)}%</p>
              <p className="text-xs text-slate-500 mt-1">전체 중</p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Shield className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Alert Box for High Priority */}
      {highPriorityCount > 0 && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 mb-1">긴급 대응이 필요한 공격 {highPriorityCount}개</h3>
              <p className="text-sm text-red-800">
                현재 가장 많이 퍼지고 있는 공격 유형입니다. 우선적으로 대응 전략을 확인하세요.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* TOP 3 Worldviews */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-slate-900">
            🎯 TOP 3 주요 공격
          </h2>
          <span className="text-sm text-slate-600">
            전체의 {Math.round(top3Percentage)}%
          </span>
        </div>

        {top3.map((wv, index) => (
          <div
            key={wv.id}
            className="bg-white rounded-lg shadow-md border-2 border-slate-200 p-6 hover:shadow-lg transition-all"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-4 flex-1">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                    <span className="text-white text-xl font-bold">{index + 1}</span>
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-bold text-slate-900">
                      {wv.title}
                    </h3>
                    <PriorityBadge priority={wv.priority} />
                  </div>

                  <p className="text-slate-700 leading-relaxed">
                    {wv.description}
                  </p>
                </div>
              </div>
            </div>

            {/* Stats Bar */}
            <div className="flex items-center gap-6 mb-4">
              <div className="flex-1">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-slate-600">출현 빈도</span>
                  <span className="font-semibold text-slate-900">{wv.total_perceptions}개</span>
                </div>
                <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                    style={{ width: `${(wv.total_perceptions / totalPerceptions) * 100}%` }}
                  />
                </div>
              </div>

              {wv.merged_count > 1 && (
                <div className="text-sm">
                  <span className="text-slate-600">통합: </span>
                  <span className="font-semibold text-blue-600">{wv.merged_count}개</span>
                </div>
              )}
            </div>

            {/* Action Button */}
            <Link
              href={`/worldviews/${wv.id}`}
              className="block w-full py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all text-center font-semibold"
            >
              상세 분석 및 대응 전략 보기 →
            </Link>
          </div>
        ))}
      </div>

      {/* Rest of Worldviews */}
      {rest.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900">
              기타 공격 유형 ({rest.length}개)
            </h2>
            <button
              onClick={() => setShowAll(!showAll)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              {showAll ? (
                <>
                  접기 <ChevronUp className="h-4 w-4" />
                </>
              ) : (
                <>
                  펼치기 <ChevronDown className="h-4 w-4" />
                </>
              )}
            </button>
          </div>

          {showAll && (
            <div className="grid grid-cols-2 gap-4">
              {rest.map(wv => (
                <div
                  key={wv.id}
                  className="bg-white rounded-lg shadow-sm border border-slate-200 p-5 hover:shadow-md transition-shadow"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-slate-900">
                          {wv.title}
                        </h3>
                        <PriorityBadge priority={wv.priority} />
                      </div>
                      <p className="text-sm text-slate-600 leading-relaxed">
                        {wv.description}
                      </p>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-4 mb-3 text-sm">
                    <div>
                      <span className="text-slate-600">출현: </span>
                      <span className="font-semibold text-slate-900">{wv.total_perceptions}개</span>
                    </div>
                    {wv.merged_count > 1 && (
                      <div>
                        <span className="text-slate-600">통합: </span>
                        <span className="font-semibold text-blue-600">{wv.merged_count}개</span>
                      </div>
                    )}
                  </div>

                  {/* Action Button */}
                  <Link
                    href={`/worldviews/${wv.id}`}
                    className="block w-full py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors text-center text-sm font-medium"
                  >
                    상세 보기 →
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {parsedWorldviews.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          <Target className="h-12 w-12 mx-auto mb-4 text-slate-300" />
          <p className="font-semibold">분석된 공격 유형이 없습니다.</p>
        </div>
      )}
    </div>
  )
}
