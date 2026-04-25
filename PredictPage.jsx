// BrewIQ · frontend/src/pages/PredictPage.jsx
import { useApi } from '../hooks/useAuth'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import AiInsight from '../components/AiInsight'

const MONTH_REV_2024 = [6399,13215,15892,5720,8164,7618,6916,7614,9989,13891,8591,8238]
const MONTHS = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']

export default function PredictPage() {
  const { data: predData, loading: l1 } = useApi('/predictions/?months=12')
  const { data: prodData, loading: l2 } = useApi('/predictions/by-product')

  if (l1 || l2) return <div className="loading">Calcul des prédictions RF...</div>
  if (!predData || !prodData) return null

  const chartData = predData.predictions.map((p, i) => ({
    month: MONTHS[i],
    'Prévu 2025': p.predicted_revenue,
    'Réel 2024': MONTH_REV_2024[i],
  }))

  return (
    <div className="page-grid">
      <AiInsight>
        Modèle <strong>Random Forest</strong> entraîné sur 3 547 transactions.
        Croissance prédite de <strong>+8%</strong> pour 2025. Pic saisonnier attendu en
        <strong> Mars et Octobre</strong>. Confiance moyenne : 80%.
      </AiInsight>

      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-title">Prévision CA mensuel 2025 vs 2024 <span className="tag">RF Model</span></div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData} margin={{ top: 4, right: 16, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(128,128,128,0.15)" />
            <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#888' }} />
            <YAxis tick={{ fontSize: 10, fill: '#888' }} tickFormatter={v => `${(v/1000).toFixed(0)}K`} />
            <Tooltip formatter={v => `${v.toFixed(0)}€`} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="Réel 2024"  stroke="#888780" strokeWidth={1.5} strokeDasharray="4 3" dot={false} />
            <Line type="monotone" dataKey="Prévu 2025" stroke="#C8773E" strokeWidth={2} dot={{ r: 3, fill: '#C8773E' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-row-2">
        <div className="card">
          <div className="card-title">Détail prévisions H1 2025</div>
          {predData.predictions.slice(0, 6).map(p => (
            <div key={p.month} className="pred-row">
              <span className="pred-month">{p.month_name}</span>
              <div className="pred-bar-track">
                <div className="pred-bar-fill" style={{ width: `${Math.round(p.predicted_revenue / 16000 * 100)}%` }} />
              </div>
              <span className="pred-rev">{p.predicted_revenue.toFixed(0)}€</span>
              <span className={`pred-trend ${p.growth_pct >= 0 ? 'up' : 'dn'}`}>
                {p.growth_pct >= 0 ? '↑' : '↓'} {Math.abs(p.growth_pct)}%
              </span>
              <span className="pred-conf">{Math.round(p.confidence * 100)}%</span>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="card-title">Demande prévue par produit <span className="tag">Q1 2025</span></div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={prodData.data} layout="vertical" margin={{ top: 0, right: 16, left: 60, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(128,128,128,0.1)" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 9, fill: '#888' }} tickFormatter={v => `${v}`} />
              <YAxis type="category" dataKey="product" tick={{ fontSize: 10, fill: '#888' }} width={70} />
              <Tooltip formatter={v => [`${v} unités`, 'Prévu Q1']} />
              <Bar dataKey="predicted_q1_2025" fill="#D4A853" radius={[0, 3, 3, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
