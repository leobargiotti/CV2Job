import os
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit,
    QPushButton, QHBoxLayout, QFileDialog, QMessageBox
)
from pdf import extract_text_from_pdf, summarize_text
from job_matcher import load_embeddings, calculate_and_save_embeddings, check_predicted_job_similarity
from pop_up import BatchProcessingDialog

class JobMatchingApp(QMainWindow):
    def __init__(self):
        """
        Initialize the Job Matching App.

        This constructor sets up the main window and widgets for the app. It loads
        the embeddings for the job offers from a file, or calculates them if the
        file does not exist. It also sets up the events for the buttons.

        :return: None
        """
        self.jobs_excel = os.getenv("PATH_EXCEL_DATASET")
        embeddings_file = os.getenv("PATH_EMBEDDINGS")

        if os.path.exists(embeddings_file):
            self.embeddings = load_embeddings(embeddings_file)
        else:
            print("Calculating embeddings...")
            calculate_and_save_embeddings(self.jobs_excel, embeddings_file)
            print("Embeddings calculation completed.")
            self.embeddings = load_embeddings(embeddings_file)

        super().__init__()
        self.setWindowTitle("Job Matching System")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        button_layout = QHBoxLayout()

        self.upload_button = QPushButton("Upload CV PDF", self)
        button_layout.addWidget(self.upload_button)

        self.batch_button = QPushButton("Process Multiple PDFs", self)
        button_layout.addWidget(self.batch_button)

        button_layout.setStretch(0, 1)
        button_layout.setStretch(1, 1)

        self.upload_button.clicked.connect(self.handle_file_upload)
        self.batch_button.clicked.connect(self.open_batch_processing)

        self.layout.addLayout(button_layout)

        section1_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        summary_header_layout = QHBoxLayout()
        summary_label = QLabel("CV Summary", self)
        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_summary_text)
        summary_header_layout.addWidget(summary_label)
        summary_header_layout.addWidget(clear_button)
        left_layout.addLayout(summary_header_layout)

        self.summary_text = QTextEdit(self)
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlaceholderText("The CV summary will appear here...")
        left_layout.addWidget(self.summary_text)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Enter CV Information", self))
        self.cv_text = QTextEdit(self)
        self.cv_text.setPlaceholderText("Enter the text of your CV here...")
        right_layout.addWidget(self.cv_text)

        section1_layout.addLayout(left_layout)
        section1_layout.addLayout(right_layout)

        self.layout.addLayout(section1_layout)

        self.layout.addWidget(QLabel("Compare with Job Offers", self))
        self.compare_button = QPushButton("Match CV", self)
        self.compare_button.clicked.connect(self.handle_match)
        self.layout.addWidget(self.compare_button)

        self.layout.addWidget(QLabel("Best Match", self))
        self.result_area = QTextEdit(self)
        self.result_area.setReadOnly(True)
        self.layout.addWidget(self.result_area)

    def clear_summary_text(self):
        """
        Clears the content of the CV Summary box.
        """
        self.summary_text.clear()

    def handle_match(self):
        """
        Combines the CV summary and manual input for matching with job offers.
        Displays the best match in the results area.
        """
        summary_content = self.summary_text.toPlainText().strip()
        cv_text_content = self.cv_text.toPlainText().strip()
        combined_text = summary_content if cv_text_content.strip() == "" else f"{summary_content}\n{cv_text_content}"
        if not combined_text.strip():
            QMessageBox.critical(self, "Error", "Please enter or upload your CV text.")
            return

        if self.embeddings is None or self.embeddings.size == 0:
            QMessageBox.critical(self, "Error", "Embeddings are not calculated!")
            return
        try:
            result = check_predicted_job_similarity(combined_text, self.jobs_excel, self.embeddings)
            self.result_area.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during matching: {e}")

    def handle_file_upload(self):
        """
        Opens a file dialog to upload a CV file, extracts text, and summarizes it.
        Displays the summary in the CV Summary box.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Document",
            os.getenv("PATH_FOLDER_PDFS"),
            "PDF Files (*.pdf)"
        )
        if file_path:
            try:
                text = extract_text_from_pdf(file_path)
                try:
                    summary = summarize_text(text)
                    self.summary_text.setPlainText(summary)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error summarizing the text: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading the document: {e}")

    def open_batch_processing(self):
        """
        Opens a Batch Processing dialog.

        This dialog allows the user to select a folder containing multiple PDFs,
        specify an output file name and directory, and process the PDFs in batch.
        Each PDF is processed as if it were a single CV, and the results are written
        to a single Excel file.

        :return: None
        """
        batch_dialog = BatchProcessingDialog(self.embeddings, self.jobs_excel)
        batch_dialog.exec()

