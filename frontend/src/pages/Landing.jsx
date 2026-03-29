import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Navbar */}
      <nav className="w-full flex justify-between items-center px-6 md:px-12 py-4 border-b border-gray-200">
        <span className="font-bold text-lg md:text-xl">⚖️ Solon Checker</span>
        <div className="flex gap-2 md:gap-3">
          <Link to="/login" className="border border-blue-700 text-blue-700 px-3 py-2 md:px-4 rounded hover:bg-blue-50 text-sm font-medium">Σύνδεση</Link>
          <Link to="/register" className="bg-blue-700 text-white px-3 py-2 md:px-4 rounded hover:bg-blue-800 text-sm font-medium">Εγγραφή</Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="flex-1 w-full max-w-5xl mx-auto px-6 md:px-8 py-10 md:py-16 text-center flex flex-col justify-center">
        <h1 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4 md:mb-6 leading-tight">
          Αυτόματη παρακολούθηση<br className="hidden md:block" /> δικαστικών αποφάσεων
        </h1>
        <p className="text-gray-500 text-lg md:text-xl mb-8 md:mb-10">
          Ειδοποίηση αμέσως όταν βγει απόφαση στο solon.gov.gr
        </p>
        <Link
          to="/register"
          className="inline-block bg-blue-700 text-white px-10 py-4 rounded-lg text-lg font-semibold hover:bg-blue-800"
        >
          Ξεκινήστε — €15/μήνα
        </Link>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8 mt-10 md:mt-14 text-left">
          {[
            ['🔍', 'Αυτόματος έλεγχος', '3 φορές/μέρα στο solon.gov.gr'],
            ['📧', 'Άμεση ειδοποίηση', 'Email ή Telegram'],
            ['⚖️', 'Για δικηγόρους', 'Απλό, γρήγορο, αξιόπιστο'],
          ].map(([icon, title, desc]) => (
            <div key={title} className="p-5 md:p-6 border border-gray-200 rounded-xl hover:shadow-md transition-shadow">
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
