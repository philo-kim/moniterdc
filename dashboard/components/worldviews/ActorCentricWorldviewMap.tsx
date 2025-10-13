'use client'

/**
 * ActorCentricWorldviewMap - Actor 중심 세계관 지도
 *
 * 사용자 질문: "X는 왜 그렇게 생각하나?"
 * Actor → 사고방식(메커니즘) → 구체적 패턴
 */

import { useState, useEffect } from 'react'
import { ChevronDown, ChevronRight, Users, Brain } from 'lucide-react'
import Link from 'next/link'
import { MechanismList, type MechanismType } from './MechanismBadge'

interface Worldview {
  id: string
  title: string
  description: string
  core_subject?: string
  core_attributes?: MechanismType[]
  total_perceptions: number
}

interface ActorGroup {
  actor: string
  worldviews: Worldview[]
  total_perceptions: number
  all_mechanisms: MechanismType[]
}

export function ActorCentricWorldviewMap() {
  const [expandedActors, setExpandedActors] = useState<Set<string>>(new Set())
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

  const worldviews: Worldview[] = (data?.worldviews || []).map((wv: any) => ({
    id: wv.id,
    title: wv.title,
    description: wv.description,
    core_subject: wv.core_subject,
    core_attributes: wv.core_attributes as MechanismType[],
    total_perceptions: wv.total_perceptions || 0
  })).filter((wv: Worldview) => wv.core_subject && wv.core_attributes && wv.core_attributes.length > 0)

  // Actor별로 그룹화
  const actorGroups: ActorGroup[] = []
  const actorMap = new Map<string, ActorGroup>()

  worldviews.forEach(wv => {
    if (!wv.core_subject) return

    if (!actorMap.has(wv.core_subject)) {
      actorMap.set(wv.core_subject, {
        actor: wv.core_subject,
        worldviews: [],
        total_perceptions: 0,
        all_mechanisms: []
      })
    }

    const group = actorMap.get(wv.core_subject)!
    group.worldviews.push(wv)
    group.total_perceptions += wv.total_perceptions

    // 메커니즘 수집 (중복 제거)
    if (wv.core_attributes) {
      wv.core_attributes.forEach(m => {
        if (!group.all_mechanisms.includes(m)) {
          group.all_mechanisms.push(m)
        }
      })
    }
  })

  actorMap.forEach(group => actorGroups.push(group))

  // 담론 수로 정렬
  actorGroups.sort((a, b) => b.total_perceptions - a.total_perceptions)

  const toggleActor = (actor: string) => {
    const newExpanded = new Set(expandedActors)
    if (newExpanded.has(actor)) {
      newExpanded.delete(actor)
    } else {
      newExpanded.add(actor)
    }
    setExpandedActors(newExpanded)
  }

  const totalPerceptions = actorGroups.reduce((sum, g) => sum + g.total_perceptions, 0)
  const totalWorldviews = worldviews.length

  return (
    <div className="space-y-4">
      {/* 간단한 통계 */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div className="flex items-center gap-6 text-sm">
          <div>
            <span className="text-slate-600">세계관 </span>
            <span className="font-bold text-slate-900">{totalWorldviews}개</span>
          </div>
          <div>
            <span className="text-slate-600">담론 </span>
            <span className="font-bold text-slate-900">{totalPerceptions}개</span>
          </div>
          <div>
            <span className="text-slate-600">행위자 </span>
            <span className="font-bold text-slate-900">{actorGroups.length}개</span>
          </div>
        </div>
      </div>

      {/* Actor Groups */}
      <div className="space-y-3">
        {actorGroups.map(group => {
          const isExpanded = expandedActors.has(group.actor)

          return (
            <div
              key={group.actor}
              className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden"
            >
              {/* Actor Header */}
              <button
                onClick={() => toggleActor(group.actor)}
                className="w-full px-5 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1">
                  {isExpanded ? (
                    <ChevronDown className="h-5 w-5 text-slate-400 flex-shrink-0" />
                  ) : (
                    <ChevronRight className="h-5 w-5 text-slate-400 flex-shrink-0" />
                  )}

                  <Users className="h-5 w-5 text-indigo-600 flex-shrink-0" />

                  <div className="flex-1 text-left">
                    <h3 className="text-lg font-bold text-slate-900">
                      {group.actor}
                    </h3>
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      {group.all_mechanisms.map(m => (
                        <span key={m} className="text-xs px-2 py-0.5 bg-slate-100 text-slate-700 rounded">
                          {m.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-sm">
                    <div className="text-right">
                      <p className="text-xs text-slate-500">패턴</p>
                      <p className="text-base font-bold text-slate-900">
                        {group.worldviews.length}개
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500">담론</p>
                      <p className="text-base font-bold text-blue-600">
                        {group.total_perceptions}개
                      </p>
                    </div>
                  </div>
                </div>
              </button>

              {/* Worldviews */}
              {isExpanded && (
                <div className="border-t border-slate-200 bg-slate-50">
                  <div className="p-5 space-y-3">
                    {group.worldviews.map(wv => (
                      <div
                        key={wv.id}
                        className="bg-white rounded-lg border border-slate-200 p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <h4 className="font-semibold text-slate-900 mb-2">
                              {wv.title}
                            </h4>
                            <p className="text-sm text-slate-600 mb-3">
                              {wv.description}
                            </p>

                            <div className="flex items-center gap-4 text-xs text-slate-600">
                              <div className="flex items-center gap-1">
                                <Brain className="h-3 w-3" />
                                <span>{wv.core_attributes?.length || 0}개 메커니즘</span>
                              </div>
                              <div>
                                담론 {wv.total_perceptions}개
                              </div>
                            </div>
                          </div>

                          <Link
                            href={`/worldviews/${wv.id}`}
                            className="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                          >
                            상세보기
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
      {actorGroups.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          분석된 세계관이 없습니다.
        </div>
      )}
    </div>
  )
}
