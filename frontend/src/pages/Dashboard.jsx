import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import client from '../api/client'
import Navbar from '../components/Navbar'

function CaseCard({ c, onDelete, onToggle }) {
  const latest = c.latest_result
  return (
    <div className={`border rounded p-4 ${!c.active ? 'opacity-50' : ''}`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="font-semibold">{c.court}</p>
          <p className="text-sm text-gray-600">{c.search_type} {c.number}/{c.year}</p>
          {c.description && <p className="text-sm text-gray-500">{c.description}</p>}
        </div>
        <div className="flex gap-2 text-sm">
          <Link to={`/cases/${c.id}/edit`} className="text-blue-600">✏️</Link>
          <button onClick={() => onToggle(c)} className="text-yellow-600">
            {c.active ? '⏸' : '▶️'}
          </button>
          <button onClick={() => onDelete(c.id)} className="text-red-600">🗑</button>
        </div>
      </div>
      {latest && (
        <div className={`mt-2 p-2 rounded text-sm ${latest.decision_number ? 'bg-green-50' : 'bg-gray-50'}`}>
          {latest.decision_number
            ? <><strong>Απόφαση {latest.decision_number}/{latest.decision_year}:</strong> {latest.result_text}
               {' '}<a href={latest.decision_link} target="_blank" rel="noreferrer" className="text-blue-600 underline">Άνοιγμα</a></>
            : <span className="text-gray-500">Εκκρεμεί · Τελ. έλεγχος: {latest.checked_at?.slice(0,10)}</span>
          }
        </div>
      )}
      {!latest && <p className="mt-2 text-sm text-gray-400">Δεν έχει ελεγχθεί ακόμα</p>}
    </div>
  )
}

export default function Dashboard() {
  const qc = useQueryClient()
  const { data: cases = [], isLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: () => client.get('/cases').then(r => r.data)
  })
  const del = useMutation({
    mutationFn: id => client.delete(`/cases/${id}`),
    onSuccess: () => qc.invalidateQueries(['cases'])
  })
  const toggle = useMutation({
    mutationFn: c => client.patch(`/cases/${c.id}`, { active: !c.active }),
    onSuccess: () => qc.invalidateQueries(['cases'])
  })
  const runNow = useMutation({
    mutationFn: () => client.post('/checks/run-now'),
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-3xl mx-auto p-4 md:p-6">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6">
          <h1 className="text-2xl font-bold">Υποθέσεις</h1>
          <div className="flex gap-3">
            <button onClick={() => runNow.mutate()}
                    disabled={runNow.isPending}
                    className="bg-gray-200 px-3 py-2 rounded text-sm flex-1 sm:flex-none">
              {runNow.isPending ? '⏳ Έλεγχος...' : '🔄 Έλεγχος τώρα'}
            </button>
            <Link to="/cases/new"
                  className="bg-blue-700 text-white px-3 py-2 rounded text-sm flex-1 sm:flex-none text-center">
              + Νέα Υπόθεση
            </Link>
          </div>
        </div>
        {isLoading && <p>Φόρτωση...</p>}
        {!isLoading && cases.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <p className="text-4xl mb-4">⚖️</p>
            <p>Δεν έχετε υποθέσεις. <Link to="/cases/new" className="text-blue-600">Προσθέστε μία</Link></p>
          </div>
        )}
        <div className="flex flex-col gap-4">
          {cases.map(c => (
            <CaseCard key={c.id} c={c}
                      onDelete={id => del.mutate(id)}
                      onToggle={c => toggle.mutate(c)} />
          ))}
        </div>
      </div>
    </div>
  )
}
