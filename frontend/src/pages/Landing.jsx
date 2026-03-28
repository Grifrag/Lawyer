import { Link } from 'react-router-dom'
export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      <nav className="flex justify-between items-center px-8 py-4 border-b">
        <span className="font-bold text-xl">⚖️ Solon Checker</span>
        <div className="flex gap-4">
          <Link to="/login" className="border border-blue-700 text-blue-700 px-4 py-2 rounded hover:bg-blue-50">Σύνδεση</Link>
          <Link to="/register" className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-800">Εγγραφή</Link>
        </div>
      </nav>
      <div className="max-w-2xl mx-auto text-center py-24 px-6">
        <h1 className="text-4xl font-bold mb-4">Αυτόματη παρακολούθηση δικαστικών αποφάσεων</h1>
        <p className="text-gray-600 text-lg mb-8">Ειδοποίηση αμέσως όταν βγει απόφαση στο solon.gov.gr</p>
        <div className="flex justify-center gap-4 mb-16">
          <Link to="/register" className="bg-blue-700 text-white px-8 py-3 rounded-lg text-lg font-semibold">
            Ξεκινήστε — €15/μήνα
          </Link>
        </div>
        <div className="grid grid-cols-3 gap-6 text-left">
          {[
            ['🔍', 'Αυτόματος έλεγχος', '3 φορές/μέρα στο solon.gov.gr'],
            ['📧', 'Άμεση ειδοποίηση', 'Email ή Telegram'],
            ['⚖️', 'Για δικηγόρους', 'Απλό, γρήγορο, αξιόπιστο'],
          ].map(([icon, title, desc]) => (
            <div key={title} className="p-4 border rounded-lg">
              <p className="text-2xl mb-2">{icon}</p>
              <p className="font-semibold">{title}</p>
              <p className="text-gray-500 text-sm">{desc}</p>
            </div>
          ))}
        </div>
        <footer className="mt-16 text-gray-400 text-sm">
          © 2026 Γρηγόριος Φραγκάκης — OptiGrid
        </footer>
      </div>
    </div>
  )
}
