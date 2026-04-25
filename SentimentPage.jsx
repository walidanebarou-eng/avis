// BrewIQ · frontend/src/pages/SentimentPage.jsx
import { useState } from 'react'
import { useApi, apiPost } from '../hooks/useAuth'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import AiInsight from '../components/AiInsight'

const COLORS = { positif: '#3B6D11', neutre: '#888780', négatif: '#A32D2D' }
const PILLS   = { positif: 'pill-pos', neutre: 'pill-neu', négatif: 'pill-neg' }

export default function SentimentPage() {
  const { data, loading } = useApi('/sentiment/')
  const [inputText, setInputText] = useState('')
  const [liveResult, setLiveResult] = useState(null)
  const [analysing,  setAnalysing]  = useState(false)

  const analyse = async () => {
    if (!inputText.trim()) return
    setAnalysing(true)
    const r = await apiPost('/sentiment/analyse', { text: inputText })
    setLiveResult(r)
    setAnalysing(false)
  }

  if (loading) return <div className="loading">Analyse NLP en cours...</div>
  if (!data)   return null

  const { stats, reviews } = data
  const pieData = Object.entries(stats.counts).map(([name, value]) => ({ name, value }))

  return (
    <div className="page-grid">
      <AiInsight>
        <strong>{stats.satisfaction_rate}%</strong> d'avis positifs sur{' '}
        {stats.total} avis analysés. Mots clés négatifs récurrents : <em>cher, coûteux, élevé</em>.
        Score moyen de sentiment : <strong>{stats.average_score}</strong>.
      </AiInsight>

      {/* Live analyser */}
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-title">Analyser un avis en temps réel <span className="tag">NLP · FR</span></div>
        <textarea
          className="review-input"
          placeholder="Saisir un avis client en français..."
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          rows={3}
        />
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 8 }}>
          <button className="btn-primary" onClick={analyse} disabled={analysing}>
            {analysing ? 'Analyse...' : '▶ Analyser'}
          </button>
          {liveResult && (
            <div className="live-result">
              <span className={`pill ${PILLS[liveResult.sentiment]}`}>{liveResult.sentiment}</span>
              <span className="score-label">Score: {liveResult.score}</span>
              <span className="conf-label">Conf: {Math.round(liveResult.confidence * 100)}%</span>
              <span className="kw-label">{liveResult.keywords?.join(', ')}</span>
            </div>
          )}
        </div>
      </div>

      <div className="chart-row-2">
        <div className="card">
          <div className="card-title">Avis clients analysés <span className="tag">{reviews.length} uniques</span></div>
          <div className="review-list">
            {reviews.map((r, i) => (
              <div key={i} className="review-card">
                <div className="review-header">
                  <span className="review-idx">#{i + 1}</span>
                  <span className={`pill ${PILLS[r.sentiment]}`}>{r.sentiment}</span>
                  <span className="review-score">{r.score > 0 ? '+' : ''}{r.score}</span>
                </div>
                <div className="review-text">"{r.text}"</div>
                <div className="review-kws">{r.keywords?.map(k => (
                  <span key={k} className={`kw-tag ${k.startsWith('+') ? 'kw-pos' : 'kw-neg'}`}>{k}</span>
                ))}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card-title">Distribution sentiment</div>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} dataKey="value" label={e => `${e.name} ${e.value}`} labelLine={false}>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <div>
            {Object.entries(stats.percentages).map(([k, v]) => (
              <div key={k} className="stat-row">
                <span className="dot" style={{ background: COLORS[k] }} />
                <span className="stat-name">{k}</span>
                <div className="stat-bar"><div style={{ width: `${v}%`, height: 4, background: COLORS[k], borderRadius: 2 }} /></div>
                <span className="stat-pct">{v}%</span>
              </div>
            ))}
          </div>

          <div className="kpi-sm">
            <div><div className="kpi-sm-label">Score moyen</div><div className="kpi-sm-val">{stats.average_score}</div></div>
            <div><div className="kpi-sm-label">Taux satisfaction</div><div className="kpi-sm-val">{stats.satisfaction_rate}%</div></div>
          </div>
        </div>
      </div>
    </div>
  )
}
