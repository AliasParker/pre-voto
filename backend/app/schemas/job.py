from pydantic import BaseModel


class JobResponse(BaseModel):
    job: str
    status: str  # "completed", "started", "failed"
    items_processed: int = 0
    errors: int = 0
    duration_ms: int | None = None
