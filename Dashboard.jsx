// BrewIQ · frontend/src/pages/Dashboard.jsx
import { useApi } from '../hooks/useAuth'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import KpiCard from '../components/KpiCard'
import AiInsight from '../components/AiInsight'

export default function Dashboard() {
  const { data, loading } = useApi('/dashboard/')

  if (loading) return <div className="loading">Chargement...</div>
  if (!data)   return null

  const { kpis, by_month, by_product, by_tod, sentiment } = data

  return (
    <div className="page-grid">
      <div className="kpi-row">
        <KpiCard label="Revenu Total"     value={`${(kpis.total_revenue/1000).toFixed(1)}K€`} trend="+8.3%"  up />
        <KpiCard label="Transactions"     value={kpis.total_transactions.toLocaleString()}    trend="12 mois" up />
        <KpiCard label="Panier Moyen"     value={`${kpis.average_basket.toFixed(2)}€`}        trend="+2.1€"  up />
        <KpiCard label="Satisfaction IA"  value={`${sentiment.satisfaction_rate}%`}           trend="positif" up />
      </div>

      <AiInsight>
        Le <strong>Latte</strong> génère le CA le plus élevé (26 875€). Le <strong>Mardi</strong> est
        le jour le plus rentable (18 168€). Pic de commandes entre <strong>10h–11h</strong>.
      </AiInsight>

      <div className="chart-row-2">
        <div className="card">
          <div className="card-title">Revenu mensuel 2024 <span className="tag">€</span></div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={by_month} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(128,128,128,0.15)" />
              <XAxis dataKey="month_name" tick={{ fontSize: 10, fill: '#888' }} />
              <YAxis tick={{ fontSize: 10, fill: '#888' }} tickFormatter={v => `${(v/1000).toFixed(0)}K`} />
              <Tooltip formatter={v => [`${v.toFixed(0)}€`, 'Revenu']} />
              <Bar dataKey="revenue" fill="#C8773E" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">Top produits <span className="tag">par CA</span></div>
          {by_product.slice(0, 6).map((p, i) => {
            const max = by_product[0].revenue
            const pct = Math.round(p.revenue / max * 100)
            return (
              <div key={p.product} className="bar-row">
                <span className="bar-label">{p.product}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${pct}%`, background: i < 2 ? '#C8773E' : '#D4A853' }} />
                </div>
                <span className="bar-value">{(p.revenue/1000).toFixed(1)}K€</span>
              </div>
            )
          })}
        </div>
      </div>

      <div className="chart-row-3">
        <div className="card">
          <div className="card-title">Moment de journée</div>
          {by_tod.map(t => {
            const max = Math.max(...by_tod.map(x => x.revenue))
            const pct = Math.round(t.revenue / max * 100)
            const ic = t.time_of_day === 'Morning' ? '🌅' : t.time_of_day === 'Afternoon' ? '☀️' : '🌙'
            return (
              <div key={t.time_of_day} className="tod-row">
                <span className="tod-ic">{ic}</span>
                <div style={{ flex: 1 }}>
                  <div className="tod-header">
                    <span>{t.time_of_day}</span>
                    <span>{t.revenue.toFixed(0)}€</span>
                  </div>
                  <div className="mini-bar"><div style={{ width: `${pct}%`, height: '4px', background: '#C8773E', borderRadius: 2 }} /></div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="card">
          <div className="card-title">Paiement</div>
          <div className="center-stat">
            <div className="big-pct">100%</div>
            <div className="big-label">Paiement par carte</div>
            <div className="chip chip-ok">Aucun cash détecté</div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Sentiment NLP <span className="tag">IA</span></div>
          <div className="sent-summary">
            <div className="sent-big">{sentiment.satisfaction_rate}%</div>
            <div className="sent-lbl">Avis positifs</div>
          </div>
          {Object.entries(sentiment.counts).map(([k, v]) => (
            <div key={k} className="sent-row">
              <span className="dot" style={{ background: k==='positif'?'#3B6D11':k==='négatif'?'#A32D2D':'#888' }} />
              <span className="sent-name">{k}</span>
              <span className="sent-n">{v}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
