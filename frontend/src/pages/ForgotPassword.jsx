import { useState } from 'react'
import client from '../api/client'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const submit = async e => {
    e.preventDefault()
    await client.post('/auth/forgot-password', { email })
    setSent(true)
  }
  if (sent) return (
    <div className="min-h-screen flex items-center justify-center">
      <p>✅ Αν το email υπάρχει, θα λάβετε σύνδεσμο.</p>
    </div>
  )
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={submit} className="bg-white p-8 rounded shadow w-80">
        <h1 className="text-xl font-bold mb-4">Επαναφορά κωδικού</h1>
        <input className="w-full border rounded p-2 mb-4" type="email" placeholder="Email"
               value={email} onChange={e=>setEmail(e.target.value)} required />
        <button className="w-full bg-blue-700 text-white py-2 rounded">Αποστολή</button>
      </form>
    </div>
  )
}
