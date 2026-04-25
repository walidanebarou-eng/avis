// BrewIQ · frontend/src/App.jsx
import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Topbar  from './components/Topbar'
import Dashboard    from './pages/Dashboard'
import Analytics    from './pages/Analytics'
import SentimentPage from './pages/SentimentPage'
import PredictPage  from './pages/PredictPage'
import ProductsPage from './pages/ProductsPage'
import StocksPage   from './pages/StocksPage'
import LoginPage    from './pages/LoginPage'
import { AuthProvider, useAuth } from './hooks/useAuth'
import './App.css'

const PAGES = {
  dashboard:  { title: 'Dashboard Overview',     sub: '3 547 transactions · Jan–Déc 2024',       Component: Dashboard },
  analytics:  { title: 'Ventes & IA Analytics',  sub: 'Analyse complète produit, jour, heure',   Component: Analytics },
  sentiment:  { title: 'Sentiment NLP',           sub: 'Analyse des avis clients · Modèle FR',    Component: SentimentPage },
  predict:    { title: 'Prédictions IA',          sub: 'Random Forest · Forecasting 2025',        Component: PredictPage },
  products:   { title: 'Catalogue Produits',      sub: '8 produits actifs · Performance & KPIs', Component: ProductsPage },
  stocks:     { title: 'Gestion des Stocks',      sub: 'Vélocité de vente · Réapprovisionnement',Component: StocksPage },
}

function AppInner() {
  const { token } = useAuth()
  const [page, setPage] = useState('dashboard')

  if (!token) return <LoginPage />

  const { title, sub, Component } = PAGES[page]

  return (
    <div className="shell">
      <Sidebar current={page} onNavigate={setPage} />
      <div className="main">
        <Topbar title={title} sub={sub} />
        <div className="content">
          <Component />
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  )
}
