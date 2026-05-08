class ExtractionService:
    def __init__(self):
        self._converter = None

    @property
    def converter(self):
        if self._converter is None:
            from docling.document_converter import DocumentConverter

            self._converter = DocumentConverter()
        return self._converter

    def extract_markdown(self, local_path: str) -> str:
        result = self.converter.convert(local_path)
        return result.document.export_to_markdown()


_extraction_service = None


def get_extraction_service():
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service
