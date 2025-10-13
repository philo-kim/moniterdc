'use client'

import { MechanismGroupedWorldviewMap } from '@/components/worldviews/MechanismGroupedWorldviewMap'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header - 간결화 */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                담론 세계관 분석
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                사고 메커니즘 기반 분류
              </p>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <MechanismGroupedWorldviewMap />
      </div>
    </div>
  )
}
