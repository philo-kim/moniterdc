'use client'

/**
 * WorldviewCard - 개별 세계관 카드
 *
 * 세계관의 요약 정보와 강도 미터 표시
 */

import { useState } from 'react'
import Link from 'next/link'
import { TrendingUp, TrendingDown, Minus, SkullIcon, ChevronRight, AlertTriangle } from 'lucide-react'
import { StrengthMeter } from './StrengthMeter'

interface WorldviewCardProps {
  worldview: {
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
  }
}

export function WorldviewCard({ worldview }: WorldviewCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Trend icon and color
  const getTrendDisplay = (trend: string) => {
    switch (trend) {
      case 'rising':
        return {
          icon: <TrendingUp className="h-4 w-4" />,
          color: 'text-green-600',
          bg: 'bg-green-50',
          label: '상승'
        }
      case 'falling':
        return {
          icon: <TrendingDown className="h-4 w-4" />,
          color: 'text-orange-600',
          bg: 'bg-orange-50',
          label: '하락'
        }
      case 'dead':
        return {
          icon: <SkullIcon className="h-4 w-4" />,
          color: 'text-gray-600',
          bg: 'bg-gray-50',
          label: '소멸'
        }
      default:
        return {
          icon: <Minus className="h-4 w-4" />,
          color: 'text-yellow-600',
          bg: 'bg-yellow-50',
          label: '안정'
        }
    }
  }

  const trendDisplay = getTrendDisplay(worldview.trend)

  // Valence color
  const getValenceColor = (valence: string) => {
    switch (valence) {
      case 'negative':
        return 'text-red-600 bg-red-50'
      case 'positive':
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  // Format date
  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900 flex-1 pr-2">
            {worldview.title}
          </h3>
          <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${trendDisplay.bg} ${trendDisplay.color}`}>
            {trendDisplay.icon}
            <span>{trendDisplay.label}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span className="font-medium">{worldview.core_subject}</span>
          <span>→</span>
          <div className="flex flex-wrap gap-1">
            {worldview.core_attributes.slice(0, 3).map((attr, i) => (
              <span key={i} className={`px-2 py-0.5 rounded text-xs ${getValenceColor(worldview.overall_valence)}`}>
                {attr}
              </span>
            ))}
            {worldview.core_attributes.length > 3 && (
              <span className="text-xs text-gray-500">
                +{worldview.core_attributes.length - 3}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Frame */}
      <div className="px-4 py-3 bg-gray-50 text-sm text-gray-700 italic border-b border-gray-200">
        "{worldview.frame}"
      </div>

      {/* Strength Meters */}
      <div className="p-4 space-y-3">
        <StrengthMeter
          label="전체 강도"
          value={worldview.strength_overall}
          color="blue"
          showValue
        />

        {isExpanded && (
          <>
            <StrengthMeter
              label="인지적"
              value={worldview.strength_cognitive}
              color="purple"
            />
            <StrengthMeter
              label="시간적"
              value={worldview.strength_temporal}
              color="green"
            />
            <StrengthMeter
              label="사회적"
              value={worldview.strength_social}
              color="orange"
            />
            <StrengthMeter
              label="구조적"
              value={worldview.strength_structural}
              color="red"
            />
          </>
        )}

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs text-blue-600 hover:text-blue-800"
        >
          {isExpanded ? '간단히 보기' : '세부 강도 보기'}
        </button>
      </div>

      {/* Stats */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div className="text-gray-600">인식 개수</div>
            <div className="font-semibold text-gray-900">
              {worldview.total_perceptions}
            </div>
          </div>
          <div>
            <div className="text-gray-600">콘텐츠</div>
            <div className="font-semibold text-gray-900">
              {worldview.total_contents}
            </div>
          </div>
          <div>
            <div className="text-gray-600">최초 발견</div>
            <div className="font-semibold text-gray-900">
              {formatDate(worldview.first_seen)}
            </div>
          </div>
          <div>
            <div className="text-gray-600">최근 발견</div>
            <div className="font-semibold text-gray-900">
              {formatDate(worldview.last_seen)}
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-gray-200 flex gap-2">
        <Link
          href={`/worldviews/${worldview.id}`}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          상세 보기
          <ChevronRight className="h-4 w-4" />
        </Link>
        <Link
          href={`/worldviews/${worldview.id}/deconstruct`}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          <AlertTriangle className="h-4 w-4" />
          해체
        </Link>
      </div>
    </div>
  )
}
