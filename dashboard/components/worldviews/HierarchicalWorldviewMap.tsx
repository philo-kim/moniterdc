'use client'

/**
 * HierarchicalWorldviewMap - 계층형 세계관 지도
 *
 * Category > Subcategory 구조로 세계관을 표시
 * 3개 주요 카테고리로 그룹화
 */

import { useState } from 'react'
import useSWR from 'swr'
import { ChevronDown, ChevronRight, MessageSquare, Target, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

interface Worldview {
  id: string
  title: string
  frame: string
  total_perceptions: number
  strength_overall: number
}

interface ParsedFrame {
  category: string
  subcategory: string
  narrative: {
    summary: string
    logic_chain: string
  }
  metadata: {
    core: {
      primary_subject: string
      primary_attribute: string
    }
    emotional_drivers: {
      primary: string
    }
  }
  deconstruction?: {
    logical_flaws?: any[]
    fact_checks?: any[]
  }
}

interface CategoryGroup {
  name: string
  worldviews: {
    id: string
    subcategory: string
    summary: string
    logic_chain: string
    total_perceptions: number
    strength: number
    primary_emotion: string
    has_deconstruction: boolean
  }[]
  total_perceptions: number
}

const fetcher = (url: string) => fetch(url).then(r => r.json())

export function HierarchicalWorldviewMap() {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['민주당/좌파에 대한 인식', '외부 세력의 위협']))

  const { data, error, isLoading } = useSWR(
    '/api/worldviews?limit=100',
    fetcher,
    { refreshInterval: 30000 }
  )

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        데이터 로딩 실패: {error.message}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
        <p className="mt-4 text-slate-600">세계관 분석 로딩 중...</p>
      </div>
    )
  }

  const worldviews: Worldview[] = data?.worldviews || []

  // Filter only hierarchical worldviews (with '>')
  const hierarchical = worldviews.filter(w => w.title.includes('>'))

  // Group by category
  const categories: CategoryGroup[] = []
  const categoryMap = new Map<string, CategoryGroup>()

  hierarchical.forEach(wv => {
    try {
      const frame: ParsedFrame = JSON.parse(wv.frame)
      const catName = frame.category

      if (!categoryMap.has(catName)) {
        categoryMap.set(catName, {
          name: catName,
          worldviews: [],
          total_perceptions: 0
        })
      }

      const cat = categoryMap.get(catName)!
      cat.worldviews.push({
        id: wv.id,
        subcategory: frame.subcategory,
        summary: frame.narrative.summary,
        logic_chain: frame.narrative.logic_chain,
        total_perceptions: wv.total_perceptions,
        strength: wv.strength_overall,
        primary_emotion: frame.metadata.emotional_drivers.primary,
        has_deconstruction: !!(frame.deconstruction && Object.keys(frame.deconstruction).length > 0)
      })
      cat.total_perceptions += wv.total_perceptions
    } catch (e) {
      console.error('Failed to parse worldview:', wv.id, e)
    }
  })

  categoryMap.forEach(cat => categories.push(cat))

  // Sort categories by total perceptions
  categories.sort((a, b) => b.total_perceptions - a.total_perceptions)

  const toggleCategory = (catName: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(catName)) {
      newExpanded.delete(catName)
    } else {
      newExpanded.add(catName)
    }
    setExpandedCategories(newExpanded)
  }

  // Emotion color mapping
  const getEmotionColor = (emotion: string) => {
    const colors: Record<string, string> = {
      '불안': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      '분노': 'bg-red-100 text-red-800 border-red-300',
      '경계': 'bg-orange-100 text-orange-800 border-orange-300',
      '불신': 'bg-purple-100 text-purple-800 border-purple-300',
      '두려움': 'bg-gray-100 text-gray-800 border-gray-300'
    }
    return colors[emotion] || 'bg-blue-100 text-blue-800 border-blue-300'
  }

  const totalPerceptions = categories.reduce((sum, cat) => sum + cat.total_perceptions, 0)

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">주요 카테고리</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{categories.length}</p>
            </div>
            <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">세부 세계관</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{hierarchical.length}</p>
            </div>
            <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600">분석된 인식</p>
              <p className="text-3xl font-bold text-slate-900 mt-1">{totalPerceptions}</p>
            </div>
            <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-4">
        {categories.map(category => {
          const isExpanded = expandedCategories.has(category.name)

          return (
            <div
              key={category.name}
              className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden"
            >
              {/* Category Header */}
              <button
                onClick={() => toggleCategory(category.name)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {isExpanded ? (
                    <ChevronDown className="h-5 w-5 text-slate-400" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-slate-400" />
                  )}
                  <h2 className="text-xl font-bold text-slate-900">
                    {category.name}
                  </h2>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm text-slate-600">세부 세계관</p>
                    <p className="text-lg font-semibold text-slate-900">
                      {category.worldviews.length}개
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-600">분석된 인식</p>
                    <p className="text-lg font-semibold text-blue-600">
                      {category.total_perceptions}개
                    </p>
                  </div>
                </div>
              </button>

              {/* Subcategories */}
              {isExpanded && (
                <div className="border-t border-slate-200 bg-slate-50">
                  <div className="p-6 space-y-4">
                    {category.worldviews.map(wv => (
                      <div
                        key={wv.id}
                        className="bg-white rounded-lg border border-slate-200 p-5 hover:shadow-md transition-shadow"
                      >
                        {/* Subcategory Header */}
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-slate-900 mb-2">
                              {wv.subcategory}
                            </h3>
                            <p className="text-slate-700 text-sm leading-relaxed">
                              {wv.summary}
                            </p>
                          </div>

                          <div className="ml-4 flex flex-col gap-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getEmotionColor(wv.primary_emotion)}`}>
                              {wv.primary_emotion}
                            </span>
                            {wv.has_deconstruction && (
                              <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-300">
                                반박 준비됨
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Logic Chain */}
                        <div className="mb-4 p-3 bg-slate-50 rounded border border-slate-200">
                          <p className="text-xs text-slate-600 mb-1">논리 연쇄</p>
                          <p className="text-sm font-mono text-slate-800">
                            {wv.logic_chain}
                          </p>
                        </div>

                        {/* Stats and Actions */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-6 text-sm">
                            <div>
                              <span className="text-slate-600">인식: </span>
                              <span className="font-semibold text-slate-900">
                                {wv.total_perceptions}개
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-600">강도: </span>
                              <span className="font-semibold text-blue-600">
                                {Math.round(wv.strength * 100)}%
                              </span>
                            </div>
                          </div>

                          <Link
                            href={`/worldviews/${wv.id}`}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                          >
                            상세 분석 →
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Empty State */}
      {categories.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          분석된 세계관이 없습니다.
        </div>
      )}
    </div>
  )
}
