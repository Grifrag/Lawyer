import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Navbar - full width */}
      <nav className="w-full flex justify-between items-center px-12 py-4 border-b border-gray-200">
        <span className="font-bold text-xl">⚖️ Solon Checker</span>
        <div className="flex gap-3">
          <Link to="/login" className="border border-blue-700 text-blue-700 px-4 py-2 rounded hover:bg-blue-50 text-sm font-medium">Σύνδεση</Link>
          <Link to="/register" className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-800 text-sm font-medium">Εγγραφή</Link>
        </div>
      </nav>

      {/* Hero - full width with max-w for readability */}
      <main className="flex-1 w-full max-w-5xl mx-auto px-8 py-24 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6 leading-tight">
          Αυτόματη παρακολούθηση<br />δικαστικών αποφάσεων
        </h1>
        <p className="text-gray-500 text-xl mb-10">
          Ειδοποίηση αμέσως όταν βγει απόφαση στο solon.gov.gr
        </p>
        <Link
          to="/register"
          className="inline-block bg-blue-700 text-white px-10 py-4 rounded-lg text-lg font-semibold hover:bg-blue-800"
        >
          Ξεκινήστε — €15/μήνα
        </Link>

        {/* Features */}
        <div className="grid grid-cols-3 gap-8 mt-20 text-left">
          {[
            ['🔍', 'Αυτόματος έλεγχος', '3 φορές/μέρα στο solon.gov.gr'],
            ['📧', 'Άμεση ειδοποίηση', 'Email ή Telegram'],
            ['⚖️', 'Για δικηγόρους', 'Απλό, γρήγορο, αξιόπιστο'],
          ].map(([icon, title, desc]) => (
            <div key={title} className="p-6 border border-gray-200 rounded-xl hover:shadow-md transition-shadow">
              <p className="text-3xl mb-3">{icon}</p>
              <p className="font-semibold text-gray-900 text-lg mb-1">{title}</p>
              <p className="text-gray-500 text-sm">{desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full text-center py-6 text-gray-400 text-sm border-t border-gray-100">
        © 2026 Γρηγόριος Φραγκάκης — OptiGrid
      </footer>
    </div>
  )
}
