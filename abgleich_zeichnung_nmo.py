import pdfplumber
from typing import List, Dict


def extract_positions_from_drawing(pdf_path: str) -> List[Dict]:
    """
    Verbesserte Version zum Auslesen der Stückliste aus der Zeichnung.
    Versucht, Position, Material, Länge und Breite zu erkennen.
    """
    positions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Header der Tabelle analysieren
                header_row = table[0]
                header = [str(cell).strip().lower() if cell else "" for cell in header_row]

                # Spaltenindex suchen (flexibler als vorher)
                pos_idx = next((i for i, h in enumerate(header) if any(x in h for x in ["pos", "h-pos", "cad-pos"])), None)
                material_idx = next((i for i, h in enumerate(header) if any(x in h for x in ["material", "werkstoff"])), None)
                length_idx = next((i for i, h in enumerate(header) if any(x in h for x in ["länge", "length", "länge tb"])), None)
                width_idx = next((i for i, h in enumerate(header) if any(x in h for x in ["breite", "width", "breite tb"])), None)

                if pos_idx is None or material_idx is None:
                    continue  # Keine Stückliste

                for row in table[1:]:
                    if not row or not row[pos_idx]:
                        continue

                    position = str(row[pos_idx]).strip()
                    material = str(row[material_idx]).strip() if row[material_idx] else ""
                    length = str(row[length_idx]).strip() if length_idx and row[length_idx] else ""
                    width = str(row[width_idx]).strip() if width_idx and row[width_idx] else ""

                    # Nur sinnvolle Einträge aufnehmen
                    if position and material and len(position) > 2:
                        positions.append({
                            "position": position,
                            "material": material,
                            "length": length,
                            "width": width
                        })

    return positions


# ====================== TEST ======================
if __name__ == "__main__":
    pdf_path = "402-ST-02502-a_Schuss 29-30 Segment A - Hauptansichten Teil 1_Kom_nic.pdf"

    result = extract_positions_from_drawing(pdf_path)
    print(f"Gefundene Positionen: {len(result)}")

    for item in result[:15]:
        print(item)