from docling.document_converter import DocumentConverter


class ExtractionService:
    def __init__(self):
        self._converter = None

    @property
    def converter(self):
        if self._converter is None:
            self._converter = DocumentConverter()
        return self._converter

    def extract_markdown(self, local_path: str) -> str:
        result = self.converter.convert(local_path)
        return result.document.export_to_markdown()


extraction_service = ExtractionService()
