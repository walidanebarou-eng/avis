// BrewIQ · frontend/src/hooks/useAuth.jsx
import { createContext, useContext, useState } from 'react'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken]   = useState(localStorage.getItem('brewiq_token'))
  const [user,  setUser]    = useState(JSON.parse(localStorage.getItem('brewiq_user') || 'null'))

  const login = async (username, password) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    if (!res.ok) throw new Error('Identifiants invalides')
    const data = await res.json()
    localStorage.setItem('brewiq_token', data.access_token)
    localStorage.setItem('brewiq_user', JSON.stringify({ username: data.username, role: data.role }))
    setToken(data.access_token)
    setUser({ username: data.username, role: data.role })
  }

  const logout = () => {
    localStorage.removeItem('brewiq_token')
    localStorage.removeItem('brewiq_user')
    setToken(null)
    setUser(null)
  }

  return <AuthCtx.Provider value={{ token, user, login, logout }}>{children}</AuthCtx.Provider>
}

export const useAuth = () => useContext(AuthCtx)


// ── hooks/useApi.js ─────────────────────────────────────────────────────────
import { useState, useEffect } from 'react'

export function useApi(endpoint, deps = []) {
  const token = localStorage.getItem('brewiq_token')
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    setLoading(true)
    fetch(`/api${endpoint}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, deps)

  return { data, loading, error }
}

export async function apiPost(endpoint, body) {
  const token = localStorage.getItem('brewiq_token')
  const res = await fetch(`/api${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(body)
  })
  return res.json()
}
