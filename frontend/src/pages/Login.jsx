import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import client from '../api/client'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { setAuth } = useAuthStore()
  const nav = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await client.post('/auth/login', { email, password })
      setAuth(data.access_token, {
        email,
        email_verified: data.email_verified,
        subscription_status: data.subscription_status,
        trial_ends_at: data.trial_ends_at,
      })
      nav('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Σφάλμα σύνδεσης')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={submit} className="bg-white p-8 rounded shadow w-full max-w-sm">
        <h1 className="text-2xl font-bold mb-6 text-center">Σύνδεση</h1>
        {error && <p className="text-red-600 mb-4 text-sm">{error}</p>}
        <input className="w-full border rounded p-2 mb-3" type="email"
               placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <input className="w-full border rounded p-2 mb-4" type="password"
               placeholder="Κωδικός" value={password} onChange={e=>setPassword(e.target.value)} required />
        <button className="w-full bg-blue-700 text-white py-2 rounded font-semibold">
          Σύνδεση
        </button>
        <div className="mt-4 text-center text-sm">
          <Link to="/register" className="text-blue-600">Εγγραφή</Link>
          {' | '}
          <Link to="/forgot-password" className="text-blue-600">Ξεχάσατε κωδικό;</Link>
        </div>
      </form>
    </div>
  )
}
