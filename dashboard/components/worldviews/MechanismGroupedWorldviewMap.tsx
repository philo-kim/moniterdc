'use client'

/**
 * MechanismGroupedWorldviewMap - v2.0 메커니즘 중심 세계관 지도
 *
 * 핵심: 주제가 아닌 사고 구조로 그룹화
 * Category/Subcategory (X) → Mechanism Pattern (O)
 */

import { useState, useEffect } from 'react'
import { ChevronDown, ChevronRight, Users, TrendingUp, Brain } from 'lucide-react'
import Link from 'next/link'
import { MechanismList, type MechanismType, MechanismBadge } from './MechanismBadge'

interface Worldview {
  id: string
  title: string
  description: string
  core_subject?: string
  core_attributes?: MechanismType[]
  total_perceptions: number
  strength_overall: number
}

interface MechanismGroup {
  mechanism: MechanismType
  worldviews: Worldview[]
  total_perceptions: number
  unique_actors: string[]
}

const MECHANISM_ORDER: MechanismType[] = [
  '즉시_단정',
  '역사_투사',
  '필연적_인과',
  '네트워크_추론',
  '표면_부정'
]

export function MechanismGroupedWorldviewMap() {
  const [expandedMechanisms, setExpandedMechanisms] = useState<Set<MechanismType>>(
    new Set(['즉시_단정', '네트워크_추론'])
  )
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
        <p className="mt-4 text-slate-600">메커니즘 분석 로딩 중...</p>
      </div>
    )
  }

  const worldviews: Worldview[] = (data?.worldviews || []).map((wv: any) => ({
    id: wv.id,
    title: wv.title,
    description: wv.description,
    core_subject: wv.core_subject,
    core_attributes: wv.core_attributes as MechanismType[],
    total_perceptions: wv.total_perceptions || 0,
    strength_overall: wv.strength_overall || 0
  }))

  // 메커니즘별로 그룹화
  const mechanismGroups: MechanismGroup[] = []
  const mechanismMap = new Map<MechanismType, MechanismGroup>()

  // 각 메커니즘에 대해 그룹 생성
  MECHANISM_ORDER.forEach(mechanism => {
    mechanismMap.set(mechanism, {
      mechanism,
      worldviews: [],
      total_perceptions: 0,
      unique_actors: []
    })
  })

  // 세계관을 메커니즘별로 분류
  worldviews.forEach(wv => {
    if (wv.core_attributes && wv.core_attributes.length > 0) {
      // 주요 메커니즘 (첫 번째)에만 배치
      const primaryMechanism = wv.core_attributes[0]
      const group = mechanismMap.get(primaryMechanism)
      if (group) {
        group.worldviews.push(wv)
        group.total_perceptions += wv.total_perceptions
        if (wv.core_subject && !group.unique_actors.includes(wv.core_subject)) {
          group.unique_actors.push(wv.core_subject)
        }
      }
    }
  })

  mechanismMap.forEach(group => mechanismGroups.push(group))

  const toggleMechanism = (mechanism: MechanismType) => {
    const newExpanded = new Set(expandedMechanisms)
    if (newExpanded.has(mechanism)) {
      newExpanded.delete(mechanism)
    } else {
      newExpanded.add(mechanism)
    }
    setExpandedMechanisms(newExpanded)
  }

  const totalPerceptions = mechanismGroups.reduce((sum, g) => sum + g.total_perceptions, 0)
  const totalWorldviews = worldviews.length

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow-sm p-6 border-2 border-purple-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-700 font-medium">사고 메커니즘</p>
              <p className="text-3xl font-bold text-purple-900 mt-1">5개</p>
              <p className="text-xs text-purple-600 mt-1">v2.0 핵심 패턴</p>
            </div>
            <div className="h-12 w-12 bg-purple-200 rounded-lg flex items-center justify-center">
              <Brain className="h-6 w-6 text-purple-700" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm p-6 border-2 border-blue-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-700 font-medium">발견된 세계관</p>
              <p className="text-3xl font-bold text-blue-900 mt-1">{totalWorldviews}개</p>
              <p className="text-xs text-blue-600 mt-1">살아있는 시스템</p>
            </div>
            <div className="h-12 w-12 bg-blue-200 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-blue-700" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow-sm p-6 border-2 border-green-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-700 font-medium">분석된 담론</p>
              <p className="text-3xl font-bold text-green-900 mt-1">{totalPerceptions}개</p>
              <p className="text-xs text-green-600 mt-1">구조 추출 완료</p>
            </div>
            <div className="h-12 w-12 bg-green-200 rounded-lg flex items-center justify-center">
              <Users className="h-6 w-6 text-green-700" />
            </div>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-300 rounded-xl p-5">
        <h3 className="text-sm font-bold text-amber-900 mb-2">💡 메커니즘 기반 분석이란?</h3>
        <p className="text-sm text-amber-800 leading-relaxed mb-2">
          v2.0은 <strong>"무엇에 대한 이야기"</strong>가 아니라 <strong>"어떻게 생각하는가"</strong>로 세계관을 분류합니다.
          이민, 범죄, 사법 등 주제가 달라도 같은 사고 패턴을 쓰면 같은 세계관입니다.
        </p>
        <p className="text-xs text-amber-700 italic">
          예: "증거 없이 즉시 단정 + 과거 투사"는 어떤 주제에서든 반복됩니다.
        </p>
      </div>

      {/* Mechanism Groups */}
      <div className="space-y-4">
        {mechanismGroups.map(group => {
          const isExpanded = expandedMechanisms.has(group.mechanism)

          return (
            <div
              key={group.mechanism}
              className="bg-white rounded-xl shadow-md border-2 border-slate-200 overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* Mechanism Header */}
              <button
                onClick={() => toggleMechanism(group.mechanism)}
                className="w-full px-6 py-5 flex items-center justify-between hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1">
                  {isExpanded ? (
                    <ChevronDown className="h-6 w-6 text-slate-400" />
                  ) : (
                    <ChevronRight className="h-6 w-6 text-slate-400" />
                  )}

                  <MechanismBadge mechanism={group.mechanism} size="lg" showTooltip={false} />

                  <div className="flex items-center gap-6 ml-6">
                    <div className="text-left">
                      <p className="text-xs text-slate-500">세계관</p>
                      <p className="text-lg font-bold text-slate-900">
                        {group.worldviews.length}개
                      </p>
                    </div>
                    <div className="text-left">
                      <p className="text-xs text-slate-500">행위자</p>
                      <p className="text-lg font-bold text-indigo-700">
                        {group.unique_actors.length}명
                      </p>
                    </div>
                    <div className="text-left">
                      <p className="text-xs text-slate-500">담론</p>
                      <p className="text-lg font-bold text-blue-600">
                        {group.total_perceptions}개
                      </p>
                    </div>
                  </div>
                </div>
              </button>

              {/* Worldviews */}
              {isExpanded && (
                <div className="border-t-2 border-slate-200 bg-slate-50">
                  <div className="p-6 space-y-4">
                    {group.worldviews.length === 0 ? (
                      <p className="text-center text-slate-500 py-8">
                        이 메커니즘을 주로 사용하는 세계관이 아직 발견되지 않았습니다
                      </p>
                    ) : (
                      group.worldviews.map(wv => (
                        <div
                          key={wv.id}
                          className="bg-white rounded-lg border-2 border-slate-200 p-5 hover:shadow-lg transition-all hover:border-blue-300"
                        >
                          <div className="mb-3">
                            <h3 className="text-lg font-bold text-slate-900 mb-2">
                              {wv.title}
                            </h3>
                            <p className="text-sm text-slate-700 leading-relaxed mb-3">
                              {wv.description}
                            </p>

                            {/* Actor */}
                            {wv.core_subject && (
                              <div className="flex items-center gap-2 mb-3">
                                <Users className="h-4 w-4 text-indigo-600" />
                                <span className="text-xs font-medium text-slate-600">핵심 행위자:</span>
                                <span className="text-sm font-bold text-indigo-900 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200">
                                  {wv.core_subject}
                                </span>
                              </div>
                            )}

                            {/* All Mechanisms */}
                            {wv.core_attributes && wv.core_attributes.length > 0 && (
                              <div className="mb-3">
                                <p className="text-xs font-medium text-slate-600 mb-2">사용하는 메커니즘:</p>
                                <MechanismList mechanisms={wv.core_attributes} size="sm" showTooltip={true} />
                              </div>
                            )}
                          </div>

                          <div className="flex items-center justify-between pt-3 border-t border-slate-200">
                            <div className="flex items-center gap-4 text-xs">
                              <div>
                                <span className="text-slate-600">담론: </span>
                                <span className="font-bold text-slate-900">{wv.total_perceptions}개</span>
                              </div>
                            </div>

                            <Link
                              href={`/worldviews/${wv.id}`}
                              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all text-sm font-bold shadow-md hover:shadow-lg"
                            >
                              사고 구조 분석 →
                            </Link>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
