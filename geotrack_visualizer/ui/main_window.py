# MainWindow class will be placed here

import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTableWidget, 
    QTableWidgetItem, QHBoxLayout, QMessageBox, QDialog, QCheckBox, QComboBox, QSplitter,
    QHeaderView, QTextBrowser, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from .custom_toolbar import CustomNavigationToolbar
from ..utils.helpers import resource_path

# Project root icons directory
ICONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../icons'))

class MainWindow(QMainWindow):
    """Main application window for the GeoTrack Visualizer.
    
    This class handles the main UI setup, file loading, map rendering,
    and interactive features of the application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GeoTrack Visualizer')
        self.resize(1200, 800)
        
        # Set application icon
        app_icon = QIcon(os.path.join(ICONS_DIR, 'app_icon.png'))
        self.setWindowIcon(app_icon)
        
        self.default_dir = self.load_or_select_default_directory()
        self.dark_mode = False
        self.init_ui()

    def load_or_select_default_directory(self):
        """Load the default directory from config or prompt user to select one.
        
        Returns:
            str: Path to the default directory for file operations
        """
        # Try to load from config file
        from ..utils.helpers import CONFIG_PATH
        from ..utils.helpers import SETTINGS_DIR
        import os
        import json
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                    return config.get('default_directory', '')
            except (json.JSONDecodeError, IOError):
                pass
        return self.select_and_save_directory()

    def select_and_save_directory(self):
        """Prompt user to select a default directory and save it to config."""
        from ..utils.helpers import CONFIG_PATH
        from ..utils.helpers import SETTINGS_DIR
        import os
        import json
        directory = QFileDialog.getExistingDirectory(self, "Select Default Directory")
        if directory:
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump({'default_directory': directory}, f)
            return directory
        return ''

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(QVBoxLayout())
        
        # Top toolbar with app controls in a more compact layout
        top_controls = QHBoxLayout()
        top_controls.setContentsMargins(5, 5, 5, 5)
        top_controls.setSpacing(10)
        
        # Mode selection buttons directly in the layout
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(5)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create mode label with adaptive styling
        self.mode_label = QLabel("Mode:")
        self.mode_label.setObjectName("sectionLabel")
        self.mode_label.setStyleSheet("font-weight: bold;")
        mode_layout.addWidget(self.mode_label)
        
        # Live tracking button (disabled)
        self.live_btn = QPushButton('Live Tracking')
        self.live_btn.setEnabled(False)
        self.live_btn.setToolTip('Live tracking functionality is currently disabled in this version')
        self.live_btn.setObjectName("liveButton")
        self.live_btn.setStyleSheet("padding: 4px 8px; font-weight: bold;")
        
        # Historical tracking button (active)
        self.hist_btn = QPushButton('Historical Tracking')
        self.hist_btn.setToolTip('Load historical tracking data from TIFF and GeoJSON files')
        self.hist_btn.clicked.connect(self.start_historical_tracking)
        self.hist_btn.setObjectName("histButton")
        self.hist_btn.setStyleSheet("padding: 4px 8px; font-weight: bold; background-color: #4CAF50;")
        
        mode_layout.addWidget(self.live_btn)
        mode_layout.addWidget(self.hist_btn)
        
        # Settings controls directly in the layout
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(5)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create settings label with adaptive styling
        self.settings_label = QLabel("Settings:")
        self.settings_label.setObjectName("sectionLabel")
        self.settings_label.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(self.settings_label)
        
        # Dark mode toggle
        self.dark_mode_cb = QCheckBox("Dark Mode")
        self.dark_mode_cb.setObjectName("darkModeCheckbox")
        self.dark_mode_cb.stateChanged.connect(self.toggle_dark_mode)
        settings_layout.addWidget(self.dark_mode_cb)
        
        # Map style selector
        self.map_style_label = QLabel("Map Style:")
        self.map_style_label.setObjectName("mapStyleLabel")
        settings_layout.addWidget(self.map_style_label)
        
        self.map_style = QComboBox()
        self.map_style.addItems(["Default", "Terrain", "Satellite"])
        self.map_style.currentIndexChanged.connect(self.update_map_style)
        settings_layout.addWidget(self.map_style)
        
        # Add layouts to top controls
        top_controls.addLayout(mode_layout, 2)
        top_controls.addStretch(1)
        top_controls.addLayout(settings_layout, 2)
        
        # Apply initial colors based on mode
        self.update_ui_colors(self.dark_mode)
        
        self.central_widget.layout().addLayout(top_controls)

    def update_ui_colors(self, dark_mode):
        """Update UI element colors based on dark/light mode for optimal readability."""
        if dark_mode:
            label_color = "color: white; font-weight: bold;"
            button_text_color = "color: white;"
            disabled_button_color = "color: #aaaaaa; background-color: #555555;"
            active_button_color = "color: white; background-color: #4CAF50;"
            checkbox_style = "color: white;"
            combobox_style = "background-color: #444444; color: white; selection-background-color: #666666;"
        else:
            label_color = "color: black; font-weight: bold;"
            button_text_color = "color: black;"
            disabled_button_color = "color: #777777; background-color: #e0e0e0;"
            active_button_color = "color: black; background-color: #4CAF50;"
            checkbox_style = "color: black;"
            combobox_style = "background-color: white; color: black; selection-background-color: #e0e0e0;"
        for label in self.findChildren(QLabel, "sectionLabel"):
            label.setStyleSheet(label_color)
        self.map_style_label.setStyleSheet(label_color)
        self.live_btn.setStyleSheet(f"padding: 4px 8px; font-weight: bold; {disabled_button_color}")
        self.hist_btn.setStyleSheet(f"padding: 4px 8px; font-weight: bold; {active_button_color}")
        self.dark_mode_cb.setStyleSheet(checkbox_style)
        self.map_style.setStyleSheet(combobox_style)

    def toggle_dark_mode(self, state):
        self.dark_mode = state == Qt.Checked
        app = QApplication.instance()
        if self.dark_mode:
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(dark_palette)
            app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
        else:
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("")
        self.update_ui_colors(self.dark_mode)

    def update_map_style(self, index):
        style = self.map_style.currentText()
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'figure') and hasattr(widget, 'draw'):
                fig = widget.figure
                if fig and len(fig.axes) > 0:
                    ax = fig.axes[0]
                    for img in ax.get_images():
                        if len(img.get_array().shape) == 2:  
                            if style == "Terrain":
                                img.set_cmap('terrain')
                                img.set_alpha(0.8)
                            elif style == "Satellite":
                                img.set_cmap('gist_earth')
                                img.set_alpha(1.0)
                            else:
                                img.set_cmap('gray')
                                img.set_alpha(0.5)
                    widget.draw()

    def start_historical_tracking(self):
        from .file_select_dialog import FileSelectDialog
        dialog = FileSelectDialog(self.default_dir, self)
        if dialog.exec_():
            self.show_map_and_table(dialog.tiff_path, dialog.geojson_path)

    def show_map_and_table(self, tiff_path, geojson_path):
        import geopandas as gpd
        import rasterio
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from PyQt5.QtWidgets import QSplitter, QMessageBox, QHBoxLayout, QPushButton, QProgressDialog
        progress = QProgressDialog('Loading map and data...', None, 0, 0, self)
        progress.setWindowTitle('GeoTrack Visualizer')
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()
        self.setWindowTitle('GeoTrack Visualizer')
        for i in reversed(range(self.central_widget.layout().count())):
            widget = self.central_widget.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        splitter = QSplitter(Qt.Horizontal)
        self.central_widget.layout().addWidget(splitter)
        fig, ax = plt.subplots(figsize=(6, 6))
        try:
            with rasterio.open(tiff_path) as src:
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                tiff_crs = src.crs
                if src.count == 3:
                    r = src.read(1)
                    g = src.read(2)
                    b = src.read(3)
                    rgb = np.dstack((r, g, b))
                    if rgb.max() > 255:
                        rgb = rgb / rgb.max()
                    ax.imshow(rgb, extent=extent, origin='upper', aspect='auto')
                else:
                    raster = src.read(1)
                    ax.imshow(raster, extent=extent, cmap='gray', alpha=0.5, origin='upper', aspect='auto')
        except Exception as e:
            ax.text(0.5, 0.5, f'Failed to load TIFF:\n{e}', ha='center', va='center')
            tiff_crs = None
        try:
            gdf = gpd.read_file(geojson_path)
            if gdf.crs is None:
                gdf = gdf.set_crs('EPSG:4326', allow_override=True)
            need_reproject = tiff_crs is not None and gdf.crs != tiff_crs
            orig_points = np.array([(geom.x, geom.y) for geom in gdf.geometry])
            gdf_orig = gdf.copy()
            if need_reproject:
                gdf = gdf.to_crs(tiff_crs)
                points = np.array([(geom.x, geom.y) for geom in gdf.geometry])
            else:
                points = orig_points
            scatter = ax.scatter(points[:, 0], points[:, 1], color='red', s=40, alpha=0.7, picker=True)
            if 'TN Bearing' in gdf.columns:
                bearings = gdf['TN Bearing'].values
                angles = np.deg2rad(bearings)
                arrow_length = 0.0005 * max(ax.get_xlim()[1] - ax.get_xlim()[0], ax.get_ylim()[1] - ax.get_ylim()[0])
                dx = arrow_length * np.sin(angles)
                dy = arrow_length * np.cos(angles)
                ax.quiver(points[:, 0], points[:, 1], dx, dy, angles='xy', scale_units='xy', scale=1, color='blue', width=0.003, headwidth=3)
        except Exception as e:
            ax.text(0.5, 0.3, f'Failed to load GeoJSON:\n{e}', ha='center', va='center')
            gdf = None
            scatter = None
        import matplotlib.ticker as mticker
        ax.set_title('Map View')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        if tiff_crs is not None and tiff_crs.to_epsg() == 4326:
            ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.6f'))
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.6f'))
        else:
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:,.0f}"))
        if 'extent' in locals():
            ax.set_xlim(extent[0], extent[1])
            ax.set_ylim(extent[2], extent[3])
        canvas = FigureCanvas(fig)
        splitter.addWidget(canvas)
        def zoom(factor):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            x_c = (cur_xlim[0] + cur_xlim[1]) / 2
            y_c = (cur_ylim[0] + cur_ylim[1]) / 2
            x_range = (cur_xlim[1] - cur_xlim[0]) * factor / 2
            y_range = (cur_ylim[1] - cur_ylim[0]) * factor / 2
            ax.set_xlim([x_c - x_range, x_c + x_range])
            ax.set_ylim([y_c - y_range, y_c + y_range])
            canvas.draw()
        from PyQt5.QtWidgets import QAction
        from PyQt5.QtGui import QIcon
        from PyQt5.QtCore import QSize
        from PyQt5.QtWidgets import QStyle
        toolbar = CustomNavigationToolbar(canvas, self)
        style = QApplication.style()
        clear_icon = style.standardIcon(QStyle.SP_DialogResetButton)
        zoom_in_icon = QIcon(os.path.join(ICONS_DIR, 'plus.svg'))
        zoom_out_icon = QIcon(os.path.join(ICONS_DIR, 'minus.svg'))
        zoom_in_action = QAction(zoom_in_icon, '', self)
        zoom_in_action.setToolTip('Zoom In: Make the map view larger')
        zoom_out_action = QAction(zoom_out_icon, '', self)
        zoom_out_action.setToolTip('Zoom Out: Make the map view smaller')
        clear_action = QAction(clear_icon, '', self)
        clear_action.setToolTip('Clear: Remove current map and table, and upload new files')
        for action in [zoom_in_action, zoom_out_action, clear_action]:
            toolbar.removeAction(action)
        default_actions = toolbar.actions()
        home_action = None
        pan_action = None
        pan_cursor_path = os.path.join(ICONS_DIR, 'pan_cursor.png')
        if os.path.isfile(pan_cursor_path):
            pan_icon = QIcon(pan_cursor_path)
        else:
            pan_icon = QIcon(os.path.join(ICONS_DIR, 'pan.svg'))
        reset_icon = QIcon(os.path.join(ICONS_DIR, 'reset.svg'))
        for act in default_actions:
            tip = act.toolTip().lower()
            if 'home' in tip or 'reset original view' in tip:
                home_action = act
                act.setIcon(reset_icon)
                act.setToolTip('Reset View: Return the map to its original extent and zoom level. Use this if you want to quickly see the entire map as it was loaded.')
            elif 'pan' in tip:
                pan_action = act
                act.setIcon(pan_icon)
                act.setToolTip('Pan Map: Click and drag the map to move to different areas.\nLeft-click: Move the map.\nRight-click: Move the map and zoom at the same time. Useful for exploring regions outside the current view.')
            elif 'zoom' in tip and 'rect' in tip:
                act.setToolTip('Zoom to Rectangle: Drag to select a region to zoom into for a closer view.')
            elif 'save' in tip:
                act.setToolTip('Save Map as Image: Save the current map view as a PNG file.')
        insert_index = 0
        if home_action:
            toolbar.removeAction(home_action)
            toolbar.insertAction(toolbar.actions()[insert_index], home_action)
            insert_index += 1
        if pan_action:
            toolbar.removeAction(pan_action)
            toolbar.insertAction(toolbar.actions()[insert_index], pan_action)
            insert_index += 1
        toolbar.insertAction(toolbar.actions()[insert_index], zoom_in_action)
        zoom_in_action.setToolTip('Zoom In: Make the map view larger. Click to zoom in and see more detail in the current region.')
        insert_index += 1
        toolbar.insertAction(toolbar.actions()[insert_index], zoom_out_action)
        zoom_out_action.setToolTip('Zoom Out: Make the map view smaller. Click to zoom out and see a larger area of the map.')
        insert_index += 1
        reset_zoom_action = None
        for act in toolbar.actions():
            if 'zoom' in act.toolTip().lower() and 'rect' in act.toolTip().lower():
                reset_zoom_action = act
                break
        if reset_zoom_action:
            toolbar.removeAction(reset_zoom_action)
            toolbar.insertAction(toolbar.actions()[insert_index], reset_zoom_action)
            reset_zoom_action.setToolTip('Reset Zoom: Fit the map to the window. Use this to automatically adjust the map to fit all data layers in view.')
            insert_index += 1
        toolbar.insertAction(toolbar.actions()[insert_index], clear_action)
        clear_action.setToolTip('Clear: Remove all map overlays and uploaded data. Use this to reset the workspace and upload new files.')
        def zoom(factor):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            x_c = (cur_xlim[0] + cur_xlim[1]) / 2
            y_c = (cur_ylim[0] + cur_ylim[1]) / 2
            x_range = (cur_xlim[1] - cur_xlim[0]) * factor / 2
            y_range = (cur_ylim[1] - cur_ylim[0]) * factor / 2
            ax.set_xlim([x_c - x_range, x_c + x_range])
            ax.set_ylim([y_c - y_range, y_c + y_range])
            canvas.draw()
        zoom_in_action.triggered.connect(lambda: zoom(0.5))
        zoom_out_action.triggered.connect(lambda: zoom(2.0))
        clear_action.triggered.connect(self.clear_all)
        self.central_widget.layout().insertWidget(1, toolbar)
        toolbar.setEnabled(True)
        toolbar.setVisible(True)
        self.activateWindow()
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setStyleSheet(
            "QTableWidget {gridline-color: #d0d0d0; border: 1px solid #c0c0c0;}"
            "QHeaderView::section {background-color: #f0f0f0; padding: 4px; border: 1px solid #c0c0c0;}"
            "QTableWidget::item:selected {background-color: #308cc6; color: white;}"
        )
        if gdf is not None:
            import json
            with open(geojson_path, 'r') as f:
                data = json.load(f)
            orig_lons = []
            orig_lats = []
            for feature in data['features']:
                coords = feature['geometry']['coordinates']
                orig_lons.append(coords[0])
                orig_lats.append(coords[1])
            props = gdf_orig.drop(columns='geometry').copy()
            props['Longitude'] = orig_lons
            props['Latitude'] = orig_lats
            if 'need_reproject' in locals() and need_reproject:
                props['Mapped Longitude'] = gdf.geometry.x
                props['Mapped Latitude'] = gdf.geometry.y
                columns = list(props.columns)
            else:
                columns = list(props.columns)
                columns = [c for c in columns if c not in ['Mapped Longitude', 'Mapped Latitude']]
            table.setRowCount(len(props))
            table.setColumnCount(len(columns))
            table.setHorizontalHeaderLabels(columns)
            header_font = QFont()
            header_font.setBold(True)
            table.horizontalHeader().setFont(header_font)
            for i, row in props.iterrows():
                for j, col in enumerate(columns):
                    if col in ['Longitude', 'Latitude', 'Mapped Longitude', 'Mapped Latitude']:
                        item = QTableWidgetItem(f"{row[col]:.15f}")
                    else:
                        item = QTableWidgetItem(str(row[col]))
                    if isinstance(row[col], (int, float)):
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    table.setItem(i, j, item)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.horizontalHeader().setStretchLastSection(True)
        splitter.addWidget(table)
        splitter.setSizes([600, 400])
        progress.close()
        if scatter is not None and gdf is not None:
            from matplotlib.offsetbox import AnnotationBbox, TextArea
            annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox={"boxstyle":"round,pad=0.5", "fc":"yellow", "alpha":0.8},
                            arrowprops={"arrowstyle":"->"}, fontsize=9)
            annot.set_visible(False)
            def on_pick(event):
                ind = event.ind[0]
                attr = props.iloc[ind].to_dict()
                msg = '\n'.join(f"{k}: {v}" for k, v in attr.items())
                scatter.set_facecolors(['red' if i != ind else 'yellow' for i in range(len(props))])
                canvas.draw()
                table.selectRow(ind)
                table.scrollToItem(table.item(ind, 0))
                QMessageBox.information(self, 'Point Attributes', msg)
            def hover(event):
                if event.inaxes == ax:
                    cont, ind = scatter.contains(event)
                    if cont:
                        ind = ind['ind'][0]
                        attr = props.iloc[ind].to_dict()
                        tooltip_attrs = ['TN Bearing', 'Signal Strength', 'Date & Time']
                        tooltip_text = '\n'.join(f"{k}: {attr.get(k, 'N/A')}" 
                                               for k in tooltip_attrs if k in attr)
                        annot.xy = (points[ind][0], points[ind][1])
                        annot.set_text(tooltip_text)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                    else:
                        if annot.get_visible():
                            annot.set_visible(False)
                            fig.canvas.draw_idle()
            fig.canvas.mpl_connect('pick_event', on_pick)
            fig.canvas.mpl_connect('motion_notify_event', hover)

    def clear_all(self):
        for i in reversed(range(self.central_widget.layout().count())):
            widget = self.central_widget.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.start_historical_tracking()
