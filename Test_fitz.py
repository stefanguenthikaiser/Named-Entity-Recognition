try:
    import stanza
    print("✅ docx (PyMuPDF) ist korrekt importiert.")
except ImportError as e:
    print("❌ Fehler beim Importieren von docx:", e)
