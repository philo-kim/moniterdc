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
import { MechanismList, type MechanismType, MechanismBadge } from '../MechanismBadge'

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
    <div className="space-y-4">
      {/* 간단한 통계 */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-6">
            <div>
              <span className="text-slate-600">세계관 </span>
              <span className="font-bold text-slate-900">{totalWorldviews}개</span>
            </div>
            <div>
              <span className="text-slate-600">담론 </span>
              <span className="font-bold text-slate-900">{totalPerceptions}개</span>
            </div>
          </div>
        </div>
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
                                <span className="text-sm font-bold text-indigo-900">
                                  {wv.core_subject}
                                </span>
                              </div>
                            )}

                            {/* All Mechanisms - 2개 이상일 때만 표시 */}
                            {wv.core_attributes && wv.core_attributes.length > 1 && (
                              <div className="mb-3">
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
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                            >
                              상세보기
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
