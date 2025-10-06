/**
 * GET /api/worldviews/:id
 *
 * 특정 세계관 상세 조회
 */

import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
)

export const dynamic = 'force-dynamic'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params

    // Get worldview
    const { data: worldview, error } = await supabase
      .from('worldviews')
      .select('*')
      .eq('id', id)
      .single()

    if (error || !worldview) {
      return NextResponse.json(
        { error: 'Worldview not found' },
        { status: 404 }
      )
    }

    // Get linked perceptions via perception_worldview_links
    const { data: links } = await supabase
      .from('perception_worldview_links')
      .select('perception_id, relevance_score')
      .eq('worldview_id', id)

    const perceptionIds = (links || []).map(l => l.perception_id)
    let perceptions = []

    if (perceptionIds.length > 0) {
      const { data: perceptionData } = await supabase
        .from('layered_perceptions')
        .select('*')
        .in('id', perceptionIds)

      perceptions = perceptionData || []
    }

    // Get contents (source materials)
    const contentIds = [...new Set(perceptions.map(p => p.content_id).filter(Boolean))]
    let contents = []

    if (contentIds.length > 0) {
      const { data: contentData } = await supabase
        .from('contents')
        .select('*')
        .in('id', contentIds)

      contents = contentData || []
    }

    // Get strength history
    const { data: strengthHistory } = await supabase
      .from('worldview_strength_history')
      .select('*')
      .eq('worldview_id', id)
      .order('recorded_at', { ascending: true })
      .limit(30)

    // Build complete response
    return NextResponse.json({
      ...worldview,
      perceptions,
      contents,
      strength_history: strengthHistory || [],
      stats: {
        total_perceptions: perceptions.length,
        total_contents: contents.length,
        perception_density: perceptions.length / Math.max(contents.length, 1),
        avg_valence: calculateAvgValence(perceptions),
        temporal_span_days: calculateTemporalSpan(perceptions)
      }
    })

  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * PATCH /api/worldviews/:id
 *
 * 세계관 업데이트
 */
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    const body = await request.json()

    const { data, error } = await supabase
      .from('worldviews')
      .update(body)
      .eq('id', id)
      .select()

    if (error) {
      return NextResponse.json(
        { error: 'Failed to update worldview' },
        { status: 500 }
      )
    }

    return NextResponse.json(data[0])

  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/worldviews/:id
 *
 * 세계관 삭제
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params

    const { error } = await supabase
      .from('worldviews')
      .delete()
      .eq('id', id)

    if (error) {
      return NextResponse.json(
        { error: 'Failed to delete worldview' },
        { status: 500 }
      )
    }

    return NextResponse.json({ success: true })

  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Helper functions

function calculateAvgValence(perceptions: any[]): string {
  if (!perceptions.length) return 'neutral'

  const valences = perceptions.map(p => p.perceived_valence)
  const counts = {
    positive: valences.filter(v => v === 'positive').length,
    negative: valences.filter(v => v === 'negative').length,
    neutral: valences.filter(v => v === 'neutral').length
  }

  const max = Math.max(counts.positive, counts.negative, counts.neutral)

  if (max === counts.positive) return 'positive'
  if (max === counts.negative) return 'negative'
  return 'neutral'
}

function calculateTemporalSpan(perceptions: any[]): number {
  if (!perceptions.length) return 0

  const dates = perceptions
    .map(p => p.extracted_at)
    .filter(Boolean)
    .map(d => new Date(d).getTime())

  if (dates.length < 2) return 0

  const minDate = Math.min(...dates)
  const maxDate = Math.max(...dates)

  return Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24)) // days
}
