from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QCheckBox, QScrollArea, QWidget, QDialogButtonBox
)
from typing import List, Set


class CategoryDialog(QDialog):
    """Dialog for selecting categories with bulk operations"""

    def __init__(self, available_categories: List[str], selected_categories: List[str], parent=None):
        super().__init__(parent)
        self.available_categories = available_categories
        self.selected_categories = set(selected_categories)  # Use set for faster lookups
        self.checkboxes = {}
        self._setup_ui()

    # --- UI setup functions ---
    def _setup_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Select Categories")
        self.resize(400, 300)  # Simplified geometry setting

        layout = QVBoxLayout()

        # Bulk selection buttons
        layout.addLayout(self._create_bulk_buttons())

        # Categories list
        layout.addWidget(self._create_categories_scroll_area())

        # Dialog buttons
        layout.addWidget(self._create_button_box())

        self.setLayout(layout)

    def _create_bulk_buttons(self) -> QHBoxLayout:
        """Create Select All/Deselect All buttons"""
        layout = QHBoxLayout()

        buttons = [
            ("Select All", self._select_all),
            ("Deselect All", self._deselect_all)
        ]

        for text, slot in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        layout.addStretch()
        return layout

    def _create_categories_scroll_area(self) -> QScrollArea:
        """Create scrollable categories list"""
        scroll = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)

        # Create checkboxes for all categories
        for category in self.available_categories:
            checkbox = QCheckBox(category)
            checkbox.setChecked(category in self.selected_categories)
            checkbox.toggled.connect(self._update_selection)
            layout.addWidget(checkbox)
            self.checkboxes[category] = checkbox

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        return scroll

    def _create_button_box(self) -> QDialogButtonBox:
        """Create standard buttons"""
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _select_all(self):
        """Select all categories"""
        self._set_all_checkboxes(True)

    def _deselect_all(self):
        """Deselect all categories"""
        self._set_all_checkboxes(False)

    def _set_all_checkboxes(self, state: bool):
        """Set all checkboxes to specified state"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(state)

    # --- Logic setup functions ---
    def _update_selection(self):
        """Update selected categories set when any checkbox changes"""
        self.selected_categories = {
            category for category, checkbox in self.checkboxes.items()
            if checkbox.isChecked()
        }

    def get_selected_categories(self) -> List[str]:
        """Return selected categories as sorted list"""
        return sorted(self.selected_categories)  # Return predictable order