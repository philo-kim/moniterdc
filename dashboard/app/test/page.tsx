'use client'

import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function TestPage() {
  const { data, error, isLoading } = useSWR('/api/worldviews/c4427c50-32ce-45ed-bfcb-b1769a74fa71', fetcher)

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">SWR Test Page</h1>

      <div className="space-y-4">
        <div>
          <strong>isLoading:</strong> {isLoading ? 'true' : 'false'}
        </div>

        <div>
          <strong>hasError:</strong> {error ? 'true' : 'false'}
        </div>

        <div>
          <strong>hasData:</strong> {data ? 'true' : 'false'}
        </div>

        {data && (
          <div>
            <strong>Title:</strong> {data.title}
            <br />
            <strong>Perceptions:</strong> {data.layered_perceptions?.length || 0}
          </div>
        )}

        {error && (
          <div className="text-red-600">
            <strong>Error:</strong> {error.message}
          </div>
        )}
      </div>
    </div>
  )
}
