from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                               QPushButton, QLineEdit, QLabel, QFileDialog, 
                               QProgressBar, QTextEdit, QGroupBox, QCheckBox, QScrollArea)
from PySide6.QtCore import QThread, Signal
import pandas as pd
from apz_core import build_dataframe, export_to_excel
import os

# Alle verfügbaren Spalten (du kannst das später erweitern)
AVAILABLE_COLUMNS = [
    'WE-Nr.', 'Hersteller', 'Zeugnisnr.', 'Schmelze', 'Walztafel', 
    'Material', 't (mm)', 'APZ', 'DBS', 'Schmelzanalyse', 'Mech. Kennw.',
    'UT E1/S1 >10mm', 'Oberfläche', 'Grenzabmaße', 'Aubitz t>30', 
    'Radioaktiv.', 'CE', 'Z35', 'Bemerkung'
]

class ParseThread(QThread):
    progress = Signal(int)
    log = Signal(str)

    def __init__(self, pdf_paths, excel_paths, out_file, selected_columns):
        super().__init__()
        self.pdf_paths = pdf_paths
        self.excel_paths = excel_paths
        self.out_file = out_file
        self.selected_columns = selected_columns

    def run(self):
        self.log.emit("Starte Verarbeitung...")
        self.progress.emit(10)

        df = build_dataframe(self.pdf_paths)

        # Nur ausgewählte Spalten behalten
        if self.selected_columns:
            df = df[[col for col in self.selected_columns if col in df.columns]]

        for excel in self.excel_paths:
            try:
                df_excel = pd.read_excel(excel)
                df = pd.concat([df, df_excel], ignore_index=True)
            except Exception as e:
                self.log.emit(f"Excel-Fehler: {e}")

        self.progress.emit(60)
        export_to_excel(df, self.out_file, columns=self.selected_columns)
        self.progress.emit(100)
        self.log.emit(f"Fertig! {len(df)} Zeilen in {os.path.basename(self.out_file)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APZ-Tool V3 – Mit Spaltenauswahl")
        self.setGeometry(100, 100, 750, 650)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Dateiauswahl
        self.input_label = QLabel("PDFs und/oder Excel-Dateien auswählen:")
        layout.addWidget(self.input_label)

        self.input_button = QPushButton("Dateien wählen")
        self.input_button.clicked.connect(self.select_inputs)
        layout.addWidget(self.input_button)

        self.input_text = QLineEdit()
        layout.addWidget(self.input_text)

        # === NEU: Checkboxen für Spaltenauswahl ===
        self.column_group = QGroupBox("Spalten in der Ausgabe-Excel (Haken setzen)")
        self.column_layout = QVBoxLayout()

        self.checkboxes = {}
        for col in AVAILABLE_COLUMNS:
            cb = QCheckBox(col)
            cb.setChecked(True)  # Standard: alles ausgewählt
            self.checkboxes[col] = cb
            self.column_layout.addWidget(cb)

        self.column_group.setLayout(self.column_layout)

        # Scrollbar machen, falls viele Spalten
        scroll = QScrollArea()
        scroll.setWidget(self.column_group)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(280)
        layout.addWidget(scroll)

        # Ausgabedatei
        self.out_label = QLabel("Name der Ausgabedatei:")
        layout.addWidget(self.out_label)
        self.out_text = QLineEdit("APZ_Zusammenfassung_2025.xlsx")
        layout.addWidget(self.out_text)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_parsing)
        layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(180)
        layout.addWidget(self.log_text)

    def select_inputs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Dateien wählen", "", "Dateien (*.pdf *.xlsx)")
        if files:
            self.input_text.setText("; ".join(files))

    def start_parsing(self):
        raw_files = [p.strip() for p in self.input_text.text().split(";") if p.strip()]
        pdf_paths = [f for f in raw_files if f.lower().endswith('.pdf')]
        excel_paths = [f for f in raw_files if f.lower().endswith('.xlsx')]
        out_file = self.out_text.text()

        if not raw_files:
            self.log_text.append("Fehler: Keine Dateien ausgewählt.")
            return

        # Ausgewählte Spalten sammeln
        selected_columns = [col for col, cb in self.checkboxes.items() if cb.isChecked()]

        self.thread = ParseThread(pdf_paths, excel_paths, out_file, selected_columns)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.log.connect(self.log_text.append)
        self.thread.finished.connect(lambda: self.start_button.setEnabled(True))
        self.start_button.setEnabled(False)
        self.thread.start()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()