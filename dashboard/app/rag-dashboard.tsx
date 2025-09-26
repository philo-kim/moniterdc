'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { createClient } from '@supabase/supabase-js'
import {
  TrendingUp,
  Shield,
  Target,
  AlertTriangle,
  Activity,
  RefreshCw,
  BarChart3,
  MessageSquare,
  Clock,
  CheckCircle
} from 'lucide-react'

interface LogicData {
  id: string
  logic_type: 'attack' | 'defense'
  core_argument: string
  keywords: string[]
  ai_classification: string
  effectiveness_score: number
  threat_level: number
  created_at: string
  usage_count: number
  success_count: number
}

interface MatchData {
  id: string
  match_confidence: number
  match_reason: string
  attack_argument: string
  defense_argument: string
  created_at: string
}

interface StatsData {
  totalLogics: number
  attackLogics: number
  defenseLogics: number
  totalMatches: number
  avgConfidence: number
}

const RAGDashboard: React.FC = () => {
  const [stats, setStats] = useState<StatsData>({
    totalLogics: 0,
    attackLogics: 0,
    defenseLogics: 0,
    totalMatches: 0,
    avgConfidence: 0
  })

  const [recentLogics, setRecentLogics] = useState<LogicData[]>([])
  const [recentMatches, setRecentMatches] = useState<MatchData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  // supabase 클라이언트를 useMemo로 메모이제이션
  const supabase = React.useMemo(() => createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  ), [])

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)

      // 논리 저장소 통계
      const { data: logics } = await supabase
        .from('logic_repository')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10)

      // 매칭 결과
      const { data: matches } = await supabase
        .from('logic_matches')
        .select(`
          *,
          attack:attack_id(core_argument),
          defense:defense_id(core_argument)
        `)
        .order('created_at', { ascending: false })
        .limit(10)

      if (logics) {
        const attacks = logics.filter(l => l.logic_type === 'attack')
        const defenses = logics.filter(l => l.logic_type === 'defense')

        setStats({
          totalLogics: logics.length,
          attackLogics: attacks.length,
          defenseLogics: defenses.length,
          totalMatches: matches?.length || 0,
          avgConfidence: matches?.length ?
            matches.reduce((sum, m) => sum + m.match_confidence, 0) / matches.length : 0
        })

        setRecentLogics(logics)
      }

      if (matches) {
        setRecentMatches(matches.map(match => ({
          ...match,
          attack_argument: match.attack?.core_argument || 'N/A',
          defense_argument: match.defense?.core_argument || 'N/A'
        })))
      }

      setLastUpdate(new Date())
    } catch (error) {
      console.error('데이터 조회 실패:', error)
    } finally {
      setIsLoading(false)
    }
  }, [supabase])

  useEffect(() => {
    fetchData()

    // 30초마다 자동 새로고침
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [fetchData])

  const StatCard = ({
    title,
    value,
    subtitle,
    icon: Icon,
    color
  }: {
    title: string
    value: string | number
    subtitle?: string
    icon: any
    color: string
  }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4" style={{ borderLeftColor: color }}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <Icon className="h-8 w-8" style={{ color }} />
      </div>
    </div>
  )

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100'
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getThreatColor = (level: number) => {
    if (level >= 8) return 'text-red-600'
    if (level >= 6) return 'text-yellow-600'
    return 'text-green-600'
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🤖 Logic Defense RAG System
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                DC갤러리 정치 AI 모니터링 시스템 대시보드
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={fetchData}
                disabled={isLoading}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                새로고침
              </button>
              <div className="text-sm text-gray-500">
                마지막 업데이트: {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="총 논리"
            value={stats.totalLogics}
            subtitle="수집된 정치 논리"
            icon={MessageSquare}
            color="#3B82F6"
          />
          <StatCard
            title="공격 논리"
            value={stats.attackLogics}
            subtitle="분석된 공격적 논리"
            icon={Target}
            color="#EF4444"
          />
          <StatCard
            title="방어 논리"
            value={stats.defenseLogics}
            subtitle="보유한 방어 전략"
            icon={Shield}
            color="#10B981"
          />
          <StatCard
            title="매칭 신뢰도"
            value={`${(stats.avgConfidence * 100).toFixed(1)}%`}
            subtitle={`${stats.totalMatches}개 매칭 결과`}
            icon={Activity}
            color="#8B5CF6"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Logic Repository */}
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                최근 수집된 논리
              </h2>
            </div>
            <div className="p-6">
              {isLoading ? (
                <div className="flex justify-center items-center h-32">
                  <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  {recentLogics.slice(0, 5).map(logic => (
                    <div key={logic.id} className="border-l-4 border-blue-500 pl-4 py-2">
                      <div className="flex items-center justify-between mb-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          logic.logic_type === 'attack'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {logic.logic_type === 'attack' ? '🎯 공격' : '🛡️ 방어'}
                        </span>
                        <span className={`text-sm font-medium ${getThreatColor(logic.threat_level)}`}>
                          위협도: {logic.threat_level}/10
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">
                        {logic.core_argument.slice(0, 100)}...
                      </p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>효과성: {logic.effectiveness_score}/10</span>
                        <span>사용: {logic.usage_count}회</span>
                        <span>{new Date(logic.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Matches */}
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                최근 매칭 결과
              </h2>
            </div>
            <div className="p-6">
              {isLoading ? (
                <div className="flex justify-center items-center h-32">
                  <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
                </div>
              ) : (
                <div className="space-y-4">
                  {recentMatches.slice(0, 5).map(match => (
                    <div key={match.id} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex items-center justify-between mb-3">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(match.match_confidence)}`}>
                          신뢰도: {(match.match_confidence * 100).toFixed(1)}%
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(match.created_at).toLocaleTimeString()}
                        </span>
                      </div>

                      <div className="space-y-2">
                        <div className="text-sm">
                          <span className="font-medium text-red-600">공격:</span>
                          <p className="text-gray-700 ml-4 mt-1">
                            {match.attack_argument?.slice(0, 80)}...
                          </p>
                        </div>

                        <div className="text-sm">
                          <span className="font-medium text-green-600">방어:</span>
                          <p className="text-gray-700 ml-4 mt-1">
                            {match.defense_argument?.slice(0, 80)}...
                          </p>
                        </div>

                        {match.match_reason && (
                          <div className="text-xs text-gray-600 bg-white p-2 rounded">
                            <strong>매칭 사유:</strong> {match.match_reason.slice(0, 100)}...
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
            시스템 상태
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">크롤러</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                ✅ 정상
              </span>
            </div>
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">RAG 시스템</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                ✅ 정상
              </span>
            </div>
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">매칭 엔진</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                ✅ 정상
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RAGDashboard