'use client'

/**
 * InterpretationComparison - 해석 대비 컴포넌트
 *
 * "같은 사건을 다르게 해석하는 이유"를 시각화
 */

import { ArrowRight, Eye, Users } from 'lucide-react'

interface Example {
  case: string
  dc_interpretation: string
  normal_interpretation: string
  gap: string
}

interface InterpretationComparisonProps {
  examples: Example[]
  category: string
}

export function InterpretationComparison({ examples, category }: InterpretationComparisonProps) {
  if (!examples || examples.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-900 mb-2">
          해석 프레임워크 비교
        </h2>
        <p className="text-sm text-slate-600">
          같은 사건을 어떻게 다르게 해석하는가? - 세계관의 차이를 이해하기
        </p>
      </div>

      <div className="space-y-6">
        {examples.map((example, idx) => (
          <div key={idx} className="bg-slate-50 rounded-lg p-6 border border-slate-200">
            {/* 사건/사례 */}
            <div className="mb-6 pb-4 border-b border-slate-300">
              <div className="inline-block px-3 py-1 bg-slate-200 rounded-full mb-3">
                <span className="text-xs font-semibold text-slate-700">사건/사례</span>
              </div>
              <h3 className="text-lg font-bold text-slate-900">
                {example.case}
              </h3>
            </div>

            {/* 두 가지 해석 */}
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              {/* DC Gallery 해석 (세계관 A) */}
              <div className="bg-blue-50 rounded-lg p-4 border-2 border-blue-200">
                <div className="flex items-center gap-2 mb-3">
                  <Eye className="h-5 w-5 text-blue-600" />
                  <h4 className="font-bold text-blue-900">이 세계관의 해석</h4>
                </div>
                <p className="text-sm text-blue-800 leading-relaxed">
                  {example.dc_interpretation}
                </p>
              </div>

              {/* 일반적 해석 (세계관 B) */}
              <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
                <div className="flex items-center gap-2 mb-3">
                  <Users className="h-5 w-5 text-green-600" />
                  <h4 className="font-bold text-green-900">일반적 해석</h4>
                </div>
                <p className="text-sm text-green-800 leading-relaxed">
                  {example.normal_interpretation}
                </p>
              </div>
            </div>

            {/* 해석 차이의 핵심 */}
            <div className="bg-amber-50 rounded-lg p-4 border-2 border-amber-200">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-1">
                  <ArrowRight className="h-5 w-5 text-amber-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-amber-900 mb-2">
                    해석 차이의 핵심
                  </h4>
                  <p className="text-sm text-amber-800 leading-relaxed">
                    {example.gap}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 설명 */}
      <div className="mt-6 pt-6 border-t border-slate-200">
        <p className="text-sm text-slate-600 leading-relaxed">
          💡 <span className="font-semibold">왜 이렇게 다를까요?</span>
          {' '}같은 사건을 보더라도 <span className="font-semibold">어떤 세계관</span>으로
          해석하는가에 따라 완전히 다른 의미를 도출합니다.
          표면적 사실 확인만으로는 이 차이를 좁힐 수 없습니다.
          <span className="font-semibold text-blue-600"> 심층 세계관을 이해해야만 대화가 가능</span>합니다.
        </p>
      </div>
    </div>
  )
}
