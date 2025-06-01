import sys
import sqlite3
import csv
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget, QInputDialog,
    QFileDialog, QMainWindow, QDockWidget, QStatusBar
)

class BookManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #181c24;
                color: #e0e6ed;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #2d3748;
                border-radius: 8px;
                background: #232b3b;
            }
            QTabBar::tab {
                background: #232b3b;
                color: #7fdbff;
                border: 1px solid #2d3748;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                min-width: 120px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f2027, stop:1 #2c5364);
                color: #fff;
                font-weight: bold;
            }
            QLabel {
                color: #7fdbff;
                font-weight: bold;
            }
            QLineEdit, QTableWidget, QInputDialog, QComboBox {
                background: #232b3b;
                color: #e0e6ed;
                border: 1px solid #7fdbff;
                border-radius: 5px;
                padding: 4px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #39ff14;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7fdbff, stop:1 #39ff14);
                color: #181c24;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: bold;
                margin: 4px 0;
                transition: background 0.2s;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #39ff14, stop:1 #7fdbff);
                color: #232b3b;
            }
            QTableWidget {
                gridline-color: #7fdbff;
                selection-background-color: #39ff14;
                selection-color: #181c24;
                alternate-background-color: #232b3b;
                min-height: 150px;
            }
            QHeaderView::section {
                background: #0f2027;
                color: #7fdbff;
                border: 1px solid #2d3748;
                font-weight: bold;
                padding: 6px;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
                background: transparent;
            }
            QTableWidget QScrollBar:vertical, QTableWidget QScrollBar:horizontal {
                width: 0px;
                height: 0px;
                background: transparent;
            }
            QMessageBox {
                background: #232b3b;
                color: #e0e6ed;
            }
        """)

        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(300, 100, 600, 400)

        self.conn = sqlite3.connect("database.db")
        self.create_table()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)


        self.tabs = QTabWidget()
        self.tab_data = QWidget()
        self.tab_export = QWidget()
        self.tabs.addTab(self.tab_data, "Data Buku")
        self.tabs.addTab(self.tab_export, "Ekspor")

        self.init_tab_data()
        self.init_tab_export()

        self.layout.addWidget(self.tabs)

        self.init_dock_widget()

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Buat QLabel untuk status dan ratakan ke tengah
        self.status_label = QLabel("Hendra Ahmad Yani | F1D022122")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Tambahkan label ke status bar dengan stretch (biar di tengah)
        self.status_bar.addPermanentWidget(self.status_label, 1)
        

        self.show_data()
        


    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS buku (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            judul TEXT,
                            pengarang TEXT,
                            tahun TEXT)''')
        self.conn.commit()

    def init_tab_data(self):
        layout = QVBoxLayout()

        # Form input
        self.input_judul = QLineEdit()
        self.input_pengarang = QLineEdit()
        self.input_tahun = QLineEdit()

        layout.addWidget(QLabel("Judul:"))
        layout.addWidget(self.input_judul)
        self.btn_paste_clipboard = QPushButton("Tempel dari Clipboard")
        self.btn_paste_clipboard.clicked.connect(self.paste_from_clipboard)
        layout.addWidget(self.btn_paste_clipboard)

        layout.addWidget(QLabel("Pengarang:"))
        layout.addWidget(self.input_pengarang)
        layout.addWidget(QLabel("Tahun:"))
        layout.addWidget(self.input_tahun)

        self.btn_simpan = QPushButton("Simpan")
        self.btn_simpan.clicked.connect(self.save_data)
        layout.addWidget(self.btn_simpan)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Cari judul...")
        self.input_search.textChanged.connect(self.search_data)
        layout.addWidget(self.input_search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.cellDoubleClicked.connect(self.edit_data)
        self.table.setMinimumHeight(150) 
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.table)

        self.btn_delete = QPushButton("Hapus Data")
        self.btn_delete.clicked.connect(self.delete_data)
        layout.addWidget(self.btn_delete)

        self.tab_data.setLayout(layout)

    def init_tab_export(self):
        layout = QVBoxLayout()
        self.btn_export = QPushButton("Export ke CSV")
        self.btn_export.clicked.connect(self.export_to_csv)
        layout.addWidget(self.btn_export)
        self.tab_export.setLayout(layout)

    def save_data(self):
        judul = self.input_judul.text()
        pengarang = self.input_pengarang.text()
        tahun = self.input_tahun.text()

        if not judul or not pengarang or not tahun:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi.")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO buku (judul, pengarang, tahun) VALUES (?, ?, ?)", (judul, pengarang, tahun))
        self.conn.commit()
        self.clear_inputs()
        self.show_data()

    def show_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM buku")
        data = cursor.fetchall()

        self.table.setRowCount(0)
        for row_data in data:
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, value in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(value)))

    def clear_inputs(self):
        self.input_judul.clear()
        self.input_pengarang.clear()
        self.input_tahun.clear()

    def search_data(self):
        keyword = self.input_search.text().lower()
        for row in range(self.table.rowCount()):
            match = keyword in self.table.item(row, 1).text().lower()
            self.table.setRowHidden(row, not match)

    def edit_data(self, row, column):
        id_data = self.table.item(row, 0).text()
        judul = self.table.item(row, 1).text()
        pengarang = self.table.item(row, 2).text()
        tahun = self.table.item(row, 3).text()

        new_judul, ok1 = QInputDialog.getText(self, "Edit Judul", "Judul:", text=judul)
        new_pengarang, ok2 = QInputDialog.getText(self, "Edit Pengarang", "Pengarang:", text=pengarang)
        new_tahun, ok3 = QInputDialog.getText(self, "Edit Tahun", "Tahun:", text=tahun)

        if ok1 and ok2 and ok3:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE buku SET judul=?, pengarang=?, tahun=? WHERE id=?", (new_judul, new_pengarang, new_tahun, id_data))
            self.conn.commit()
            self.show_data()

    def delete_data(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih data yang akan dihapus.")
            return

        id_data = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus data ini?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM buku WHERE id=?", (id_data,))
            self.conn.commit()
            self.show_data()

    def export_to_csv(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM buku")
        data = cursor.fetchall()

        # Dialog "Save As"
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan CSV",
            "data_buku.csv",
            "CSV Files (*.csv);;All Files (*)",
            options=options
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(data)
            QMessageBox.information(self, "Berhasil", f"Data berhasil diekspor ke {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal menulis file:\n{e}")

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.input_judul.setText(text)

    def init_dock_widget(self):
        dock = QDockWidget("Panel Samping", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        dock_content = QWidget()
        dock_layout = QVBoxLayout(dock_content)

        
        dock_layout.addWidget(QLabel("🔍 Cari Judul Buku:"))
        dock_layout.addWidget(self.input_search)

        
        self.label_statistik = QLabel()
        self.update_statistik()
        dock_layout.addWidget(QLabel("📊 Statistik Buku:"))
        dock_layout.addWidget(self.label_statistik)

        
        bantuan_btn = QPushButton("❓ Lihat Bantuan")
        bantuan_btn.clicked.connect(self.show_help_dialog)
        dock_layout.addWidget(bantuan_btn)

       
        link_btn = QPushButton("🌐 Buka Dokumentasi")
        link_btn.clicked.connect(self.open_documentation_link)
        dock_layout.addWidget(link_btn)

        dock_layout.addStretch()
        dock.setWidget(dock_content)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def update_statistik(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*), MIN(tahun), MAX(tahun) FROM buku")
        count, tahun_min, tahun_max = cursor.fetchone()

        if count == 0:
            text = "Belum ada data buku."
        else:
            text = f"Total Buku: {count}\nTahun Terlama: {tahun_min}\nTahun Terbaru: {tahun_max}"
        self.label_statistik.setText(text)
    
    def show_help_dialog(self):
        QMessageBox.information(
            self,
            "Bantuan Pengguna",
            "📚 Panduan Aplikasi:\n\n"
            "- Isi data buku di form Judul, Pengarang, dan Tahun.\n"
            "- Klik 'Simpan' untuk menyimpan data ke database.\n"
            "- Klik dua kali baris tabel untuk mengedit.\n"
            "- Gunakan kolom pencarian di panel kanan untuk mencari.\n"
            "- Gunakan tab 'Ekspor' untuk menyimpan data sebagai CSV.\n"
            "- Klik 'Hapus Data' untuk menghapus entri.\n"
            "- Statistik buku muncul otomatis di panel ini.\n"
        )

    def open_documentation_link(self):
        QDesktopServices.openUrl(QUrl("https://github.com/hndraa/pv25-week11"))




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec_())
