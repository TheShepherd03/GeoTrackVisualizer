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
