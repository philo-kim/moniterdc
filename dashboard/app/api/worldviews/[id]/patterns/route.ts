import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const worldviewId = params.id

    // Fetch all active/fading patterns for this worldview
    const { data: patterns, error } = await supabase
      .from('worldview_patterns')
      .select('id, layer, text, strength, status, appearance_count, last_seen')
      .eq('worldview_id', worldviewId)
      .in('status', ['active', 'fading'])

    if (error) {
      console.error('Error fetching patterns:', error)
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    // Group by layer and sort each layer by strength descending
    const grouped = {
      surface: (patterns?.filter(p => p.layer === 'surface') || [])
        .sort((a, b) => b.strength - a.strength),
      implicit: (patterns?.filter(p => p.layer === 'implicit') || [])
        .sort((a, b) => b.strength - a.strength),
      deep: (patterns?.filter(p => p.layer === 'deep') || [])
        .sort((a, b) => b.strength - a.strength)
    }

    return NextResponse.json(grouped)
  } catch (error: any) {
    console.error('Error in patterns API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
