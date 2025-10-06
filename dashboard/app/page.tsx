'use client'

import { HierarchicalWorldviewMap } from '@/components/worldviews/HierarchicalWorldviewMap'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-slate-900 mb-3">
            DC Gallery 세계관 분석 시스템
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            DC Gallery 정치 담론의 세계관 구조를 분석하고,
            여당 지지자들이 이해할 수 있도록 맥락과 반박 논리를 제공합니다
          </p>
        </header>

        {/* Main Content */}
        <HierarchicalWorldviewMap />
      </div>
    </div>
  )
}
