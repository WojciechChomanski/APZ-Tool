import pdfplumber
import pandas as pd
from typing import List, Dict


def extract_positions_from_drawing(pdf_path: str) -> List[Dict]:
    """
    Extrahiert Positionen aus der Stückliste der Zeichnung (Hauptansichten PDF).
    Gibt eine Liste von Dictionaries zurück mit:
    - position
    - material
    - length
    - width
    """
    positions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 3:
                    continue

                # Suche nach typischen Spaltenüberschriften der Stückliste
                header = [str(cell).strip().lower() if cell else "" for cell in table[0]]

                # Mögliche Spaltennamen (anpassen je nach PDF)
                pos_col = next((i for i, h in enumerate(header) if "pos" in h or "h-pos" in h), None)
                material_col = next((i for i, h in enumerate(header) if "material" in h or "werkstoff" in h), None)
                length_col = next((i for i, h in enumerate(header) if "länge" in h or "length" in h), None)
                width_col = next((i for i, h in enumerate(header) if "breite" in h or "width" in h), None)

                if pos_col is None or material_col is None:
                    continue  # Diese Tabelle ist wahrscheinlich nicht die Stückliste

                for row in table[1:]:  # Header überspringen
                    if not row or not row[pos_col]:
                        continue

                    position = str(row[pos_col]).strip()
                    material = str(row[material_col]).strip() if row[material_col] else ""
                    length = str(row[length_col]).strip() if length_col and row[length_col] else ""
                    width = str(row[width_col]).strip() if width_col and row[width_col] else ""

                    # Nur relevante Positionen aufnehmen (z. B. die mit grüner Markierung in deinem Fall)
                    if position and material:
                        positions.append({
                            "position": position,
                            "material": material,
                            "length": length,
                            "width": width,
                            "source": "Zeichnung"
                        })

    return positions


# ====================== TEST ======================
if __name__ == "__main__":
    drawing_pdf = "402-ST-02502-a_Schuss 29-30 Segment A - Hauptansichten Teil 1_Kom_nic.pdf"

    result = extract_positions_from_drawing(drawing_pdf)

    print(f"Gefundene Positionen aus der Zeichnung: {len(result)}")
    for pos in result[:10]:   # Zeige die ersten 10 zum Testen
        print(pos)