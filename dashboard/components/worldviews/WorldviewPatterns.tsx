'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface Pattern {
  id: string
  text: string
  strength: number
  appearance_count: number
  status: string
}

interface WorldviewPatternsProps {
  worldviewId: string
  patterns: {
    surface: Pattern[]
    implicit: Pattern[]
    deep: Pattern[]
  }
}

const LayerConfig = {
  surface: {
    title: '표면층',
    subtitle: '자주 언급되는 사건들',
    description: '빠르게 변화 (7일 주기)',
    color: 'blue',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-900',
    icon: '🔵',
    defaultShow: 10
  },
  implicit: {
    title: '암묵층',
    subtitle: '전제되는 가정들',
    description: '중간 속도 변화 (30일 주기)',
    color: 'amber',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    textColor: 'text-amber-900',
    icon: '🟡',
    defaultShow: 5
  },
  deep: {
    title: '심층',
    subtitle: '근본 믿음',
    description: '천천히 변화 (180일 주기)',
    color: 'red',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-900',
    icon: '🔴',
    defaultShow: 3
  }
}

function PatternLayer({
  layer,
  patterns
}: {
  layer: 'surface' | 'implicit' | 'deep'
  patterns: Pattern[]
}) {
  const [expanded, setExpanded] = useState(false)
  const config = LayerConfig[layer]

  const activePatterns = patterns.filter(p => p.status === 'active' || p.status === 'fading')
  const sortedPatterns = [...activePatterns].sort((a, b) => b.strength - a.strength)

  const displayPatterns = expanded ? sortedPatterns : sortedPatterns.slice(0, config.defaultShow)
  const hasMore = sortedPatterns.length > config.defaultShow

  if (sortedPatterns.length === 0) {
    return (
      <div className={`${config.bgColor} ${config.borderColor} border rounded-lg p-4`}>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <h3 className={`font-bold ${config.textColor}`}>{config.title}</h3>
            <p className="text-sm text-gray-600">{config.subtitle}</p>
          </div>
        </div>
        <p className="text-sm text-gray-500 italic">패턴 없음</p>
      </div>
    )
  }

  // Calculate average strength
  const avgStrength = sortedPatterns.reduce((sum, p) => sum + p.strength, 0) / sortedPatterns.length

  return (
    <div className={`${config.bgColor} ${config.borderColor} border rounded-lg p-4`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <h3 className={`font-bold ${config.textColor}`}>{config.title}</h3>
            <p className="text-sm text-gray-600">{config.subtitle}</p>
          </div>
        </div>
        <div className="text-right text-sm">
          <div className={`font-semibold ${config.textColor}`}>{sortedPatterns.length}개 패턴</div>
          <div className="text-gray-600">평균 강도 {avgStrength.toFixed(1)}</div>
        </div>
      </div>

      {/* Description */}
      <p className="text-xs text-gray-500 mb-3">{config.description}</p>

      {/* Patterns list */}
      <div className="space-y-2">
        {displayPatterns.map((pattern, idx) => (
          <div
            key={pattern.id}
            className="bg-white rounded p-3 shadow-sm border border-gray-200"
          >
            <div className="flex items-start gap-2">
              <div className={`text-xs font-bold ${config.textColor} min-w-[20px]`}>
                {idx + 1}.
              </div>
              <div className="flex-1">
                <div className="text-sm text-gray-800 leading-relaxed mb-1">
                  {pattern.text}
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span className="font-semibold">강도 {pattern.strength.toFixed(1)}</span>
                  <span>•</span>
                  <span>{pattern.appearance_count}회 출현</span>
                  {pattern.status === 'fading' && (
                    <>
                      <span>•</span>
                      <span className="text-amber-600">약화 중</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Show more button */}
      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className={`w-full mt-3 py-2 px-4 rounded ${config.bgColor} ${config.textColor} hover:opacity-80 transition-opacity flex items-center justify-center gap-2 text-sm font-medium`}
        >
          {expanded ? (
            <>
              접기
              <ChevronUp className="w-4 h-4" />
            </>
          ) : (
            <>
              더보기 - 전체 {sortedPatterns.length}개 패턴 보기
              <ChevronDown className="w-4 h-4" />
            </>
          )}
        </button>
      )}
    </div>
  )
}

export default function WorldviewPatterns({ worldviewId, patterns }: WorldviewPatternsProps) {
  return (
    <div className="space-y-4">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">이 세계관의 핵심 구조</h2>
        <p className="text-sm text-gray-600">
          강도가 높을수록 이 세계관에서 자주 반복되는 패턴입니다.
          표면층은 빠르게 변하고, 심층으로 갈수록 안정적인 패턴입니다.
        </p>
      </div>

      <PatternLayer layer="surface" patterns={patterns.surface} />
      <PatternLayer layer="implicit" patterns={patterns.implicit} />
      <PatternLayer layer="deep" patterns={patterns.deep} />
    </div>
  )
}
