import os
import fitz  # PyMuPDF
import docx  # python-docx
import spacy

# Lade das mittlere deutsche Sprachmodell von spaCy
nlp = spacy.load("de_core_news_md")

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif ext == ".pdf":
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        elif ext == ".docx":
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"[!] Fehler bei {file_path}: {e}")

    return text

def extract_entities(text):
    doc = nlp(text)
    data = {
        "PER": set(),
        "LOC": set(),
        "ORG": set(),
        "DATE": set()
    }

    for ent in doc.ents:
        if ent.label_ in data:
            data[ent.label_].add(ent.text.strip())

    return data

def process_directory(directory_path, output_file):
    with open(output_file, "w", encoding="utf-8") as out:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"📄 Verarbeite: {file_path}")
                text = extract_text_from_file(file_path)
                if not text.strip():
                    continue

                entities = extract_entities(text)

                out.write(f"Datei: {file_path}\n")
                out.write(f"👤 Personen: {', '.join(entities['PER']) or '-'}\n")
                out.write(f"🌍 Orte: {', '.join(entities['LOC']) or '-'}\n")
                out.write(f"🏢 Organisationen: {', '.join(entities['ORG']) or '-'}\n")
                out.write(f"📅 Daten: {', '.join(entities['DATE']) or '-'}\n")
                out.write("-" * 60 + "\n")

    print(f"\n✅ Alle Entitäten gespeichert in: {output_file}")

# ➤ Beispiel: Pfad zu deinem Ordner mit Dateien
verzeichnis = r"V:\Test ABSTM-Institutionelle Zusammenarbeit\Ablieferung ABSTM\Test Migration\Test ABSTM-Institutionelle Zusammenarbeit\Ablieferung ABSTM\Test 2_ska\Test Konvertierung"
ausgabedatei = "entities_spacy_summary.txt"

process_directory(verzeichnis, ausgabedatei)
