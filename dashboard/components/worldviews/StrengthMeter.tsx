'use client'

/**
 * StrengthMeter - 강도 표시 컴포넌트
 *
 * 0-1 범위의 강도 값을 시각화
 */

interface StrengthMeterProps {
  label: string
  value: number
  color?: 'blue' | 'purple' | 'green' | 'orange' | 'red'
  showValue?: boolean
}

export function StrengthMeter({
  label,
  value,
  color = 'blue',
  showValue = false
}: StrengthMeterProps) {
  // Clamp value between 0 and 1
  const clampedValue = Math.max(0, Math.min(1, value))
  const percentage = Math.round(clampedValue * 100)

  // Color classes
  const colorClasses = {
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    green: 'bg-green-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500'
  }

  const bgColor = colorClasses[color]

  // Opacity based on value
  const getOpacity = (val: number) => {
    if (val < 0.3) return 'opacity-40'
    if (val < 0.6) return 'opacity-70'
    return 'opacity-100'
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-gray-700">{label}</span>
        {showValue && (
          <span className="text-xs font-semibold text-gray-900">
            {percentage}%
          </span>
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full ${bgColor} ${getOpacity(clampedValue)} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
