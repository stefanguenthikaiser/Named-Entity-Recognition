import os
import torch
from transformers import BertTokenizer, BertForTokenClassification
from docx import Document
import fitz  # PyMuPDF für PDFs

# Modell und Tokenizer laden
model_path = r"C:/Users/u3atmz/Documents/Code Repositories/Named Entity Recognition/bert"  # Pfad zum Modell
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForTokenClassification.from_pretrained(model_path)

# Verarbeitungsfunktion für Texte
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
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"[!] Fehler bei {file_path}: {e}")
    
    return text

# Entitäten extrahieren
def extract_entities(text):
    # Sicherstellen, dass der Text maximal 512 Tokens enthält
    max_length = 512
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=max_length)
    
    with torch.no_grad():
        outputs = model(**inputs).logits
    predictions = torch.argmax(outputs, dim=2)
    
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    entity_types = predictions[0].tolist()

    entities = {"PERSON": [], "LOC": [], "ORG": []}
    
    for token, entity_type in zip(tokens, entity_types):
        if entity_type == 1:  # PERSON
            entities["PERSON"].append(token)
        elif entity_type == 2:  # LOC
            entities["LOC"].append(token)
        elif entity_type == 3:  # ORG
            entities["ORG"].append(token)
    
    return entities

# Hauptverarbeitungsfunktion für Verzeichnisse
def process_directory(directory_path, output_file):
    with open(output_file, "w", encoding="utf-8") as out:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"📄 Verarbeite: {file_path}")
                text = extract_text_from_file(file_path)
                if not text.strip():
                    continue

                # Text in kleinere Abschnitte teilen, wenn er zu lang ist
                chunk_size = 500  # Maximaler Abschnitt
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i+chunk_size]
                    entities = extract_entities(chunk)

                    out.write(f"Datei: {file_path}\n")
                    out.write(f"👤 Personen: {', '.join(entities['PERSON']) or '-'}\n")
                    out.write(f"🌍 Orte: {', '.join(entities['LOC']) or '-'}\n")
                    out.write(f"🏢 Dienste/Organisationen: {', '.join(entities['ORG']) or '-'}\n")
                    out.write("-" * 60 + "\n")
    
    print(f"\n✅ Alle Entitäten gespeichert in: {output_file}")

# ➤ Verzeichnis und Ausgabe festlegen
verzeichnis = r"V:\Test ABSTM-Institutionelle Zusammenarbeit\Ablieferung ABSTM\Test Migration\Test ABSTM-Institutionelle Zusammenarbeit\Ablieferung ABSTM\Test 2_ska\Test Konvertierung"  # z. B. "C:/Users/ich/Dokumente/testdaten"
ausgabedatei = "bert_ergebnisse.txt"

process_directory(verzeichnis, ausgabedatei)
