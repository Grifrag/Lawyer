import { useState, useEffect } from 'react'
import client from '../api/client'
import Navbar from '../components/Navbar'

export default function Settings() {
  const [form, setForm] = useState({
    notification_type: '', gmail_sender: '', gmail_recipient: '',
    gmail_app_password: '', telegram_bot_token: '', telegram_chat_id: ''
  })
  const [msg, setMsg] = useState('')
  const set = k => e => setForm(f => ({...f, [k]: e.target.value}))

  useEffect(() => {
    client.get('/settings').then(r => setForm(f => ({...f, ...r.data})))
  }, [])

  const SENSITIVE_KEYS = ['gmail_app_password', 'telegram_bot_token']
  const save = async e => {
    e.preventDefault()
    const payload = Object.fromEntries(
      Object.entries(form).filter(([k, v]) => !SENSITIVE_KEYS.includes(k) || v !== '')
    )
    await client.post('/settings', payload)
    setMsg('✅ Αποθηκεύτηκε')
    setTimeout(() => setMsg(''), 3000)
  }

  const test = async () => {
    const r = await client.post('/settings/test')
    setMsg(r.data.message)
    setTimeout(() => setMsg(''), 5000)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-lg mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">Ρυθμίσεις Ειδοποιήσεων</h1>
        {msg && <p className="mb-4 text-sm">{msg}</p>}
        <form onSubmit={save} className="bg-white p-6 rounded shadow flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Τύπος ειδοποίησης</label>
            <select className="w-full border rounded p-2" value={form.notification_type} onChange={set('notification_type')}>
              <option value="">-- Επιλέξτε --</option>
              <option value="gmail">Gmail</option>
              <option value="telegram">Telegram</option>
              <option value="both">Και τα δύο</option>
            </select>
          </div>
          {['gmail','both'].includes(form.notification_type) && <>
            <input className="w-full border rounded p-2" placeholder="Gmail αποστολέα (π.χ. sender@gmail.com)"
                   value={form.gmail_sender} onChange={set('gmail_sender')} />
            <input className="w-full border rounded p-2" placeholder="Gmail παραλήπτη"
                   value={form.gmail_recipient} onChange={set('gmail_recipient')} />
            <input className="w-full border rounded p-2" type="password" placeholder="App Password Gmail"
                   value={form.gmail_app_password} onChange={set('gmail_app_password')} />
          </>}
          {['telegram','both'].includes(form.notification_type) && <>
            <input className="w-full border rounded p-2" placeholder="Telegram Bot Token"
                   value={form.telegram_bot_token} onChange={set('telegram_bot_token')} />
            <input className="w-full border rounded p-2" placeholder="Telegram Chat ID"
                   value={form.telegram_chat_id} onChange={set('telegram_chat_id')} />
          </>}
          <div className="flex gap-3">
            <button type="submit" className="flex-1 bg-blue-700 text-white py-2 rounded">Αποθήκευση</button>
            <button type="button" onClick={test} className="flex-1 bg-gray-200 py-2 rounded">Δοκιμαστική</button>
          </div>
        </form>
      </div>
    </div>
  )
}
