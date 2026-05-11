import { Link } from 'react-router-dom'

export default function Terms() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="mb-8">
          <Link to="/" className="text-blue-600 text-sm">← Επιστροφή</Link>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">Όροι Χρήσης</h1>
        <p className="text-gray-500 text-sm mb-10">Τελευταία ενημέρωση: Μάιος 2026</p>

        <div className="bg-white rounded-xl shadow-sm p-8 space-y-8 text-gray-700 leading-relaxed">

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Γενικά</h2>
            <p>
              Η υπηρεσία <strong>Solon Checker</strong> («Υπηρεσία») παρέχεται από την
              <strong> OptiGrid Technical Solutions</strong> («Εταιρεία»). Η χρήση της
              Υπηρεσίας συνεπάγεται την ανεπιφύλακτη αποδοχή των παρόντων Όρων Χρήσης.
              Εάν δεν συμφωνείτε, παρακαλούμε να μην κάνετε χρήση της Υπηρεσίας.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Περιγραφή Υπηρεσίας</h2>
            <p>
              Το Solon Checker είναι εργαλείο αυτοματοποιημένης παρακολούθησης δικαστικών
              αποφάσεων μέσω του δημόσιου συστήματος <strong>solon.gov.gr</strong>. Η
              Υπηρεσία εκτελεί αυτόματους ελέγχους και αποστέλλει ειδοποιήσεις μέσω
              email όταν εντοπιστεί νέα δικαστική απόφαση για υπόθεση που παρακολουθείτε.
            </p>
            <p className="mt-3">
              Η Υπηρεσία <strong>δεν παρέχει νομικές συμβουλές</strong> και δεν υποκαθιστά
              τον δικηγόρο σας. Αποτελεί αποκλειστικά εργαλείο ενημέρωσης.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">3. Εγγραφή & Λογαριασμός</h2>
            <p>
              Για τη χρήση της Υπηρεσίας απαιτείται δημιουργία λογαριασμού με έγκυρη
              διεύθυνση email. Ο χρήστης είναι αποκλειστικά υπεύθυνος για τη διαφύλαξη
              των στοιχείων πρόσβασής του. Κάθε δραστηριότητα που πραγματοποιείται μέσω
              του λογαριασμού σας θεωρείται δική σας.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Δοκιμαστική Περίοδος & Συνδρομή</h2>
            <p>
              Κάθε νέος χρήστης λαμβάνει <strong>30 ημέρες δωρεάν</strong> πρόσβαση σε
              όλες τις λειτουργίες της Υπηρεσίας. Μετά τη λήξη της δοκιμαστικής περιόδου,
              απαιτείται ενεργή συνδρομή για συνέχιση χρήσης.
            </p>
            <p className="mt-3">
              Η χρέωση της συνδρομής ανέρχεται σε <strong>€4,99/μήνα</strong> και
              ανανεώνεται αυτόματα. Η ακύρωση μπορεί να γίνει οποιαδήποτε στιγμή, με
              ισχύ από την επόμενη περίοδο χρέωσης. Δεν προβλέπεται επιστροφή χρημάτων
              για ήδη χρεωμένες περιόδους.
            </p>
            <p className="mt-3">
              Οι πληρωμές διεκπεραιώνονται μέσω <strong>Stripe</strong>. Η Εταιρεία δεν
              αποθηκεύει στοιχεία πιστωτικών καρτών.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Περιορισμός Ευθύνης</h2>
            <p>
              Η Εταιρεία καταβάλλει κάθε δυνατή προσπάθεια για αξιόπιστη και έγκαιρη
              παροχή της Υπηρεσίας. Ωστόσο, <strong>δεν εγγυάται</strong> αδιάλειπτη
              λειτουργία, καθώς η Υπηρεσία εξαρτάται από τη διαθεσιμότητα εξωτερικών
              συστημάτων (solon.gov.gr).
            </p>
            <p className="mt-3">
              Η Εταιρεία δεν φέρει ευθύνη για ζημίες που προκύπτουν από:
            </p>
            <ul className="list-disc ml-6 mt-2 space-y-1">
              <li>Καθυστέρηση ή παράλειψη ειδοποίησης λόγω βλάβης τρίτων συστημάτων</li>
              <li>Αποφάσεις που ελήφθησαν βάσει πληροφοριών από την Υπηρεσία</li>
              <li>Προσωρινή μη διαθεσιμότητα της Υπηρεσίας</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Προστασία Δεδομένων (GDPR)</h2>
            <p>
              Η Εταιρεία επεξεργάζεται τα προσωπικά δεδομένα σας (email, στοιχεία
              υποθέσεων) αποκλειστικά για την παροχή της Υπηρεσίας, σύμφωνα με τον
              Γενικό Κανονισμό Προστασίας Δεδομένων (GDPR — Κανονισμός ΕΕ 2016/679).
            </p>
            <p className="mt-3">Έχετε δικαίωμα:</p>
            <ul className="list-disc ml-6 mt-2 space-y-1">
              <li>Πρόσβασης στα δεδομένα σας</li>
              <li>Διόρθωσης ή διαγραφής τους</li>
              <li>Φορητότητας δεδομένων</li>
              <li>Ανάκλησης συγκατάθεσης οποιαδήποτε στιγμή</li>
            </ul>
            <p className="mt-3">
              Για οποιοδήποτε αίτημα σχετικά με τα δεδομένα σας, επικοινωνήστε στο{' '}
              <a href="mailto:info@solonchecker.gr" className="text-blue-600">info@solonchecker.gr</a>.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Τροποποίηση Όρων</h2>
            <p>
              Η Εταιρεία διατηρεί το δικαίωμα τροποποίησης των παρόντων Όρων. Οι
              χρήστες θα ενημερώνονται μέσω email τουλάχιστον 15 ημέρες πριν την έναρξη
              ισχύος των αλλαγών.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Εφαρμοστέο Δίκαιο</h2>
            <p>
              Οι παρόντες Όροι διέπονται από το ελληνικό δίκαιο. Για κάθε διαφορά
              αρμόδια είναι τα δικαστήρια της Αθήνας.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Επικοινωνία</h2>
            <p>
              OptiGrid Technical Solutions<br />
              Email:{' '}
              <a href="mailto:info@solonchecker.gr" className="text-blue-600">info@solonchecker.gr</a><br />
              Ιστότοπος:{' '}
              <a href="https://optigridtech.net" className="text-blue-600">optigridtech.net</a>
            </p>
          </section>

        </div>
      </div>
    </div>
  )
}
