'use client'

import { MechanismGroupedWorldviewMap } from '@/components/worldviews/MechanismGroupedWorldviewMap'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-12 text-center">
          <div className="inline-block mb-4">
            <span className="px-4 py-1.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-bold rounded-full">
              v2.0 메커니즘 기반 분석
            </span>
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-3">
            담론 세계관 분석 시스템
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-2">
            같은 사건을 보고도 완전히 다르게 해석하는 이유를 이해하기 위한 인식론적 분석 도구
          </p>
          <p className="text-sm text-slate-500 mt-3 mb-4">
            &ldquo;상대방은 틀린 게 아니라, 다른 세계를 산다&rdquo;
          </p>

          {/* v2.0 핵심 가치 */}
          <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-xl p-6 max-w-4xl mx-auto">
            <h2 className="text-sm font-bold text-blue-900 mb-3">🎯 v2.0의 핵심: 주제가 아닌 사고 구조 분석</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              <div className="bg-white rounded-lg p-3 border border-blue-100">
                <p className="text-xs font-bold text-blue-800 mb-1">5대 사고 메커니즘</p>
                <p className="text-xs text-slate-600">
                  즉시 단정, 역사 투사, 필연적 인과, 네트워크 추론, 표면 부정
                </p>
              </div>
              <div className="bg-white rounded-lg p-3 border border-purple-100">
                <p className="text-xs font-bold text-purple-800 mb-1">Actor 구조 분석</p>
                <p className="text-xs text-slate-600">
                  누가(Subject), 왜(Purpose), 어떻게(Methods)
                </p>
              </div>
              <div className="bg-white rounded-lg p-3 border border-green-100">
                <p className="text-xs font-bold text-green-800 mb-1">Logic Chain 추적</p>
                <p className="text-xs text-slate-600">
                  사고의 흐름과 건너뛴 단계 시각화
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <MechanismGroupedWorldviewMap />
      </div>
    </div>
  )
}
