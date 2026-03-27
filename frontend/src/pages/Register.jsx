import { useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'

export default function Register() {
  const [form, setForm] = useState({ email: '', password: '', name: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  const submit = async (e) => {
    e.preventDefault()
    try {
      await client.post('/auth/register', form)
      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.error || 'Σφάλμα εγγραφής')
    }
  }

  if (success) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-white p-8 rounded shadow text-center">
        <p className="text-xl">✅ Εγγραφή επιτυχής!</p>
        <p className="mt-2 text-gray-600">Ελέγξτε το email σας για επαλήθευση.</p>
        <Link to="/login" className="mt-4 block text-blue-600">Σύνδεση</Link>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={submit} className="bg-white p-8 rounded shadow w-full max-w-sm">
        <h1 className="text-2xl font-bold mb-6 text-center">Εγγραφή</h1>
        {error && <p className="text-red-600 mb-4 text-sm">{error}</p>}
        <input className="w-full border rounded p-2 mb-3" placeholder="Ονοματεπώνυμο"
               value={form.name} onChange={set('name')} />
        <input className="w-full border rounded p-2 mb-3" type="email" placeholder="Email"
               value={form.email} onChange={set('email')} required />
        <input className="w-full border rounded p-2 mb-4" type="password" placeholder="Κωδικός"
               value={form.password} onChange={set('password')} required />
        <button className="w-full bg-blue-700 text-white py-2 rounded font-semibold">Εγγραφή</button>
        <div className="mt-4 text-center text-sm">
          <Link to="/login" className="text-blue-600">Ήδη εγγεγραμμένος;</Link>
        </div>
      </form>
    </div>
  )
}
