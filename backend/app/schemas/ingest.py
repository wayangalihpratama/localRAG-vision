from pydantic import BaseModel


class IngestResponse(BaseModel):
    task_id: str
    file_id: str
    filename: str
    message: str
