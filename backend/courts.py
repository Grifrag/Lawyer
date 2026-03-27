# Courts as displayed in solon.gov.gr dropdown
# Key: display name shown to user (must match solon.gov.gr visible text exactly)
# Value: documentation identifier only — the scraper selects by visible text, not by value
# NOTE: These values are placeholder identifiers. The actual solon.gov.gr internal
# dropdown values are irrelevant because Playwright selects courts by visible label text.
# The real dropdown text labels must be verified during integration testing (Task 9).
COURTS = {
    "Άρειος Πάγος": "AREIOS_PAGOS",
    "Εφετείο Αθηνών": "EFETEIO_ATHINON",
    "Εφετείο Πειραιώς": "EFETEIO_PEIRAIOS",
    "Εφετείο Θεσσαλονίκης": "EFETEIO_THESSALONIKIS",
    "Εφετείο Πατρών": "EFETEIO_PATRON",
    "Εφετείο Λάρισας": "EFETEIO_LARISAS",
    "Εφετείο Ναυπλίου": "EFETEIO_NAFPLIOU",
    "Εφετείο Δωδεκανήσου": "EFETEIO_DODEKANISOU",
    "Εφετείο Κρήτης": "EFETEIO_KRITIS",
    "Εφετείο Ιωαννίνων": "EFETEIO_IOANNINON",
    "Πρωτοδικείο Αθηνών": "PROTODIKEIO_ATHINON",
    "Πρωτοδικείο Πειραιώς": "PROTODIKEIO_PEIRAIOS",
    "Πρωτοδικείο Θεσσαλονίκης": "PROTODIKEIO_THESSALONIKIS",
    "Πρωτοδικείο Πατρών": "PROTODIKEIO_PATRON",
    "Πρωτοδικείο Λάρισας": "PROTODIKEIO_LARISAS",
    "Πρωτοδικείο Βόλου": "PROTODIKEIO_VOLOU",
    "Πρωτοδικείο Χαλκίδας": "PROTODIKEIO_XALKIDAS",
    "Πρωτοδικείο Λιβαδειάς": "PROTODIKEIO_LIVADEIAS",
    "Πρωτοδικείο Ναυπλίου": "PROTODIKEIO_NAFPLIOU",
    "Πρωτοδικείο Κορίνθου": "PROTODIKEIO_KORINTHOU",
    "Πρωτοδικείο Σπάρτης": "PROTODIKEIO_SPARTIS",
    "Πρωτοδικείο Καλαμάτας": "PROTODIKEIO_KALAMATAS",
    "Πρωτοδικείο Ιωαννίνων": "PROTODIKEIO_IOANNINON",
    "Πρωτοδικείο Κέρκυρας": "PROTODIKEIO_KERKYRAS",
    "Πρωτοδικείο Τρικάλων": "PROTODIKEIO_TRIKALON",
    "Πρωτοδικείο Γρεβενών": "PROTODIKEIO_GREVENON",
    "Πρωτοδικείο Κοζάνης": "PROTODIKEIO_KOZANIS",
    "Πρωτοδικείο Κατερίνης": "PROTODIKEIO_KATERINIS",
    "Πρωτοδικείο Βέροιας": "PROTODIKEIO_VEROIAS",
    "Πρωτοδικείο Σερρών": "PROTODIKEIO_SERRON",
    "Πρωτοδικείο Καβάλας": "PROTODIKEIO_KAVALAS",
    "Πρωτοδικείο Ξάνθης": "PROTODIKEIO_XANTHIS",
    "Πρωτοδικείο Αλεξανδρούπολης": "PROTODIKEIO_ALEXANDROUPOLIS",
    "Πρωτοδικείο Ρόδου": "PROTODIKEIO_RODOU",
    "Πρωτοδικείο Ηρακλείου": "PROTODIKEIO_IRAKLIOU",
    "Πρωτοδικείο Χανίων": "PROTODIKEIO_XANION",
    "Πρωτοδικείο Ρεθύμνου": "PROTODIKEIO_RETHYMNOU",
    "Ειρηνοδικείο Αθηνών": "EIRINO_ATHINON",
    "Ειρηνοδικείο Πειραιώς": "EIRINO_PEIRAIOS",
    "Ειρηνοδικείο Θεσσαλονίκης": "EIRINO_THESSALONIKIS",
}


def get_court_names():
    return sorted(COURTS.keys())


def get_court_value(name):
    return COURTS.get(name)
