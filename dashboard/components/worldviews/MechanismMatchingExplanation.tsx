'use client'

/**
 * MechanismMatchingExplanation - 메커니즘 기반 매칭 설명
 *
 * v2.0의 핵심: 주제가 아닌 사고 구조로 세계관을 묶는다
 */

import { Target, Percent } from 'lucide-react'
import { MechanismList, type MechanismType } from './MechanismBadge'

interface MechanismMatchingExplanationProps {
  coreSubject?: string
  coreMechanisms?: MechanismType[]
}

export function MechanismMatchingExplanation({
  coreSubject,
  coreMechanisms
}: MechanismMatchingExplanationProps) {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl shadow-sm border-2 border-blue-200 p-6 mb-6">
      <div className="flex items-center gap-2 mb-4">
        <Target className="h-6 w-6 text-blue-600" />
        <h2 className="text-xl font-bold text-slate-900">
          🎯 메커니즘 기반 매칭
        </h2>
      </div>

      <div className="bg-white rounded-lg p-5 mb-4 border border-blue-200">
        <p className="text-sm text-slate-700 leading-relaxed mb-4">
          v2.0 시스템은 <strong className="text-blue-800">주제가 아닌 사고 구조</strong>로 세계관을 정의합니다.
          이민, 범죄, 사법처럼 주제가 달라도 <strong className="text-purple-800">같은 사고 방식</strong>을 쓰면 같은 세계관입니다.
        </p>

        <div className="space-y-3">
          {/* Actor 50% */}
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-24 pt-1">
              <div className="flex items-center gap-1">
                <Percent className="h-4 w-4 text-indigo-600" />
                <span className="text-sm font-bold text-indigo-900">50%</span>
              </div>
              <span className="text-xs text-slate-600">Actor</span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-slate-900 mb-1">행위자 구조</p>
              <p className="text-xs text-slate-600 leading-relaxed">
                <strong>누가</strong> 무엇을 <strong>왜</strong> <strong>어떻게</strong> 하는가?
              </p>
              {coreSubject && (
                <div className="mt-2 inline-block bg-indigo-100 px-3 py-1 rounded-lg border border-indigo-300">
                  <span className="text-xs font-semibold text-indigo-900">
                    이 세계관의 핵심 행위자: {coreSubject}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Mechanism 30% */}
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-24 pt-1">
              <div className="flex items-center gap-1">
                <Percent className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-bold text-purple-900">30%</span>
              </div>
              <span className="text-xs text-slate-600">Mechanism</span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-slate-900 mb-1">사고 메커니즘</p>
              <p className="text-xs text-slate-600 leading-relaxed mb-2">
                어떤 사고 패턴을 반복적으로 사용하는가?
              </p>
              {coreMechanisms && coreMechanisms.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-slate-600 mb-1">이 세계관의 핵심 메커니즘:</p>
                  <MechanismList mechanisms={coreMechanisms} size="sm" showTooltip={true} />
                </div>
              )}
            </div>
          </div>

          {/* Logic 20% */}
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-24 pt-1">
              <div className="flex items-center gap-1">
                <Percent className="h-4 w-4 text-green-600" />
                <span className="text-sm font-bold text-green-900">20%</span>
              </div>
              <span className="text-xs text-slate-600">Logic</span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-slate-900 mb-1">논리 연쇄</p>
              <p className="text-xs text-slate-600 leading-relaxed">
                사실 → 해석 → 결론의 흐름이 얼마나 유사한가?
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <p className="text-xs text-amber-900 leading-relaxed">
          <strong className="font-bold">💡 왜 이렇게 하나요?</strong><br/>
          &ldquo;이민 = 범죄&rdquo;라는 주제로 묶으면 표면만 보입니다.
          하지만 <strong>&ldquo;증거 없이 즉시 단정 + 과거 투사 + 네트워크로 확장&rdquo;</strong>이라는 사고 구조로 묶으면,
          이민, 범죄, 사법, 경제 등 <strong>모든 주제</strong>에서 <strong>똑같은 패턴</strong>을 발견할 수 있습니다.
          이것이 진짜 &ldquo;세계관&rdquo;입니다.
        </p>
      </div>
    </div>
  )
}
