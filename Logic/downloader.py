# Logic/document_generator.py
import os
from datetime import datetime
from typing import Optional


class DocumentGenerator:
    def __init__(self):
        # Always use document/news_report directory
        self.output_dir = self._get_output_directory()
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_output_directory(self):
        """Get the document/news_report directory in user's Documents folder"""
        # Get user's Documents folder
        documents_folder = os.path.expanduser("~/Documents")

        # Create document/news_report in user's Documents folder
        base_dir = os.path.join(documents_folder, "news_reports")

        try:
            os.makedirs(base_dir, exist_ok=True)
            # Test write permission
            test_file = os.path.join(base_dir, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return base_dir
        except (OSError, PermissionError) as e:
            # If we can't write to the preferred directory, try current directory as fallback
            fallback_dir = os.path.join(os.getcwd(), "document_news_report")
            os.makedirs(fallback_dir, exist_ok=True)
            print(f"Warning: Could not create directory {base_dir}. Using {fallback_dir} instead.")
            return fallback_dir

    def save_markdown(self, markdown_content: str, filename: Optional[str] = None) -> str:
        """Save markdown content to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_summary_{timestamp}.md"

        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            return filepath
        except Exception as e:
            raise Exception(f"Failed to save markdown file: {str(e)}")

    def save_as_pdf(self, markdown_content: str, filename: Optional[str] = None) -> str:
        """Convert markdown to PDF"""
        try:
            # Try weasyprint first
            return self._markdown_to_pdf_weasyprint(markdown_content, filename)
        except ImportError:
            try:
                # Try pdfkit as fallback
                return self._markdown_to_pdf_pdfkit(markdown_content, filename)
            except ImportError:
                # Fallback to markdown
                md_filename = filename.replace('.pdf', '.md') if filename else None
                md_path = self.save_markdown(markdown_content, md_filename)
                return f"PDF generation not available. Markdown saved at: {md_path}"
        except Exception as e:
            # If PDF generation fails, save as markdown
            md_filename = filename.replace('.pdf', '.md') if filename else None
            md_path = self.save_markdown(markdown_content, md_filename)
            return f"PDF generation failed. Markdown saved at: {md_path}"

    def _markdown_to_pdf_weasyprint(self, markdown_content: str, filename: Optional[str] = None) -> str:
        """Convert markdown to PDF using weasyprint"""
        try:
            from weasyprint import HTML
            import markdown

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"news_summary_{timestamp}.pdf"

            filepath = os.path.join(self.output_dir, filename)

            # Convert markdown to HTML
            html_content = markdown.markdown(markdown_content, extensions=['extra'])

            # Enhanced CSS styling for better PDF output
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>News Summary Report</title>
                <style>
                    @page {{
                        size: A4;
                        margin: 2cm;
                        @top-left {{
                            content: "News Summary Report";
                            font-size: 10px;
                            color: #666;
                        }}
                        @bottom-right {{
                            content: "Page " counter(page) " of " counter(pages);
                            font-size: 10px;
                            color: #666;
                        }}
                    }}

                    body {{
                        font-family: 'Helvetica', 'Arial', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                    }}

                    h1 {{
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }}

                    h2 {{
                        color: #34495e;
                        margin-top: 30px;
                        border-left: 4px solid #3498db;
                        padding-left: 10px;
                    }}

                    h3 {{
                        color: #7f8c8d;
                        margin-top: 20px;
                    }}

                    ul, ol {{
                        margin-left: 20px;
                        margin-bottom: 15px;
                    }}

                    li {{
                        margin-bottom: 8px;
                    }}

                    .header {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}

                    .footer {{
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #bdc3c7;
                        color: #7f8c8d;
                        font-size: 12px;
                    }}

                    strong {{
                        color: #2c3e50;
                    }}

                    a {{
                        color: #3498db;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 News Summary Report</h1>
                </div>
                {html_content}
                <div class="footer">
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} by AI News Summarizer</p>
                </div>
            </body>
            </html>
            """

            HTML(string=styled_html).write_pdf(filepath)
            return filepath

        except Exception as e:
            raise Exception(f"WeasyPrint PDF generation failed: {str(e)}")

    def _markdown_to_pdf_pdfkit(self, markdown_content: str, filename: Optional[str] = None) -> str:
        """Convert markdown to PDF using pdfkit"""
        try:
            import pdfkit
            import markdown

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"news_summary_{timestamp}.pdf"

            filepath = os.path.join(self.output_dir, filename)

            # Convert markdown to HTML
            html_content = markdown.markdown(markdown_content)

            # Basic styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                    h2 {{ color: #34495e; margin-top: 30px; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # Configure pdfkit options
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
            }

            pdfkit.from_string(styled_html, filepath, options=options)
            return filepath

        except Exception as e:
            raise Exception(f"PDFKit PDF generation failed: {str(e)}")