import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from typing import List
from apz_pdf_parser import extract_apz_data  # # Holt Daten aus Parser

def build_dataframe(pdf_paths: List[str]) -> pd.DataFrame:
    # # Baut DataFrame aus extrahierten Daten (12 Zeilen)
    data = extract_apz_data(pdf_paths)
    df = pd.DataFrame(data)
    return df

def export_to_excel(df: pd.DataFrame, filename: str = "APZ_Zusammenfassung_2025.xlsx") -> None:
    # # Exportiert zu Excel mit fettem Header (21 Spalten)
    wb = Workbook()
    ws = wb.active
    ws.title = "APZ Daten"

    # # Header schreiben und fett machen
    header = list(df.columns)
    for col_num, value in enumerate(header, 1):
        cell = ws.cell(row=1, column=col_num, value=value)
        cell.font = Font(bold=True)

    # # Datenzeilen schreiben (ab Zeile 2)
    for r_idx, row in df.iterrows():
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx + 2, column=c_idx, value=value)

    wb.save(filename)  # # Speichert im Ordner