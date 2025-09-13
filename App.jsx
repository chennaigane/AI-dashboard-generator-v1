import React, { useState } from 'react'
import axios from 'axios'

export default function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function handleUpload(e) {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    setError("")
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await axios.post(import.meta.env.VITE_API_BASE + '/api/analyze/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(res.data)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{maxWidth: 900, margin: '40px auto', fontFamily: 'Inter, system-ui, Arial'}}>
      <h1>Automated Dashboard Generator & Insights Provider</h1>
      <p>Upload a CSV or Excel file to get a dashboard spec + insights.</p>

      <form onSubmit={handleUpload}>
        <input type="file" accept=".csv,.xlsx,.xls" onChange={e => setFile(e.target.files[0])} />
        <button type="submit" disabled={loading} style={{marginLeft: 12}}>
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>

      {error && <p style={{color:'crimson'}}>{error}</p>}

      {result && (
        <div style={{marginTop: 24}}>
          <h2>Summary</h2>
          <pre style={{whiteSpace:'pre-wrap', background:'#f6f8fa', padding:12, borderRadius:8}}>
{JSON.stringify({
  filename: result.filename,
  rows: result.rows,
  columns: result.columns
}, null, 2)}
          </pre>

          <h2>Dataset Preview</h2>
          <pre style={{whiteSpace:'pre-wrap', background:'#f6f8fa', padding:12, borderRadius:8}}>
{JSON.stringify(result.preview, null, 2)}
          </pre>

          <h2>Dashboard Spec</h2>
          <pre style={{whiteSpace:'pre-wrap', background:'#f6f8fa', padding:12, borderRadius:8}}>
{JSON.stringify(result.dashboard_spec, null, 2)}
          </pre>

          <h2>Insights</h2>
          <ul>
            {(result.insights || []).map((line, idx) => <li key={idx}>{line}</li>)}
          </ul>

          <h2>Power BI (DAX + Visual suggestions)</h2>
          <pre style={{whiteSpace:'pre-wrap', background:'#f6f8fa', padding:12, borderRadius:8}}>
{JSON.stringify(result.powerbi, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
