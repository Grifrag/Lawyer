import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../api/client'
import Navbar from '../components/Navbar'

// Court names exactly as they appear in solon.gov.gr dropdown
const COURTS = [
  'ΑΡΕΙΟΣ ΠΑΓΟΣ',
  'ΕΦΕΤΕΙΟ ΑΘΗΝΩΝ',
  'ΕΦΕΤΕΙΟ ΑΙΓΑΙΟΥ',
  'ΕΦΕΤΕΙΟ ΑΝΑΤΟΛΙΚΗΣ ΚΡΗΤΗΣ',
  'ΕΦΕΤΕΙΟ ΒΟΡΕΙΟΥ ΑΙΓΑΙΟΥ',
  'ΕΦΕΤΕΙΟ ΔΥΤ.ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ',
  'ΕΦΕΤΕΙΟ ΔΥΤΙΚΗΣ ΜΑΚΕΔΟΝΙΑΣ',
  'ΕΦΕΤΕΙΟ ΔΩΔΕΚΑΝΗΣΟΥ',
  'ΕΦΕΤΕΙΟ ΕΥΒΟΙΑΣ',
  'ΕΦΕΤΕΙΟ ΘΕΣΣΑΛΟΝΙΚΗΣ',
  'ΕΦΕΤΕΙΟ ΘΡΑΚΗΣ',
  'ΕΦΕΤΕΙΟ ΙΩΑΝΝΙΝΩΝ',
  'ΕΦΕΤΕΙΟ ΚΑΛΑΜΑΤΑΣ',
  'ΕΦΕΤΕΙΟ ΚΕΡΚΥΡΑΣ',
  'ΕΦΕΤΕΙΟ ΚΡΗΤΗΣ',
  'ΕΦΕΤΕΙΟ ΛΑΜΙΑΣ',
  'ΕΦΕΤΕΙΟ ΛΑΡΙΣΑΣ',
  'ΕΦΕΤΕΙΟ ΝΑΥΠΛΙΟΥ',
  'ΕΦΕΤΕΙΟ ΠΑΤΡΩΝ',
  'ΕΦΕΤΕΙΟ ΠΕΙΡΑΙΩΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΑΘΗΝΩΝ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ  (ΑΓΡΙΝ.& ΜΕΣΟΛ.)',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΑΛΕΞΑΝΔΡΟΥΠΟΛΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΑΜΦΙΣΣΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΑΡΤΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΑΧΑΪΑΣ (ΠΑΤΡΩΝ & ΑΙΓΙΟΥ & ΚΑΛΑΒΡ.)',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΒΕΡΟΙΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΒΟΙΩΤΙΑΣ (ΛΙΒΑΔ. & ΘΗΒΩΝ)',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΒΟΛΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΓΙΑΝΝΙΤΣΩΝ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΓΡΕΒΕΝΩΝ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΔΡΑΜΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΕΔΕΣΣΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΕΥΡΥΤΑΝΙΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΖΑΚΥΝΘΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΗΛΕΙΑΣ (ΠΥΡΓΟΥ & ΑΜΑΛ.)',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΗΡΑΚΛΕΙΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΘΕΣΠΡΩΤΙΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΘΕΣΣΑΛΟΝΙΚΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΑΒΑΛΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΑΡΔΙΤΣΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΑΣΤΟΡΙΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΑΤΕΡΙΝΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΕΡΚΥΡΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΕΦΑΛΛΗΝΙΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΙΛΚΙΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΟΖΑΝΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΟΡΙΝΘΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΚΩ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΛΑΚΩΝΙΑΣ  (ΣΠΑΡΤΗΣ & ΓΥΘΕΙΟΥ)',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΛΑΜΙΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΛΑΡΙΣΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΛΑΣΙΘΙΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΛΕΥΚΑΔΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΜΕΣΣΗΝΙΑΣ (ΚΑΛΑΜ. & ΚΥΠΑΡ.)',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΜΥΤΙΛΗΝΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΝΑΥΠΛΙΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΞΑΝΘΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΟΡΕΣΤΙΑΔΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΠΕΙΡΑΙΑ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΠΡΕΒΕΖΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΡΕΘΥΜΝΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΡΟΔΟΠΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΡΟΔΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΣΑΜΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΣΕΡΡΩΝ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΣΥΡΟΥ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΤΡΙΚΑΛΩΝ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΤΡΙΠΟΛΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΦΛΩΡΙΝΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΧΑΛΚΙΔΑΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΧΑΛΚΙΔΙΚΗΣ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΧΑΝΙΩΝ',
  'ΠΡΩΤΟΔΙΚΕΙΟ ΧΙΟΥ',
]

export default function CaseNew() {
  const nav = useNavigate()
  const [form, setForm] = useState({
    court: '', search_type: 'GAK', number: '', year: new Date().getFullYear(), description: ''
  })
  const [error, setError] = useState('')
  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  const submit = async e => {
    e.preventDefault()
    try {
      await client.post('/cases', form)
      nav('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Σφάλμα')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-lg mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">Νέα Υπόθεση</h1>
        {error && <p className="text-red-600 mb-4">{error}</p>}
        <form onSubmit={submit} className="bg-white p-6 rounded shadow flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Δικαστήριο</label>
            <select className="w-full border rounded p-2" value={form.court} onChange={set('court')} required>
              <option value="">-- Επιλέξτε δικαστήριο --</option>
              {COURTS.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Τύπος αναζήτησης</label>
            <select className="w-full border rounded p-2" value={form.search_type} onChange={set('search_type')}>
              <option value="GAK">ΓΑΚ</option>
              <option value="EAK">ΕΑΚ</option>
            </select>
          </div>
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1">Αριθμός</label>
              <input className="w-full border rounded p-2" value={form.number}
                     onChange={set('number')} required />
            </div>
            <div className="w-28">
              <label className="block text-sm font-medium mb-1">Έτος</label>
              <input className="w-full border rounded p-2" type="number"
                     value={form.year} onChange={set('year')} required />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Περιγραφή (προαιρετικό)</label>
            <input className="w-full border rounded p-2" value={form.description}
                   onChange={set('description')} />
          </div>
          <button className="bg-blue-700 text-white py-2 rounded font-semibold">Αποθήκευση</button>
        </form>
      </div>
    </div>
  )
}
