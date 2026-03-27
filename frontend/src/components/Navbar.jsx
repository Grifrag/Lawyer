import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import client from '../api/client'

export default function Navbar() {
  const { accessToken, clearAuth } = useAuthStore()
  const nav = useNavigate()
  const logout = async () => {
    await client.post('/auth/logout')
    clearAuth()
    nav('/login')
  }
  return (
    <nav className="bg-blue-700 text-white px-6 py-3 flex items-center gap-6">
      <Link to="/dashboard" className="font-bold text-lg">⚖️ Solon Checker</Link>
      {accessToken && <>
        <Link to="/dashboard" className="hover:underline">Υποθέσεις</Link>
        <Link to="/cases/new" className="hover:underline">+ Νέα</Link>
        <Link to="/settings" className="hover:underline">Ρυθμίσεις</Link>
        <Link to="/billing" className="hover:underline ml-auto">Συνδρομή</Link>
        <button onClick={logout} className="hover:underline">Έξοδος</button>
      </>}
    </nav>
  )
}
