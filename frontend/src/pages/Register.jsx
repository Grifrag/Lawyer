import { useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'

export default function Register() {
  const [form, setForm] = useState({ email: '', password: '', name: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [sentEmail, setSentEmail] = useState('')

  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  const submit = async (e) => {
    e.preventDefault()
    try {
      await client.post('/auth/register', form)
      setSentEmail(form.email)
      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.error || 'Σφάλμα εγγραφής')
    }
  }

  if (success) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded shadow text-center max-w-md">
        <p className="text-4xl mb-4">📧</p>
        <p className="text-xl font-bold mb-3">Ελέγξτε το email σας!</p>
        <p className="text-gray-600 mb-2">
          Σας στείλαμε email επαλήθευσης στο:
        </p>
        <p className="font-semibold text-blue-700 mb-4">{sentEmail}</p>
        <p className="text-gray-500 text-sm mb-6">
          Κάντε κλικ στον σύνδεσμο επαλήθευσης μέσα στο email για να ενεργοποιήσετε τον λογαριασμό σας.
          Αν δεν το βλέπετε, ελέγξτε τον φάκελο <strong>Spam/Junk</strong>.
        </p>
        <Link to="/login" className="text-blue-600 text-sm">Επιστροφή στη σύνδεση</Link>
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
