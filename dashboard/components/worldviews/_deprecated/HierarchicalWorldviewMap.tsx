'use client'

/**
 * HierarchicalWorldviewMap - 계층형 세계관 지도
 *
 * Category > Subcategory 구조로 세계관을 표시
 * 3개 주요 카테고리로 그룹화
 */

import { useState, useEffect } from 'react'
import { ChevronDown, ChevronRight, MessageSquare, Target, AlertTriangle, User } from 'lucide-react'
import Link from 'next/link'
import { MechanismList, type MechanismType } from '../MechanismBadge'

interface Worldview {
  id: string
  title: string
  frame: string
  total_perceptions: number
  strength_overall: number
  core_subject?: string
  core_attributes?: MechanismType[]
}

interface ParsedFrame {
  category: string
  subcategory: string
  description: string
  priority?: 'high' | 'medium' | 'low'
  metadata?: {
    merged_from?: string[]
    estimated_count?: number
  }
}

interface CategoryGroup {
  name: string
  worldviews: {
    id: string
    title: string
    description: string
    priority?: 'high' | 'medium' | 'low'
    total_perceptions: number
    strength: number
    core_subject?: string
    core_mechanisms?: MechanismType[]
  }[]
  total_perceptions: number
}

export function HierarchicalWorldviewMap() {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['민주당/좌파에 대한 인식', '외부 세력의 위협']))
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true)
        const res = await fetch('/api/worldviews?limit=100')
        if (!res.ok) {
          throw new Error('Failed to fetch worldviews')
        }
        const json = await res.json()
        setData(json)
        setError(null)
      } catch (err) {
        setError(err as Error)
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [])

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

  // Group by category
  const categories: CategoryGroup[] = []
  const categoryMap = new Map<string, CategoryGroup>()

  worldviews.forEach(wv => {
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
        title: wv.title,
        description: frame.description,
        priority: frame.priority,
        total_perceptions: wv.total_perceptions,
        strength: wv.strength_overall,
        core_subject: wv.core_subject,
        core_mechanisms: wv.core_attributes as MechanismType[]
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
              <p className="text-3xl font-bold text-slate-900 mt-1">{worldviews.length}</p>
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
                        {/* Worldview Header */}
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-slate-900 mb-2">
                              {wv.title}
                            </h3>
                            <p className="text-slate-700 text-sm leading-relaxed mb-3">
                              {wv.description}
                            </p>

                            {/* Actor (행위자) */}
                            {wv.core_subject && (
                              <div className="flex items-center gap-2 mb-3">
                                <User className="h-4 w-4 text-indigo-600" />
                                <span className="text-xs font-medium text-slate-600">행위자:</span>
                                <span className="text-sm font-semibold text-indigo-900 bg-indigo-50 px-2 py-0.5 rounded">
                                  {wv.core_subject}
                                </span>
                              </div>
                            )}

                            {/* 핵심 메커니즘 */}
                            {wv.core_mechanisms && wv.core_mechanisms.length > 0 && (
                              <div className="space-y-1">
                                <p className="text-xs font-medium text-slate-600 mb-1">사고 메커니즘:</p>
                                <MechanismList
                                  mechanisms={wv.core_mechanisms}
                                  size="sm"
                                  showTooltip={true}
                                />
                              </div>
                            )}
                          </div>

                          {wv.priority && (
                            <div className="ml-4">
                              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                                wv.priority === 'high' ? 'bg-blue-100 text-blue-800 border-blue-300' :
                                wv.priority === 'medium' ? 'bg-purple-100 text-purple-800 border-purple-300' :
                                'bg-slate-100 text-slate-800 border-slate-300'
                              }`}>
                                {wv.priority === 'high' ? '이해 우선순위: 높음' : wv.priority === 'medium' ? '이해 우선순위: 중간' : '이해 우선순위: 낮음'}
                              </span>
                            </div>
                          )}
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
