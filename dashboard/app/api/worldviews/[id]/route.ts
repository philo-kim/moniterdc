/**
 * GET /api/worldviews/:id
 *
 * 특정 세계관 상세 조회
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

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const supabase = getSupabaseClient()
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

    // Get linked layered_perceptions via perception_worldview_links
    const { data: links } = await supabase
      .from('perception_worldview_links')
      .select('perception_id, relevance_score')
      .eq('worldview_id', id)

    const layeredPerceptionIds = (links || []).map(l => l.perception_id)
    let layeredPerceptions = []
    let contentIds: string[] = []

    if (layeredPerceptionIds.length > 0) {
      // Get layered perceptions (full data with 3-layer analysis)
      const { data: layeredData } = await supabase
        .from('layered_perceptions')
        .select('*')
        .in('id', layeredPerceptionIds)

      layeredPerceptions = layeredData || []
      contentIds = [...new Set(layeredPerceptions.map(lp => lp.content_id).filter(Boolean))]
    }

    // Get contents (source materials)
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
      layered_perceptions: layeredPerceptions,
      contents,
      strength_history: strengthHistory || [],
      stats: {
        total_perceptions: layeredPerceptions.length,
        total_contents: contents.length,
        perception_density: layeredPerceptions.length / Math.max(contents.length, 1)
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
  const supabase = getSupabaseClient()
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
  const supabase = getSupabaseClient()
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

