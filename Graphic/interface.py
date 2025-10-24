import pprint

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QTextEdit, QGroupBox, QDialog, QMessageBox
)
from Logic.service import NewsService
from Graphic.categories import CategoryDialog
from Graphic.articles import ArticleSelectionDialog
from datetime import datetime


class NewsApp(QWidget):
    """Main window handling user-logic interactions"""

    def __init__(self):
        super().__init__()
        self.news_service = NewsService()
        self.selected_categories = []
        self.fetched_articles = []
        self.current_summary = ""
        self.setup_ui()

    # --- UI setup functions ---
    def setup_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("AI News Summarizer")
        self.showMaximized()

        main_layout = QVBoxLayout()
        interface_layout = QHBoxLayout()
        interface_layout.setContentsMargins(10, 10, 10, 10)

        # Controls section
        controls_layout = self._create_controls_section()
        interface_layout.addLayout(controls_layout)

        # Status area
        interface_layout.addWidget(self._create_status_group())
        main_layout.addLayout(interface_layout)

        # Summary area
        main_layout.addWidget(self._create_summary_group())
        self.setLayout(main_layout)

    def _create_controls_section(self) -> QVBoxLayout:
        """Create the main controls section (settings, buttons, downloads)"""
        layout = QVBoxLayout()

        # Settings section
        layout.addLayout(self._create_settings_section())

        # Action buttons
        layout.addLayout(self._create_action_buttons())

        # Download buttons
        layout.addLayout(self._create_download_buttons())

        return layout

    def _create_settings_section(self) -> QHBoxLayout:
        """Create settings section with location, date and categories"""
        layout = QHBoxLayout()

        # Location dropdown
        layout.addWidget(QLabel("Location:"))
        self.location_dropdown = QComboBox()
        self.location_dropdown.addItems(self.news_service.available_locations)
        layout.addWidget(self.location_dropdown)
        layout.addSpacing(50)

        # Date dropdown
        layout.addWidget(QLabel("Date Range:"))
        self.date_dropdown = QComboBox()
        self.date_dropdown.addItems(self.news_service.available_date_ranges)
        layout.addWidget(self.date_dropdown)
        layout.addSpacing(50)

        # Categories button
        self.categories_btn = QPushButton("Select Categories (0 selected)")
        self.categories_btn.clicked.connect(self.open_category_dialog)
        layout.addWidget(self.categories_btn)
        layout.addStretch()

        return layout

    def _create_action_buttons(self) -> QHBoxLayout:
        """Create fetch and summarize action buttons"""
        layout = QHBoxLayout()

        self.fetch_btn = QPushButton("Fetch Articles")
        self.fetch_btn.clicked.connect(self.fetch_articles)
        self.fetch_btn.setEnabled(False)  # Initially disabled

        self.summarize_btn = QPushButton("Generate AI Summary")
        self.summarize_btn.clicked.connect(self.generate_summary)
        self.summarize_btn.setEnabled(False)  # Initially disabled

        layout.addWidget(self.fetch_btn)
        layout.addWidget(self.summarize_btn)
        layout.setContentsMargins(10, 10, 10, 10)

        return layout

    def _create_download_buttons(self) -> QHBoxLayout:
        """Create download/save buttons"""
        layout = QHBoxLayout()

        self.save_md_btn = QPushButton("Save as Markdown")
        self.save_md_btn.clicked.connect(self.save_as_markdown)
        self.save_md_btn.setEnabled(False)

        self.save_pdf_btn = QPushButton("Save as PDF")
        self.save_pdf_btn.clicked.connect(self.save_as_pdf)
        self.save_pdf_btn.setEnabled(False)

        layout.addWidget(self.save_md_btn)
        layout.addWidget(self.save_pdf_btn)

        return layout

    def _create_status_group(self) -> QGroupBox:
        """Create the status display group"""
        group = QGroupBox("Status")
        layout = QVBoxLayout()

        self.status_area = QTextEdit()
        self.status_area.setReadOnly(True)
        self.status_area.setMaximumHeight(150)

        layout.addWidget(self.status_area)
        group.setLayout(layout)
        group.setMaximumHeight(170)

        return group

    def _create_summary_group(self) -> QGroupBox:
        """Create the summary display group"""
        group = QGroupBox("AI Summary")
        layout = QVBoxLayout()

        self.summary_area = QTextEdit()
        self.summary_area.setReadOnly(True)

        layout.addWidget(self.summary_area)
        group.setLayout(layout)

        return group

    # --- Logic setup functions ---
    def open_category_dialog(self):
        """Open category selection dialog and update selection"""
        dialog = CategoryDialog(
            self.news_service.available_categories,
            self.selected_categories,
            self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_categories = dialog.get_selected_categories()
            self._update_ui_state()

    def _update_ui_state(self):
        """Update UI elements based on current application state"""
        # Update categories button
        count = len(self.selected_categories)
        self.categories_btn.setText(f"Select Categories ({count} selected)")

        # Update button states
        self.fetch_btn.setEnabled(count > 0)
        self.summarize_btn.setEnabled(False)
        self.save_md_btn.setEnabled(False)
        self.save_pdf_btn.setEnabled(False)

    def fetch_articles(self):
        """Fetch articles and open selection dialog"""
        if not self.news_service.validate_categories(self.selected_categories):
            self.set_status("Please select at least one category!")
            return

        self.set_status("Fetching articles... This may take a moment.")

        # Fetch articles
        location = self.location_dropdown.currentText()
        date_range = self.date_dropdown.currentText()

        self.fetched_articles = self.news_service.fetch_articles(
            location, date_range, self.selected_categories
        )

        # Let user select articles
        dialog = ArticleSelectionDialog(self.fetched_articles, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.fetched_articles = [a for a in dialog.get_selected_articles() if a['selected']]
            selected_count = len(self.fetched_articles)

            self.set_status(
                f"Fetched {len(self.fetched_articles)} articles. "
                f"Selected {selected_count} for analysis.\n\n"
                f"Ready to generate AI summary!"
            )

            self.summarize_btn.setEnabled(True)
            # TODO: Devo mettere una preview invece che dumpare il JSON
            pretty_articles = pprint.pformat(self.fetched_articles, width=120, depth=2)
            self.summary_area.setText(pretty_articles)

        else:
            self.set_status("Article selection cancelled.")
            self.summarize_btn.setEnabled(False)

    def generate_summary(self):
        """Generate AI summary from selected articles"""
        if not self.fetched_articles:
            self.summary_area.setText("Please fetch articles first!")
            return

        self.set_status("Generating AI summary... This may take a moment.")

        self.current_summary = self.news_service.generate_ai_summary(self.fetched_articles)
        self.summary_area.setText(self.current_summary)

        # Enable download options
        self.save_md_btn.setEnabled(True)
        self.save_pdf_btn.setEnabled(True)

        self.set_status("Summary generated! You can now save it as Markdown or PDF.")

    def _save_summary_wrapper(self, save_function, format_name: str):
        """Wrapper function for save operations to reduce code duplication"""
        if not self.current_summary:
            QMessageBox.warning(self, "Warning", f"No summary available to save as {format_name}!")
            return False

        try:
            saved_path = save_function(
                self.current_summary,
                self.location_dropdown.currentText(),
                self.selected_categories
            )

            if format_name == "PDF":
                self.set_status("Generating PDF... This may take a moment.")

            QMessageBox.information(self, "Success",
                                    f"{format_name} file saved successfully!\n{saved_path}")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save {format_name} file:\n{str(e)}")
            return False

    def save_as_markdown(self):
        """Save current summary as Markdown file"""
        if self._save_summary_wrapper(self.news_service.save_summary_markdown, "Markdown"):
            self.set_status("Markdown file saved successfully!")

    def save_as_pdf(self):
        """Save current summary as PDF file"""
        if self._save_summary_wrapper(self.news_service.save_summary_pdf, "PDF"):
            self.set_status("PDF generated successfully!")

    def set_status(self, text: str):
        """Update status area and force UI refresh"""
        self.status_area.setText(text)
        QApplication.processEvents()  # Force UI update