/**
 * GET /api/worldviews
 *
 * 세계관 목록 조회 API
 */

import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

function getSupabaseClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY
  if (!supabaseUrl || !supabaseKey) {
    throw new Error('Supabase URL and ANON_KEY are required')
  }
  return createClient(supabaseUrl, supabaseKey)
}

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  const supabase = getSupabaseClient()
  try {
    const { searchParams } = request.nextUrl

    // Query parameters
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')
    const sortBy = searchParams.get('sort_by') || 'updated_at'
    const order = searchParams.get('order') || 'desc'

    // Build query
    let query = supabase
      .from('worldviews')
      .select('*', { count: 'exact' })
      .neq('archived', true)

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

    // Parse frame field and add metadata
    const worldviews = data?.map(w => {
      let frameData: any = {}
      try {
        if (w.frame) {
          frameData = typeof w.frame === 'string' ? JSON.parse(w.frame) : w.frame
        }
      } catch (e) {
        console.error('Failed to parse frame:', e)
      }

      // Extract actor subject from frame.actor (can be object or string)
      let actorSubject = w.core_subject
      if (frameData.actor) {
        if (typeof frameData.actor === 'object' && frameData.actor.subject) {
          actorSubject = frameData.actor.subject
        } else if (typeof frameData.actor === 'string') {
          actorSubject = frameData.actor
        }
      }

      return {
        ...w,
        // Parse frame data into individual fields
        mechanisms: frameData.core_mechanisms || w.core_attributes || [],
        actor: frameData.actor || null,
        actor_subject: actorSubject,
        logic_chain: frameData.logic_pattern || null,
        reasoning_structure: frameData.logic_pattern || null,
        // Calculate additional metrics
        perception_density: w.total_perceptions / Math.max(w.total_contents || 1, 1)
      }
    })

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
  const supabase = getSupabaseClient()
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
