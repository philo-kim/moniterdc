'use client'

import { HierarchicalWorldviewMap } from '@/components/worldviews/HierarchicalWorldviewMap'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-slate-900 mb-3">
            담론 세계관 분석 시스템
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            같은 사건을 보고도 완전히 다르게 해석하는 이유를 이해하기 위한 인식론적 분석 도구
          </p>
          <p className="text-sm text-slate-500 mt-3">
            &ldquo;상대방은 틀린 게 아니라, 다른 세계를 산다&rdquo;
          </p>
        </header>

        {/* Main Content */}
        <HierarchicalWorldviewMap />
      </div>
    </div>
  )
}
