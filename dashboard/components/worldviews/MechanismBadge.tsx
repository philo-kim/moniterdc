'use client'

/**
 * MechanismBadge - 5대 사고 메커니즘 시각화
 *
 * v2.0의 핵심: 주제가 아닌 사고 구조 분석
 */

import { useState } from 'react'
import { Info } from 'lucide-react'

export type MechanismType =
  | '즉시_단정'
  | '역사_투사'
  | '필연적_인과'
  | '네트워크_추론'
  | '표면_부정'

interface MechanismConfig {
  label: string
  color: string
  bg: string
  border: string
  description: string
  example: string
  icon: string
}

const MECHANISM_CONFIG: Record<MechanismType, MechanismConfig> = {
  '즉시_단정': {
    label: '즉시 단정',
    color: 'text-red-700',
    bg: 'bg-red-50',
    border: 'border-red-300',
    icon: '⚡',
    description: '증거나 검증 없이 바로 결론을 내리는 사고 패턴',
    example: '예: "민주당이 정보를 알았다" → 즉시 "불법 사찰이다"로 단정'
  },
  '역사_투사': {
    label: '역사 투사',
    color: 'text-purple-700',
    bg: 'bg-purple-50',
    border: 'border-purple-300',
    icon: '🔄',
    description: '과거 사건을 현재에 그대로 투영하는 사고 패턴',
    example: '예: "과거 독재 시절 X가 일어났다" → "지금도 X가 일어날 것이다"'
  },
  '필연적_인과': {
    label: '필연적 인과',
    color: 'text-blue-700',
    bg: 'bg-blue-50',
    border: 'border-blue-300',
    icon: '➡️',
    description: '우연이나 다른 가능성을 배제하고 인과를 필연으로 해석',
    example: '예: "A 사건 후 B 발생" → "A가 B를 의도적으로 일으켰다"'
  },
  '네트워크_추론': {
    label: '네트워크 추론',
    color: 'text-green-700',
    bg: 'bg-green-50',
    border: 'border-green-300',
    icon: '🕸️',
    description: '개별 점들을 연결해 거대한 네트워크/음모로 확장',
    example: '예: "A와 B가 같은 장소에 있었다" → "거대한 카르텔이 존재한다"'
  },
  '표면_부정': {
    label: '표면 부정',
    color: 'text-orange-700',
    bg: 'bg-orange-50',
    border: 'border-orange-300',
    icon: '🚫',
    description: '공식 설명이나 표면적 이유를 즉시 거부하고 숨은 의도 탐색',
    example: '예: "정상적인 정치 활동이다" → "그건 표면이고 실제는 독재 시도다"'
  }
}

interface MechanismBadgeProps {
  mechanism: MechanismType
  size?: 'sm' | 'md' | 'lg'
  showTooltip?: boolean
}

export function MechanismBadge({
  mechanism,
  size = 'md',
  showTooltip = true
}: MechanismBadgeProps) {
  const [showInfo, setShowInfo] = useState(false)
  const config = MECHANISM_CONFIG[mechanism]

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5'
  }

  return (
    <div className="relative inline-block">
      <span
        className={`
          inline-flex items-center gap-1 rounded-full font-medium border
          ${config.bg} ${config.color} ${config.border}
          ${sizeClasses[size]}
          ${showTooltip ? 'cursor-help' : ''}
        `}
        onMouseEnter={() => showTooltip && setShowInfo(true)}
        onMouseLeave={() => showTooltip && setShowInfo(false)}
      >
        <span>{config.icon}</span>
        <span>{config.label}</span>
        {showTooltip && <Info className="h-3 w-3 opacity-60" />}
      </span>

      {/* Tooltip */}
      {showTooltip && showInfo && (
        <div className="absolute z-50 w-80 p-4 mt-2 bg-white border-2 border-slate-300 rounded-lg shadow-xl left-0">
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{config.icon}</span>
              <h4 className="font-bold text-slate-900">{config.label}</h4>
            </div>
            <p className="text-sm text-slate-700 leading-relaxed">
              {config.description}
            </p>
            <div className="pt-2 mt-2 border-t border-slate-200">
              <p className="text-xs text-slate-600 italic">
                {config.example}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

interface MechanismListProps {
  mechanisms: MechanismType[]
  size?: 'sm' | 'md' | 'lg'
  showTooltip?: boolean
}

export function MechanismList({
  mechanisms,
  size = 'md',
  showTooltip = true
}: MechanismListProps) {
  if (!mechanisms || mechanisms.length === 0) {
    return null
  }

  return (
    <div className="flex flex-wrap gap-2">
      {mechanisms.map((mechanism) => (
        <MechanismBadge
          key={mechanism}
          mechanism={mechanism}
          size={size}
          showTooltip={showTooltip}
        />
      ))}
    </div>
  )
}
