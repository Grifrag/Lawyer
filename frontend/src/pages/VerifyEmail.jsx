import { useSearchParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import client from '../api/client'

export default function VerifyEmail() {
  const [params] = useSearchParams()
  const [status, setStatus] = useState('pending')
  useEffect(() => {
    const token = params.get('token')
    if (token) {
      client.post('/auth/verify-email', { token })
        .then(() => setStatus('success'))
        .catch(() => setStatus('error'))
    }
  }, [params])
  return (
    <div className="min-h-screen flex items-center justify-center">
      {status === 'pending' && <p>Αναμονή επαλήθευσης...</p>}
      {status === 'success' && <p>✅ Email επαληθεύτηκε! <a href="/login" className="text-blue-600">Σύνδεση</a></p>}
      {status === 'error' && <p>❌ Μη έγκυρος σύνδεσμος.</p>}
    </div>
  )
}
