from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QFileDialog, QProgressBar, QTextEdit
from PySide6.QtCore import QThread, Signal
import pandas as pd
from apz_core import build_dataframe, export_to_excel
import os

class ParseThread(QThread):
    progress = Signal(int)
    log = Signal(str)

    def __init__(self, pdf_paths, excel_paths, out_file):
        super().__init__()
        self.pdf_paths = pdf_paths
        self.excel_paths = excel_paths
        self.out_file = out_file

    def run(self):
        self.log.emit("Starte Verarbeitung...")
        self.progress.emit(10)
        df = build_dataframe(self.pdf_paths)  # PDFs
        for excel in self.excel_paths:
            try:
                df_excel = pd.read_excel(excel)
                df = pd.concat([df, df_excel], ignore_index=True)
                self.log.emit(f"Excel {os.path.basename(excel)} angehängt ({len(df_excel)} Zeilen).")
            except Exception as e:
                self.log.emit(f"Excel-Fehler {os.path.basename(excel)}: {e}")
        self.progress.emit(50)
        export_to_excel(df, self.out_file)
        self.progress.emit(100)
        self.log.emit(f"Fertig! Excel '{os.path.basename(self.out_file)}' erstellt ({len(df)} Zeilen total).")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APZ-Tool – Standalone")
        self.setGeometry(100, 100, 700, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.input_label = QLabel("PDFs und/oder Excel auswählen (Mehrfach):")
        layout.addWidget(self.input_label)
        self.input_button = QPushButton("Dateien wählen (PDF/Excel)")
        self.input_button.clicked.connect(self.select_inputs)
        layout.addWidget(self.input_button)
        self.input_text = QLineEdit()
        layout.addWidget(self.input_text)

        self.out_label = QLabel("Ausgabedatei (Excel):")
        layout.addWidget(self.out_label)
        self.out_text = QLineEdit("APZ_Zusammenfassung_2025.xlsx")
        layout.addWidget(self.out_text)
        self.out_button = QPushButton("Ausgabe ändern")
        self.out_button.clicked.connect(self.select_out)
        layout.addWidget(self.out_button)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_parsing)
        layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

    def select_inputs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "PDFs/Excel wählen", "", "Dateien (*.pdf *.xlsx)")
        if files:
            self.input_text.setText("; ".join(files))

    def select_out(self):
        file, _ = QFileDialog.getSaveFileName(self, "Speichern als", "APZ_Zusammenfassung_2025.xlsx", "Excel (*.xlsx)")
        if file:
            self.out_text.setText(file)

    def start_parsing(self):
        raw_files = [p.strip() for p in self.input_text.text().split(";") if p.strip()]
        pdf_paths = [f for f in raw_files if f.lower().endswith('.pdf')]
        excel_paths = [f for f in raw_files if f.lower().endswith('.xlsx')]
        out_file = self.out_text.text()
        if not raw_files:
            self.log_text.append("Fehler: Keine Dateien ausgewählt.")
            return
        self.log_text.append(f"PDFs: {len(pdf_paths)}, Excel: {len(excel_paths)}")
        self.thread = ParseThread(pdf_paths, excel_paths, out_file)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.log.connect(self.log_text.append)
        self.thread.finished.connect(lambda: self.start_button.setEnabled(True))
        self.start_button.setEnabled(False)
        self.thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())