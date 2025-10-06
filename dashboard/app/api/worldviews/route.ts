/**
 * GET /api/worldviews
 *
 * 세계관 목록 조회 API
 */

import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
)

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl

    // Query parameters
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')
    const sortBy = searchParams.get('sort_by') || 'strength_overall'
    const order = searchParams.get('order') || 'desc'
    const trend = searchParams.get('trend') // rising, stable, falling, dead
    const minStrength = parseFloat(searchParams.get('min_strength') || '0')

    // Build query
    let query = supabase
      .from('worldviews')
      .select('*', { count: 'exact' })
      .gte('strength_overall', minStrength)

    // Filter by trend
    if (trend) {
      query = query.eq('trend', trend)
    }

    // Sort
    query = query.order(sortBy, { ascending: order === 'asc' })

    // Pagination
    query = query.range(offset, offset + limit - 1)

    const { data, error, count } = await query

    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json(
        { error: 'Failed to fetch worldviews' },
        { status: 500 }
      )
    }

    // Add metadata
    const worldviews = data?.map(w => ({
      ...w,
      // Calculate additional metrics
      perception_density: w.total_perceptions / Math.max(w.total_contents, 1),
      mechanism_count: (w.cognitive_mechanisms?.length || 0) +
                      (w.formation_phases?.length || 0) +
                      (w.structural_flaws?.length || 0)
    }))

    return NextResponse.json({
      worldviews,
      pagination: {
        total: count,
        limit,
        offset,
        hasMore: offset + limit < (count || 0)
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
 * POST /api/worldviews
 *
 * 세계관 생성 (관리자용)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const { data, error } = await supabase
      .from('worldviews')
      .insert(body)
      .select()

    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json(
        { error: 'Failed to create worldview' },
        { status: 500 }
      )
    }

    return NextResponse.json(data[0], { status: 201 })

  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
