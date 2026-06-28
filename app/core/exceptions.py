class DocuQueryException(Exception):
    """Base exception for all custom app errors."""
    pass


class DocumentNotFound(DocuQueryException):
    def __init__(self, document_id: int):
        self.document_id = document_id
        super().__init__(f"Document with id {document_id} not found")


class UnsupportedFileType(DocuQueryException):
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Unsupported file type: {filename}. Only PDF files are accepted.")
