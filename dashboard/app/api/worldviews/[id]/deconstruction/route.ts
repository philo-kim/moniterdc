/**
 * GET /api/worldviews/:id/deconstruction
 *
 * 세계관 해체 전략 조회
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
    const { searchParams } = new URL(request.url)
    const regenerate = searchParams.get('regenerate') === 'true'

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

    // Check if deconstruction exists
    const existingDeconstruction = worldview.deconstruction

    if (existingDeconstruction && !regenerate) {
      // Return cached deconstruction
      return NextResponse.json({
        ...existingDeconstruction,
        worldview_id: id,
        worldview_title: worldview.title,
        cached: true
      })
    }

    // If regenerate requested or no deconstruction exists
    // This would typically call a Python backend service
    // For now, return structure with placeholder

    if (!existingDeconstruction) {
      return NextResponse.json({
        worldview_id: id,
        worldview_title: worldview.title,
        message: 'Deconstruction not yet generated. Please run DeconstructionEngine.',
        flaws: worldview.structural_flaws || [],
        cognitive_mechanisms: worldview.cognitive_mechanisms || [],
        formation_phases: worldview.formation_phases || []
      })
    }

    return NextResponse.json({
      ...existingDeconstruction,
      worldview_id: id,
      worldview_title: worldview.title
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
 * POST /api/worldviews/:id/deconstruction
 *
 * 세계관 해체 전략 생성 (비동기 작업 트리거)
 */
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params

    // This would typically queue a background job to run DeconstructionEngine
    // For MVP, we'll return a message indicating the process

    return NextResponse.json({
      worldview_id: id,
      message: 'Deconstruction generation queued. Run `DeconstructionEngine.deconstruct()` in Python backend.',
      status: 'queued'
    }, { status: 202 })

  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
