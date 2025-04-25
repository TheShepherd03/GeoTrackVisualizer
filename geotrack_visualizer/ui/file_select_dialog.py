from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog

class FileSelectDialog(QDialog):
    """Dialog for selecting TIFF and GeoJSON files.
    This dialog allows users to select the required input files for
    historical tracking visualization.
    """
    def __init__(self, default_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Files')
        self.resize(400, 200)
        self.tiff_path = ''
        self.geojson_path = ''
        self.default_dir = default_dir
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        file_layout = QHBoxLayout()
        self.tiff_label = QLabel('TIFF File:')
        self.tiff_button = QPushButton('Browse')
        self.tiff_button.clicked.connect(self.select_tiff)
        file_layout.addWidget(self.tiff_label)
        file_layout.addWidget(self.tiff_button)
        layout.addLayout(file_layout)
        geo_layout = QHBoxLayout()
        self.geojson_label = QLabel('GeoJSON File:')
        self.geojson_button = QPushButton('Browse')
        self.geojson_button.clicked.connect(self.select_geojson)
        geo_layout.addWidget(self.geojson_label)
        geo_layout.addWidget(self.geojson_button)
        layout.addLayout(geo_layout)
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def select_tiff(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Select TIFF File', self.default_dir, 'TIFF Files (*.tif *.tiff)')
        if file:
            self.tiff_path = file
            self.tiff_label.setText(f'TIFF File: {file}')

    def select_geojson(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Select GeoJSON File', self.default_dir, 'GeoJSON Files (*.geojson *.json)')
        if file:
            self.geojson_path = file
            self.geojson_label.setText(f'GeoJSON File: {file}')
