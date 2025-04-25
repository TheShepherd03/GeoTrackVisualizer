#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GeoTrack Visualizer - A desktop application for visualizing geospatial tracking data.

This application allows users to load and visualize TIFF and GeoJSON data,
with features for interactive exploration, map styling, and data analysis.
"""

# Standard library imports
import sys
import os
import json

# PyQt5 imports for GUI
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTableWidget, 
    QTableWidgetItem, QHBoxLayout, QMessageBox, QDialog, QCheckBox, QComboBox, QSplitter,
    QHeaderView, QTextBrowser, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor, QFont, QIcon

# Matplotlib navigation toolbar
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

class CustomNavigationToolbar(NavigationToolbar2QT):
    """
    Custom navigation toolbar that ensures tooltips are properly displayed.
    
    This class fixes an issue in the standard matplotlib toolbar where tooltips
    might not appear when hovering over toolbar buttons.
    """
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        self.apply_tooltips_to_widgets()
    
    def apply_tooltips_to_widgets(self):
        """Apply tooltips from QActions to their corresponding button widgets."""
        for action in self.actions():
            if action.toolTip():
                widget = self.widgetForAction(action)
                if widget:
                    widget.setToolTip(action.toolTip())


# Helper function to handle paths in both script and executable modes
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    
    return os.path.join(base_path, relative_path)

# Configuration paths
CONFIG_PATH = resource_path(os.path.join('settings', 'config.json'))
SETTINGS_DIR = resource_path('settings')

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
        app_icon = QIcon(resource_path('icons/app_icon.png'))
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
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                    return config.get('default_directory', '')
            except (json.JSONDecodeError, IOError):
                # If config file is corrupted or can't be read, fall back to selection
                pass
        
        # If no config exists or there was an error, prompt user to select a directory
        return self.select_and_save_directory()
    
    def select_and_save_directory(self):
        """Prompt user to select a default directory and save it to config.
        
        Returns:
            str: Selected directory path or empty string if canceled
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Default Directory")
        if directory:
            # Create settings directory if it doesn't exist
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            # Save to config file
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
        self.mode_label.setObjectName("sectionLabel")  # For style targeting
        self.mode_label.setStyleSheet("font-weight: bold;")
        mode_layout.addWidget(self.mode_label)
        
        # Live tracking button (disabled)
        self.live_btn = QPushButton('Live Tracking')
        self.live_btn.setEnabled(False)
        self.live_btn.setToolTip('Live tracking functionality is currently disabled in this version')
        self.live_btn.setObjectName("liveButton")  # For style targeting
        self.live_btn.setStyleSheet("padding: 4px 8px; font-weight: bold;")
        
        # Historical tracking button (active)
        self.hist_btn = QPushButton('Historical Tracking')
        self.hist_btn.setToolTip('Load historical tracking data from TIFF and GeoJSON files')
        self.hist_btn.clicked.connect(self.start_historical_tracking)
        self.hist_btn.setObjectName("histButton")  # For style targeting
        self.hist_btn.setStyleSheet("padding: 4px 8px; font-weight: bold; background-color: #4CAF50;")
        
        mode_layout.addWidget(self.live_btn)
        mode_layout.addWidget(self.hist_btn)
        
        # Settings controls directly in the layout
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(5)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create settings label with adaptive styling
        self.settings_label = QLabel("Settings:")
        self.settings_label.setObjectName("sectionLabel")  # For style targeting
        self.settings_label.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(self.settings_label)
        
        # Dark mode toggle
        self.dark_mode_cb = QCheckBox("Dark Mode")
        self.dark_mode_cb.setObjectName("darkModeCheckbox")  # For style targeting
        self.dark_mode_cb.stateChanged.connect(self.toggle_dark_mode)
        settings_layout.addWidget(self.dark_mode_cb)
        
        # Map style selector
        self.map_style_label = QLabel("Map Style:")
        self.map_style_label.setObjectName("mapStyleLabel")  # For style targeting
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
        """Update UI element colors based on dark/light mode for optimal readability.
        
        This method ensures all labels, buttons, and other UI elements have appropriate
        colors that are readable in both dark and light modes.
        
        Args:
            dark_mode (bool): Whether dark mode is enabled
        """
        if dark_mode:
            # Dark mode colors
            label_color = "color: white; font-weight: bold;"
            button_text_color = "color: white;"
            disabled_button_color = "color: #aaaaaa; background-color: #555555;"
            active_button_color = "color: white; background-color: #4CAF50;"
            checkbox_style = "color: white;"
            combobox_style = "background-color: #444444; color: white; selection-background-color: #666666;"
        else:
            # Light mode colors
            label_color = "color: black; font-weight: bold;"
            button_text_color = "color: black;"
            disabled_button_color = "color: #777777; background-color: #e0e0e0;"
            active_button_color = "color: black; background-color: #4CAF50;"
            checkbox_style = "color: black;"
            combobox_style = "background-color: white; color: black; selection-background-color: #e0e0e0;"
        
        # Apply styles to section labels
        for label in self.findChildren(QLabel, "sectionLabel"):
            label.setStyleSheet(label_color)
        
        # Apply styles to specific labels
        self.map_style_label.setStyleSheet(label_color)
        
        # Apply styles to buttons
        self.live_btn.setStyleSheet(f"padding: 4px 8px; font-weight: bold; {disabled_button_color}")
        self.hist_btn.setStyleSheet(f"padding: 4px 8px; font-weight: bold; {active_button_color}")
        
        # Apply style to checkbox
        self.dark_mode_cb.setStyleSheet(checkbox_style)
        
        # Apply style to combobox
        self.map_style.setStyleSheet(combobox_style)
    
    def toggle_dark_mode(self, state):
        """Toggle between dark and light application themes.
        
        Args:
            state: Qt checkbox state (Qt.Checked or Qt.Unchecked)
        """
        self.dark_mode = state == Qt.Checked
        app = QApplication.instance()
        
        if self.dark_mode:
            # Create and apply dark color palette
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
            # Reset to default light palette
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("")
        
        # Update all UI element colors for the current mode
        self.update_ui_colors(self.dark_mode)
    
    def update_map_style(self, index):
        """Update the map visualization style based on the selected option.
        
        This method changes the colormap and transparency of single-band images
        in the matplotlib figure to achieve different visual styles.
        
        Args:
            index (int): Index of the selected style in the dropdown (not used directly)
        """
        # Get the currently selected style text
        style = self.map_style.currentText()
        
        # Find any matplotlib canvas in the application
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'figure') and hasattr(widget, 'draw'):
                # Found a matplotlib canvas
                fig = widget.figure
                if fig and len(fig.axes) > 0:
                    ax = fig.axes[0]
                    
                    # Apply different colormaps based on the selected style
                    for img in ax.get_images():
                        # Only modify single-band (grayscale) images
                        if len(img.get_array().shape) == 2:  
                            if style == "Terrain":
                                # Terrain-like appearance with green-brown colors
                                img.set_cmap('terrain')
                                img.set_alpha(0.8)
                            elif style == "Satellite":
                                # Earth-like appearance for satellite view
                                img.set_cmap('gist_earth')
                                img.set_alpha(1.0)
                            else:  # Default
                                # Standard grayscale with transparency
                                img.set_cmap('gray')
                                img.set_alpha(0.5)
                    
                    # Redraw the canvas to show changes
                    widget.draw()
        
    def start_historical_tracking(self):
        """Open file selection dialog and load historical tracking data."""
        dialog = FileSelectDialog(self.default_dir, self)
        if dialog.exec_():
            # If user selected files, display them on the map and in the table
            self.show_map_and_table(dialog.tiff_path, dialog.geojson_path)

    def show_map_and_table(self, tiff_path, geojson_path):
        import geopandas as gpd
        import rasterio
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from PyQt5.QtWidgets import QSplitter, QMessageBox, QHBoxLayout, QPushButton, QProgressDialog
        import numpy as np
        # Show loading dialog
        progress = QProgressDialog('Loading map and data...', None, 0, 0, self)
        progress.setWindowTitle('GeoTrack Visualizer')
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()
        self.setWindowTitle('GeoTrack Visualizer')

        # Remove old layout
        for i in reversed(range(self.central_widget.layout().count())):
            widget = self.central_widget.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        splitter = QSplitter(Qt.Horizontal)
        self.central_widget.layout().addWidget(splitter)

        # Map rendering
        fig, ax = plt.subplots(figsize=(6, 6))
        try:
            with rasterio.open(tiff_path) as src:
                extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                tiff_crs = src.crs
                if src.count == 3:
                    # RGB image
                    r = src.read(1)
                    g = src.read(2)
                    b = src.read(3)
                    import numpy as np
                    rgb = np.dstack((r, g, b))
                    # Normalize if needed
                    if rgb.max() > 255:
                        rgb = rgb / rgb.max()
                    ax.imshow(rgb, extent=extent, origin='upper', aspect='auto')
                else:
                    # Grayscale fallback
                    raster = src.read(1)
                    ax.imshow(raster, extent=extent, cmap='gray', alpha=0.5, origin='upper', aspect='auto')
        except Exception as e:
            ax.text(0.5, 0.5, f'Failed to load TIFF:\n{e}', ha='center', va='center')
            tiff_crs = None

        # Plot GeoJSON, reproject if needed
        try:
            gdf = gpd.read_file(geojson_path)
            # Always set CRS if missing (GeoJSON is usually EPSG:4326)
            if gdf.crs is None:
                gdf = gdf.set_crs('EPSG:4326', allow_override=True)
            need_reproject = tiff_crs is not None and gdf.crs != tiff_crs
            # Save original coordinates
            orig_points = np.array([(geom.x, geom.y) for geom in gdf.geometry])
            gdf_orig = gdf.copy()
            if need_reproject:
                gdf = gdf.to_crs(tiff_crs)
                points = np.array([(geom.x, geom.y) for geom in gdf.geometry])
            else:
                points = orig_points
            scatter = ax.scatter(points[:, 0], points[:, 1], color='red', s=40, alpha=0.7, picker=True)
            # Draw directional arrows for each point using 'TN Bearing' attribute
            if 'TN Bearing' in gdf.columns:
                import numpy as np
                bearings = gdf['TN Bearing'].values
                # Convert bearings (degrees) to radians for quiver
                angles = np.deg2rad(bearings)
                # Arrow length (fixed for display)
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
        # Format axes nicely
        if tiff_crs is not None and tiff_crs.to_epsg() == 4326:
            # WGS84: decimal degrees
            ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.6f'))
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.6f'))
        else:
            # Projected: thousands separator, no decimals
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:,.0f}"))
        # Set axis limits to TIFF extent for tight map
        if 'extent' in locals():
            ax.set_xlim(extent[0], extent[1])
            ax.set_ylim(extent[2], extent[3])
        canvas = FigureCanvas(fig)
        splitter.addWidget(canvas)

        # Zoom in/out functionality
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

        # Add zoom/pan toolbar
        from PyQt5.QtWidgets import QAction
        from PyQt5.QtGui import QIcon
        from PyQt5.QtCore import QSize
        from PyQt5.QtWidgets import QStyle
        toolbar = CustomNavigationToolbar(canvas, self)


        # Create actions with icons
        style = QApplication.style()
        from PyQt5.QtGui import QIcon
        clear_icon = style.standardIcon(QStyle.SP_DialogResetButton)
        zoom_in_icon = QIcon(resource_path('icons/plus.svg'))
        zoom_out_icon = QIcon(resource_path('icons/minus.svg'))
        zoom_in_action = QAction(zoom_in_icon, '', self)
        zoom_in_action.setToolTip('Zoom In: Make the map view larger')
        zoom_out_action = QAction(zoom_out_icon, '', self)
        zoom_out_action.setToolTip('Zoom Out: Make the map view smaller')
        clear_action = QAction(clear_icon, '', self)
        clear_action.setToolTip('Clear: Remove current map and table, and upload new files')
        # Remove all custom actions first (if toolbar is reused)
        for action in [zoom_in_action, zoom_out_action, clear_action]:
            toolbar.removeAction(action)
        # Find default actions
        default_actions = toolbar.actions()
        # Attempt to find home/pan actions
        home_action = None
        pan_action = None
        # Assign new icons and tooltips for pan and reset (home) actions
        pan_cursor_path = resource_path('icons/pan_cursor.png')
        if os.path.isfile(pan_cursor_path):
            pan_icon = QIcon(pan_cursor_path)
        else:
            pan_icon = QIcon(resource_path('icons/pan.svg'))
        reset_icon = QIcon(resource_path('icons/reset.svg'))
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
        # Insert in logical order: Home, Pan, Zoom In, Zoom Out, Reset Zoom, Clear, then others
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
        # Try to find the default zoom-to-rect and insert after zoom out
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
        
        # Ensure the window is active
        self.activateWindow()

        # Attribute table: show only original coordinates if no reprojection, else show both
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
                # Add mapped coordinates
                props['Mapped Longitude'] = gdf.geometry.x
                props['Mapped Latitude'] = gdf.geometry.y
                columns = list(props.columns)
            else:
                columns = list(props.columns)
                # Only show original
                columns = [c for c in columns if c not in ['Mapped Longitude', 'Mapped Latitude']]
            table.setRowCount(len(props))
            table.setColumnCount(len(columns))
            table.setHorizontalHeaderLabels(columns)
            
            # Apply better formatting to the table
            header_font = QFont()
            header_font.setBold(True)
            table.horizontalHeader().setFont(header_font)
            
            for i, row in props.iterrows():
                for j, col in enumerate(columns):
                    # Show full precision for coordinates
                    if col in ['Longitude', 'Latitude', 'Mapped Longitude', 'Mapped Latitude']:
                        item = QTableWidgetItem(f"{row[col]:.15f}")
                    else:
                        item = QTableWidgetItem(str(row[col]))
                    
                    # Right-align numeric columns
                    if isinstance(row[col], (int, float)):
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    table.setItem(i, j, item)
            
            # Auto-resize columns and rows for better appearance
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.horizontalHeader().setStretchLastSection(True)
        splitter.addWidget(table)
        splitter.setSizes([600, 400])
        # Hide loading dialog
        progress.close()

        # Interactive selection: show popup on point click and highlight table row
        if scatter is not None and gdf is not None:
            # Create a tooltip for hover information
            from matplotlib.offsetbox import AnnotationBbox, TextArea
            annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox={"boxstyle":"round,pad=0.5", "fc":"yellow", "alpha":0.8},
                            arrowprops={"arrowstyle":"->"}, fontsize=9)
            annot.set_visible(False)
            
            def on_pick(event):
                ind = event.ind[0]
                attr = props.iloc[ind].to_dict()
                msg = '\n'.join(f"{k}: {v}" for k, v in attr.items())
                # Highlight selected point
                scatter.set_facecolors(['red' if i != ind else 'yellow' for i in range(len(props))])
                canvas.draw()
                # Highlight row in table
                table.selectRow(ind)
                table.scrollToItem(table.item(ind, 0))
                # Show popup
                QMessageBox.information(self, 'Point Attributes', msg)
            
            def hover(event):
                if event.inaxes == ax:
                    cont, ind = scatter.contains(event)
                    if cont:
                        ind = ind['ind'][0]
                        # Get key attributes for tooltip
                        attr = props.iloc[ind].to_dict()
                        # Show only key attributes in tooltip
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
        # Remove map, table, toolbar
        for i in reversed(range(self.central_widget.layout().count())):
            widget = self.central_widget.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Prompt file selection again
        self.start_historical_tracking()

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
        layout = QVBoxLayout()
        self.setLayout(layout)

        # TIFF file selection row
        tiff_layout = QHBoxLayout()
        tiff_label = QLabel('TIFF File:')
        self.tiff_edit = QLabel('No file selected')
        tiff_btn = QPushButton('Browse...')
        tiff_btn.clicked.connect(self.select_tiff)
        tiff_layout.addWidget(tiff_label)
        tiff_layout.addWidget(self.tiff_edit, 1)  # 1 = stretch factor
        tiff_layout.addWidget(tiff_btn)
        layout.addLayout(tiff_layout)

        # GeoJSON file selection row
        geojson_layout = QHBoxLayout()
        geojson_label = QLabel('GeoJSON File:')
        self.geojson_edit = QLabel('No file selected')
        geojson_btn = QPushButton('Browse...')
        geojson_btn.clicked.connect(self.select_geojson)
        geojson_layout.addWidget(geojson_label)
        geojson_layout.addWidget(self.geojson_edit, 1)  # 1 = stretch factor
        geojson_layout.addWidget(geojson_btn)
        layout.addLayout(geojson_layout)

        # Dialog buttons (OK/Cancel)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton('OK')
        cancel_btn = QPushButton('Cancel')
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def select_tiff(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select .tiff File', self.default_dir, 'TIFF files (*.tif *.tiff)')
        if path:
            self.tiff_path = path
            self.tiff_edit.setText(f"Selected: {os.path.basename(path)}")

    def select_geojson(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select .geojson File', self.default_dir, 'GeoJSON files (*.geojson)')
        if path:
            self.geojson_path = path
            self.geojson_edit.setText(f"Selected: {os.path.basename(path)}")

class WelcomeScreen(QDialog):
    """
    Welcome screen that displays an introduction to the application's features
    using markdown formatting for a professional appearance.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to GeoTrack Visualizer")
        self.setWindowIcon(QIcon(resource_path('icons/app_icon.png')))
        self.resize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create markdown browser with custom styling
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        
        # Set custom CSS for markdown rendering
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: #f8f9fa;
                padding: 20px;
                font-size: 14px;
            }
        """)
        
        # Load HTML content directly
        try:
            # Set the search paths for resources (images)
            self.text_browser.setSearchPaths([resource_path('')])
            
            # Load HTML file directly
            html_path = resource_path('welcome.html')
            with open(html_path, 'r') as f:
                html_content = f.read()
                self.text_browser.setHtml(html_content)
        except Exception as e:
            self.text_browser.setPlainText(f"Error loading welcome content: {e}")
        
        # Create a styled start button
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        
        self.start_button = QPushButton("Start Application")
        self.start_button.setMinimumSize(QSize(200, 50))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.start_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()
        
        layout.addWidget(self.text_browser)
        layout.addWidget(button_container)
        
    def update_theme(self, dark_mode):
        """Update the welcome screen appearance based on dark/light mode"""
        if dark_mode:
            self.text_browser.setStyleSheet("""
                QTextBrowser {
                    border: none;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
        else:
            self.text_browser.setStyleSheet("""
                QTextBrowser {
                    border: none;
                    background-color: #f8f9fa;
                    color: #000000;
                    padding: 20px;
                    font-size: 14px;
                }
            """)

if __name__ == "__main__":
    # Create and run the application
    app = QApplication(sys.argv)
    
    # Show welcome screen first
    welcome = WelcomeScreen()
    result = welcome.exec_()
    
    if result == QDialog.Accepted:
        # If user clicked Start, show the main application
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        # If welcome screen was closed, exit the application
        sys.exit(0)
