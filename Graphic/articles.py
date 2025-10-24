from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QWidget, QCheckBox, QDialogButtonBox,
    QGroupBox, QLabel
)
from typing import List, Dict


class ArticleSelectionDialog(QDialog):
    """Window to select articles types to feed the AI"""

    def __init__(self, articles: List[Dict], parent=None):
        super().__init__(parent)
        self.articles = articles
        self.article_checkboxes = {}
        self.setup_ui()

    # --- UI setup functions ---
    def setup_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Select Articles to Analyze")
        self.resize(700, 600)

        layout = QVBoxLayout()

        # Header with selection controls
        layout.addLayout(self._create_header())

        # Articles list
        layout.addWidget(self._create_articles_scroll_area())

        # Dialog buttons
        layout.addWidget(self._create_button_box())

        self.setLayout(layout)
        self.update_selection_count()

    def _create_header(self) -> QHBoxLayout:
        """Create header with selection info"""
        layout = QHBoxLayout()

        self.selection_label = QLabel(f"0 of {len(self.articles)} articles selected")
        layout.addWidget(self.selection_label)
        layout.addStretch()

        # Create bulk action buttons
        buttons = [
            ("Select All", self.select_all),
            ("Deselect All", self.deselect_all)
        ]

        for text, slot in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        return layout

    def _create_articles_scroll_area(self) -> QScrollArea:
        """Create scroll area with article selection items"""
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.articles_layout = QVBoxLayout(scroll_widget)

        # Create article items
        for article in self.articles:
            self.articles_layout.addWidget(self._create_article_item(article))

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        return scroll

    def _create_article_item(self, article: Dict) -> QGroupBox:
        """Create a single article selection item with preview"""
        group = QGroupBox()
        group.setStyleSheet("QGroupBox { border: 1px solid gray; border-radius: 5px; margin-top: 1ex; }")
        layout = QVBoxLayout()

        # Title with checkbox
        checkbox = self._create_article_checkbox(article)
        layout.addLayout(self._create_title_row(article, checkbox))

        # Metadata
        layout.addLayout(self._create_metadata_row(article))

        # Preview
        layout.addWidget(self._create_preview_label(article))

        group.setLayout(layout)
        return group

    def _create_article_checkbox(self, article: Dict) -> QCheckBox:
        """Create and register article checkbox"""
        checkbox = QCheckBox()
        checkbox.setChecked(article.get('selected', False))
        checkbox.toggled.connect(self.update_selection_count)
        self.article_checkboxes[article['id']] = checkbox
        return checkbox

    def _create_title_row(self, article: Dict, checkbox: QCheckBox) -> QHBoxLayout:
        """Create title row with checkbox"""
        layout = QHBoxLayout()
        layout.addWidget(checkbox)

        title_label = QLabel(f"<b>{article['title']}</b>")
        title_label.setWordWrap(True)
        layout.addWidget(title_label, 1)

        return layout

    def _create_metadata_row(self, article: Dict) -> QHBoxLayout:
        """Create metadata row with source and category"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(f"Source: {article['source']}"))
        layout.addWidget(QLabel(f"Category: {article['category']}"))
        layout.addStretch()
        return layout

    def _create_preview_label(self, article: Dict) -> QLabel:
        """Create content preview label"""
        preview_text = self._generate_preview_text(article['content'])
        preview = QLabel(preview_text)
        preview.setWordWrap(True)
        preview.setStyleSheet("color: gray; font-size: 10px;")
        return preview

    def _generate_preview_text(self, content: str, word_limit: int = 20) -> str:
        """Generate preview text from content"""
        words = content.split()[:word_limit]
        return ' '.join(words) + "..." if len(words) == word_limit else ' '.join(words)

    def _create_button_box(self) -> QDialogButtonBox:
        """Create standard dialog button box"""
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def select_all(self):
        """Select all articles"""
        self._set_all_checkboxes(True)

    def deselect_all(self):
        """Deselect all articles"""
        self._set_all_checkboxes(False)

    def _set_all_checkboxes(self, state: bool):
        """Set all checkboxes to specified state"""
        for checkbox in self.article_checkboxes.values():
            checkbox.setChecked(state)
        self.update_selection_count()

    # --- Logic setup functions ---
    def update_selection_count(self):
        """Update the selection count label"""
        selected_count = sum(checkbox.isChecked() for checkbox in self.article_checkboxes.values())
        self.selection_label.setText(f"{selected_count} of {len(self.articles)} articles selected")

    def get_selected_articles(self) -> List[Dict]:
        """Return updated articles with selection status"""
        return [
            {**article, 'selected': self.article_checkboxes[article['id']].isChecked()}
            for article in self.articles
        ]