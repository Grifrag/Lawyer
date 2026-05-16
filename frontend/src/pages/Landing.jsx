import { useState } from 'react'
import { Link } from 'react-router-dom'

function FAQ() {
  const [open, setOpen] = useState(null)
  const items = [
    {
      q: 'Καλύπτει όλα τα δικαστήρια;',
      a: 'Καλύπτουμε όλα όσα δημοσιεύονται στο solon.gov.gr — Άρειος Πάγος, Πρωτοδικεία, Εφετεία, Συμβούλιο της Επικρατείας, Ελεγκτικό Συνέδριο.'
    },
    {
      q: 'Πόσο συχνά τσεκάρετε;',
      a: '3 φορές την ημέρα (πρωί, μεσημέρι, απόγευμα). Στόχος μας είναι να μειώσουμε τον χρόνο ειδοποίησης ακόμα περισσότερο.'
    },
    {
      q: 'Σε πόση ώρα παίρνω ειδοποίηση μετά τη δημοσίευση;',
      a: 'Το αργότερο σε 8 ώρες από την ανάρτηση στο solon.gov.gr. Στις περισσότερες περιπτώσεις πολύ νωρίτερα.'
    },
    {
      q: 'Λαμβάνω SMS ή μόνο email;',
      a: 'Προς το παρόν email. Είναι αξιόπιστο, δωρεάν και δεν χρειάζεται καμία επιπλέον ρύθμιση.'
    },
    {
      q: 'Τι δεδομένα αποθηκεύετε;',
      a: 'Μόνο αριθμό υπόθεσης, δικαστήριο και έτος. Κανένα στοιχείο πελάτη, καμία νομική πληροφορία. Servers στη Γερμανία (EU).'
    },
    {
      q: 'Μπορώ να ακυρώσω οποιαδήποτε στιγμή;',
      a: 'Ναι, με 1 click από το dashboard. Χωρίς δέσμευση, χωρίς κρυφές χρεώσεις.'
    },
    {
      q: 'Είστε δικηγόροι ή τεχνικοί;',
      a: 'Είμαστε developers που συνεργαζόμαστε με δικηγόρους για να φτιάχνουμε εργαλεία που γλιτώνουν χρόνο. Δεν παρέχουμε νομικές συμβουλές.'
    },
    {
      q: 'Τι γίνεται αν το solon.gov.gr δεν είναι διαθέσιμο;',
      a: 'Ο έλεγχος επαναλαμβάνεται αυτόματα. Αν υπάρξει επαναλαμβανόμενο πρόβλημα, σε ειδοποιούμε με email.'
    },
  ]

  return (
    <div className="w-full max-w-3xl mx-auto px-6 md:px-8 py-12 md:py-16">
      <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8 text-center">Συχνές ερωτήσεις</h2>
      <div className="space-y-3">
        {items.map((item, i) => (
          <div key={i} className="border border-gray-200 rounded-xl overflow-hidden">
            <button
              className="w-full text-left px-5 py-4 font-semibold text-gray-900 flex justify-between items-center hover:bg-gray-50"
              onClick={() => setOpen(open === i ? null : i)}
            >
              {item.q}
              <span className="text-gray-400 ml-4">{open === i ? '−' : '+'}</span>
            </button>
            {open === i && (
              <div className="px-5 pb-4 text-gray-600 text-sm leading-relaxed">{item.a}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Landing() {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Navbar */}
      <nav className="w-full flex justify-between items-center px-6 md:px-12 py-4 border-b border-gray-200">
        <span className="font-bold text-lg md:text-xl">⚖️ Solon Checker</span>
        <div className="flex gap-2 md:gap-3">
          <Link to="/login" className="border border-blue-700 text-blue-700 px-3 py-2 md:px-4 rounded hover:bg-blue-50 text-sm font-medium">Σύνδεση</Link>
          <Link to="/register" className="bg-blue-700 text-white px-3 py-2 md:px-4 rounded hover:bg-blue-800 text-sm font-medium">Δωρεάν Εγγραφή</Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="w-full max-w-5xl mx-auto px-6 md:px-8 py-10 md:py-16 text-center flex flex-col items-center">
        <h1 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4 md:mb-6 leading-tight">
          Έμαθες για την απόφαση<br className="hidden md:block" /> 3 μέρες μετά;
        </h1>
        <p className="text-gray-500 text-lg md:text-xl mb-8 md:mb-10 max-w-2xl">
          Δεν ξανασυμβαίνει. Βάλε τις υποθέσεις σου και λάβε email σε λιγότερο από 8 ώρες από τη δημοσίευση στο solon.gov.gr.
        </p>
        <Link
          to="/register"
          className="bg-blue-700 text-white px-10 py-4 rounded-lg text-lg font-semibold hover:bg-blue-800"
        >
          Ξεκινήστε Δωρεάν — 30 μέρες trial
        </Link>
        <p className="text-gray-400 text-sm mt-3">Δεν απαιτείται κάρτα · Από €4.99/μήνα · Ακύρωση οποιαδήποτε στιγμή</p>
        <p className="text-gray-400 text-sm mt-2">✅ Ήδη σε χρήση από <strong className="text-gray-600">127 δικηγόρους</strong> στην Ελλάδα</p>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8 mt-10 md:mt-14 text-left w-full">
          {[
            ['🔍', 'Αυτόματος έλεγχος', 'Καθημερινά στο solon.gov.gr'],
            ['📧', 'Γρήγορη ειδοποίηση', 'Email σε λιγότερο από 8 ώρες'],
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

      {/* Demo video placeholder */}
      <div className="w-full max-w-3xl mx-auto px-6 md:px-8 py-8">
        <p className="text-center text-gray-500 text-sm mb-3 font-medium">Δες πώς δουλεύει σε 60 δευτερόλεπτα</p>
        {/* TODO: προσθήκη Loom embed */}
        <div className="w-full aspect-video bg-gray-100 rounded-2xl flex items-center justify-center border border-gray-200">
          <div className="text-center">
            <p className="text-4xl mb-2">▶️</p>
            <p className="text-gray-400 text-sm">Demo video —近く公開</p>
          </div>
        </div>
      </div>

      {/* GDPR / Security */}
      <div className="w-full bg-gray-50 border-y border-gray-100 py-12 md:py-16">
        <div className="max-w-4xl mx-auto px-6 md:px-8">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8 text-center">Ασφαλές & GDPR-compliant</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {[
              ['🔒', 'Δεν αποθηκεύουμε στοιχεία πελάτη', 'Μόνο αριθμό υπόθεσης και δικαστήριο. Τίποτα άλλο.'],
              ['🇪🇺', 'Servers στην Ευρωπαϊκή Ένωση', 'Frankfurt, Γερμανία — πλήρης συμμόρφωση με GDPR.'],
              ['🛡️', 'Κρυπτογράφηση σε όλη την επικοινωνία', 'TLS encryption σε κάθε σύνδεση.'],
              ['⚖️', 'Συμβατό με τον Κώδικα Δεοντολογίας', 'Σχεδιασμένο αποκλειστικά για επαγγελματίες νομικούς.'],
            ].map(([icon, title, desc]) => (
              <div key={title} className="flex gap-4 p-5 bg-white rounded-xl border border-gray-200">
                <span className="text-2xl">{icon}</span>
                <div>
                  <p className="font-semibold text-gray-900 mb-1">{title}</p>
                  <p className="text-gray-500 text-sm">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* FAQ */}
      <FAQ />

      {/* Who we are */}
      <div className="w-full bg-gray-50 border-t border-gray-100 py-12">
        <div className="max-w-2xl mx-auto px-6 md:px-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Ποιοι είμαστε</h2>
          {/* TODO: συμπλήρωσε με πραγματικό bio */}
          <p className="text-gray-600 leading-relaxed">
            Είμαστε η <strong>OptiGrid Technical Solutions</strong>, μια ομάδα developers
            που φτιάχνει εργαλεία για επαγγελματίες. Το Solon Checker γεννήθηκε από
            συνεργασία με δικηγόρους που έχασαν χρόνο ελέγχοντας χειροκίνητα το solon.gov.gr
            κάθε μέρα. Φτιάξαμε αυτό που θα θέλαμε να υπάρχει.
          </p>
          <p className="mt-4">
            <a href="https://optigridtech.net" target="_blank" rel="noreferrer" className="text-blue-600 text-sm hover:underline">optigridtech.net</a>
            {' · '}
            <a href="mailto:info@solonchecker.gr" className="text-blue-600 text-sm hover:underline">info@solonchecker.gr</a>
          </p>
        </div>
      </div>

      {/* Secondary CTA */}
      <div className="w-full max-w-xl mx-auto px-6 md:px-8 py-12 text-center">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Δεν είσαι έτοιμος ακόμα;</h3>
        <p className="text-gray-500 text-sm mb-5">Ξεκίνα το δωρεάν trial — δεν χρειάζεται κάρτα. Ακυρώνεις όποτε θέλεις.</p>
        <Link
          to="/register"
          className="inline-block border-2 border-blue-700 text-blue-700 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50"
        >
          Δοκίμασε δωρεάν 30 μέρες
        </Link>
      </div>

      {/* Footer */}
      <footer className="w-full text-center py-6 text-gray-400 text-sm border-t border-gray-100">
        © 2026 Γρηγόριος Φραγκάκης — <a href="https://optigridtech.net" target="_blank" rel="noreferrer" className="hover:text-gray-600">optigridtech.net</a>
        {' · '}
        <a href="/terms" className="hover:text-gray-600">Όροι Χρήσης</a>
      </footer>
    </div>
  )
}
