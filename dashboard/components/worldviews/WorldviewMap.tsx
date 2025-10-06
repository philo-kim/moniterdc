'use client'

/**
 * WorldviewMap - 세계관 지도 메인 뷰
 *
 * 모든 세계관을 카드 형태로 표시하고 필터링/정렬 기능 제공
 */

import { useState, useEffect } from 'react'
import useSWR from 'swr'
import { WorldviewCard } from './WorldviewCard'
import { Loader2, TrendingUp, TrendingDown, Minus, SkullIcon } from 'lucide-react'

interface Worldview {
  id: string
  title: string
  frame: string
  core_subject: string
  core_attributes: string[]
  overall_valence: string
  strength_overall: number
  strength_cognitive: number
  strength_temporal: number
  strength_social: number
  strength_structural: number
  total_perceptions: number
  total_contents: number
  trend: 'rising' | 'stable' | 'falling' | 'dead'
  first_seen: string
  last_seen: string
  created_at: string
}

const fetcher = (url: string) => fetch(url).then(r => r.json())

export function WorldviewMap() {
  const [sortBy, setSortBy] = useState('strength_overall')
  const [trendFilter, setTrendFilter] = useState<string | null>(null)
  const [minStrength, setMinStrength] = useState(0)

  // Build query params
  const queryParams = new URLSearchParams({
    sort_by: sortBy,
    order: 'desc',
    min_strength: minStrength.toString()
  })

  if (trendFilter) {
    queryParams.set('trend', trendFilter)
  }

  const { data, error, isLoading } = useSWR(
    `/api/worldviews?${queryParams.toString()}`,
    fetcher,
    {
      refreshInterval: 30000 // Refresh every 30s
    }
  )

  if (error) {
    return (
      <div className="text-center py-12 text-red-500">
        Error loading worldviews: {error.message}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-3 text-gray-600">Loading worldviews...</span>
      </div>
    )
  }

  const worldviews = data?.worldviews || []
  const total = data?.pagination?.total || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">세계관 지도</h1>
          <p className="text-gray-600 mt-1">
            {total}개의 왜곡된 세계관 패턴 감지됨
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 space-y-4">
        <div className="flex flex-wrap gap-4">
          {/* Sort by */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              정렬
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="strength_overall">전체 강도</option>
              <option value="total_perceptions">인식 개수</option>
              <option value="created_at">생성일</option>
              <option value="updated_at">업데이트일</option>
            </select>
          </div>

          {/* Trend filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              추세
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setTrendFilter(null)}
                className={`px-3 py-2 text-sm rounded-md ${
                  trendFilter === null
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                전체
              </button>
              <button
                onClick={() => setTrendFilter('rising')}
                className={`px-3 py-2 text-sm rounded-md flex items-center gap-1 ${
                  trendFilter === 'rising'
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                <TrendingUp className="h-4 w-4" />
                상승
              </button>
              <button
                onClick={() => setTrendFilter('stable')}
                className={`px-3 py-2 text-sm rounded-md flex items-center gap-1 ${
                  trendFilter === 'stable'
                    ? 'bg-yellow-500 text-white'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                <Minus className="h-4 w-4" />
                안정
              </button>
              <button
                onClick={() => setTrendFilter('falling')}
                className={`px-3 py-2 text-sm rounded-md flex items-center gap-1 ${
                  trendFilter === 'falling'
                    ? 'bg-orange-500 text-white'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                <TrendingDown className="h-4 w-4" />
                하락
              </button>
              <button
                onClick={() => setTrendFilter('dead')}
                className={`px-3 py-2 text-sm rounded-md flex items-center gap-1 ${
                  trendFilter === 'dead'
                    ? 'bg-gray-500 text-white'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                <SkullIcon className="h-4 w-4" />
                소멸
              </button>
            </div>
          </div>

          {/* Min strength slider */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              최소 강도: {minStrength.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={minStrength}
              onChange={(e) => setMinStrength(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Worldview Cards Grid */}
      {worldviews.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          필터 조건에 맞는 세계관이 없습니다.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {worldviews.map((worldview: Worldview) => (
            <WorldviewCard key={worldview.id} worldview={worldview} />
          ))}
        </div>
      )}
    </div>
  )
}
