'use client'

/**
 * LogicChainVisualizer - 논리 연쇄 시각화
 *
 * 표면 → 암묵 → 심층으로 이어지는 사고의 흐름을 시각화
 */

import { Eye, Brain, Heart, ArrowDown } from 'lucide-react'

interface ExplicitClaim {
  subject: string
  predicate: string
  quote?: string
}

interface LogicChainVisualizerProps {
  explicit_claims: ExplicitClaim[]
  implicit_assumptions: string[]
  deep_beliefs: string[]
}

export function LogicChainVisualizer({
  explicit_claims,
  implicit_assumptions,
  deep_beliefs
}: LogicChainVisualizerProps) {
  return (
    <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-900 mb-2">
          논리 연쇄: 어떻게 이 생각에 도달했는가?
        </h2>
        <p className="text-sm text-slate-600">
          표면적 주장에서 심층 세계관까지 이어지는 사고의 흐름
        </p>
      </div>

      <div className="space-y-4">
        {/* Layer 1: Explicit (표면층) */}
        <div className="relative">
          <div className="bg-blue-100 rounded-lg p-5 border-2 border-blue-300">
            <div className="flex items-center gap-2 mb-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Eye className="h-4 w-4 text-white" />
              </div>
              <h3 className="font-bold text-blue-900">
                1단계: 표면층 (Explicit) - &ldquo;글에서 직접 말하는 것&rdquo;
              </h3>
            </div>
            <div className="ml-10 space-y-2">
              {explicit_claims.slice(0, 2).map((claim, i) => (
                <div key={i} className="bg-white rounded p-3 border border-blue-200">
                  <p className="text-sm font-semibold text-slate-900">
                    {claim.subject}: {claim.predicate}
                  </p>
                  {claim.quote && (
                    <p className="text-xs text-slate-600 mt-1 italic">
                      &ldquo;{claim.quote}&rdquo;
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Arrow */}
          <div className="flex justify-center my-2">
            <div className="bg-slate-600 rounded-full p-2">
              <ArrowDown className="h-5 w-5 text-white" />
            </div>
          </div>
          <div className="text-center mb-2">
            <span className="text-sm font-medium text-slate-600">
              ↓ &ldquo;이런 전제가 깔려있다&rdquo;
            </span>
          </div>
        </div>

        {/* Layer 2: Implicit (암묵층) */}
        <div className="relative">
          <div className="bg-orange-100 rounded-lg p-5 border-2 border-orange-300">
            <div className="flex items-center gap-2 mb-3">
              <div className="flex-shrink-0 w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center">
                <Brain className="h-4 w-4 text-white" />
              </div>
              <h3 className="font-bold text-orange-900">
                2단계: 암묵층 (Implicit) - &ldquo;당연하다고 전제하는 것&rdquo;
              </h3>
            </div>
            <div className="ml-10 space-y-2">
              {implicit_assumptions.slice(0, 3).map((assumption, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-orange-600 mt-1">▸</span>
                  <p className="text-sm text-orange-900">{assumption}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Arrow */}
          <div className="flex justify-center my-2">
            <div className="bg-slate-600 rounded-full p-2">
              <ArrowDown className="h-5 w-5 text-white" />
            </div>
          </div>
          <div className="text-center mb-2">
            <span className="text-sm font-medium text-slate-600">
              ↓ &ldquo;이런 믿음이 기저에 있다&rdquo;
            </span>
          </div>
        </div>

        {/* Layer 3: Deep (심층) */}
        <div className="bg-purple-100 rounded-lg p-5 border-2 border-purple-300">
          <div className="flex items-center gap-2 mb-3">
            <div className="flex-shrink-0 w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
              <Heart className="h-4 w-4 text-white" />
            </div>
            <h3 className="font-bold text-purple-900">
              3단계: 심층 (Deep) - &ldquo;무의식적으로 믿는 것 (세계관)&rdquo;
            </h3>
          </div>
          <div className="ml-10 space-y-2">
            {deep_beliefs.map((belief, i) => (
              <div key={i} className="bg-purple-50 rounded p-3 border border-purple-200">
                <p className="text-sm font-medium text-purple-900">{belief}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 설명 */}
      <div className="mt-6 pt-6 border-t border-slate-300 bg-white rounded-lg p-4">
        <p className="text-sm text-slate-700 leading-relaxed">
          <span className="font-bold text-blue-600">💡 왜 3층 구조인가?</span>
          <br />
          <span className="font-semibold">표면층만 반박</span> → &ldquo;그건 그렇고!&rdquo; (방어 반응)
          <br />
          <span className="font-semibold">암묵층 전제 질문</span> → &ldquo;음... 그럴 수도?&rdquo; (재고 가능)
          <br />
          <span className="font-semibold">심층 세계관 이해</span> → &ldquo;아 그렇게 보는구나&rdquo; (대화 가능)
          <br /><br />
          <span className="font-medium text-purple-600">
            같은 층위에서 대화해야 통합니다. 심층 세계관을 이해하지 못하면,
            표면 주장을 아무리 반박해도 변하지 않습니다.
          </span>
        </p>
      </div>
    </div>
  )
}
