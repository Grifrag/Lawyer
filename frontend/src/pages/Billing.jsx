import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import client from '../api/client'
import Navbar from '../components/Navbar'

export default function Billing() {
  const [params] = useSearchParams()
  const nav = useNavigate()
  const [polling, setPolling] = useState(!!params.get('session_id'))

  useEffect(() => {
    if (!polling) return
    const timer = setTimeout(() => setPolling(false), 15000)
    return () => clearTimeout(timer)
  }, [polling])

  const { data } = useQuery({
    queryKey: ['billing'],
    queryFn: () => client.get('/billing/status').then(r => r.data),
    refetchInterval: polling ? 2000 : false,
  })

  useEffect(() => {
    if (polling && data?.subscription_status === 'active') {
      setPolling(false)
      nav('/dashboard')
    }
  }, [data, polling, nav])

  const subscribe = async () => {
    const { data: d } = await client.post('/billing/checkout')
    window.location.href = d.url
  }
  const manage = async () => {
    const { data: d } = await client.post('/billing/portal')
    window.location.href = d.url
  }

  const status = data?.subscription_status

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-md mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">Συνδρομή</h1>
        {polling && <p className="mb-4 text-blue-600">⏳ Επεξεργασία πληρωμής...</p>}
        <div className="bg-white p-6 rounded shadow">
          <p className="mb-2"><strong>Κατάσταση:</strong> {
            status === 'active' ? '✅ Ενεργή' :
            status === 'past_due' ? '⚠️ Εκπρόθεσμη πληρωμή' :
            status === 'cancelled' ? '❌ Ακυρωμένη' : '— Ανενεργή'
          }</p>
          <p className="mb-6 text-gray-600 text-sm">€4.99/μήνα · Ακύρωση οποιαδήποτε στιγμή</p>
          {status === 'active'
            ? <button onClick={manage} className="w-full bg-gray-200 py-2 rounded">Διαχείριση Συνδρομής</button>
            : <button onClick={subscribe} className="w-full bg-blue-700 text-white py-2 rounded font-semibold">Εγγραφή — €4.99/μήνα</button>
          }
        </div>
      </div>
    </div>
  )
}
