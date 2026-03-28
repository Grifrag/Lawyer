import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import client from '../api/client'

export default function Navbar() {
  const { accessToken, clearAuth } = useAuthStore()
  const nav = useNavigate()
  const [open, setOpen] = useState(false)

  const logout = async () => {
    await client.post('/auth/logout')
    clearAuth()
    nav('/login')
  }

  return (
    <nav className="bg-blue-700 text-white px-6 py-3">
      <div className="flex items-center justify-between">
        <Link to="/dashboard" className="font-bold text-lg">⚖️ Solon Checker</Link>

        {accessToken && (
          <>
            {/* Desktop menu */}
            <div className="hidden md:flex items-center gap-6 text-sm">
              <Link to="/dashboard" className="hover:underline">Υποθέσεις</Link>
              <Link to="/cases/new" className="hover:underline">+ Νέα</Link>
              <Link to="/settings" className="hover:underline">Ρυθμίσεις</Link>
              <Link to="/billing" className="hover:underline">Συνδρομή</Link>
              <button onClick={logout} className="hover:underline">Έξοδος</button>
            </div>

            {/* Hamburger button - mobile only */}
            <button
              className="md:hidden text-white text-2xl leading-none"
              onClick={() => setOpen(o => !o)}
            >
              {open ? '✕' : '☰'}
            </button>
          </>
        )}
      </div>

      {/* Mobile menu */}
      {accessToken && open && (
        <div className="md:hidden flex flex-col gap-4 pt-4 pb-2 text-sm border-t border-blue-600 mt-3">
          <Link to="/dashboard" onClick={() => setOpen(false)} className="hover:underline">Υποθέσεις</Link>
          <Link to="/cases/new" onClick={() => setOpen(false)} className="hover:underline">+ Νέα Υπόθεση</Link>
          <Link to="/settings" onClick={() => setOpen(false)} className="hover:underline">Ρυθμίσεις</Link>
          <Link to="/billing" onClick={() => setOpen(false)} className="hover:underline">Συνδρομή</Link>
          <button onClick={logout} className="text-left hover:underline">Έξοδος</button>
        </div>
      )}
    </nav>
  )
}
