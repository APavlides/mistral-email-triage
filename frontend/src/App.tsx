import { useEffect, useState } from 'react'

type TriageResult = {
  category: string
  urgency: string
  summary: string
  suggested_reply: string
}

function App() {
  const [backend, setBackend] = useState('checking...')
  const [text, setText] = useState('')
  const [result, setResult] = useState<TriageResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => setBackend(data.status))
      .catch(() => setBackend('unreachable'))
  }, [])

  async function triage() {
    if (!text.trim()) {
      setError('Paste an email first.')
      return
    }
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch('/api/triage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      if (!res.ok) {
        // FastAPI sends errors as { detail: "..." }; the proxy's own errors have no JSON body
        const body = await res.json().catch(() => null)
        throw new Error(
          typeof body?.detail === 'string' ? body.detail : `Request failed (${res.status})`,
        )
      }
      setResult(await res.json())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <h1>Ticket triage</h1>
      <p className="backend">Backend: {backend}</p>
      <textarea
        rows={8}
        placeholder="Paste an email here"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button onClick={triage} disabled={loading}>
        {loading ? 'Triaging...' : 'Triage'}
      </button>
      {error && (
        <p role="alert" className="error">
          Error: {error}
        </p>
      )}
      {!result && !loading && !error && (
        <p className="empty">No result yet. Paste an email and click Triage.</p>
      )}
      {result && (
        <section className="result">
          <div className="badges">
            <div>
              <span className="label">Category</span>
              <span className="badge">{result.category.replace('_', ' ')}</span>
            </div>
            <div>
              <span className="label">Urgency</span>
              <span className={`badge urgency-${result.urgency}`}>{result.urgency}</span>
            </div>
          </div>
          <div className="card">
            <span className="label">Summary</span>
            <p>{result.summary}</p>
          </div>
          <div className="card">
            <span className="label">Suggested reply</span>
            <p>{result.suggested_reply}</p>
          </div>
        </section>
      )}
    </main>
  )
}

export default App
