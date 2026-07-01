from pydantic import BaseModel


class HealthResponse(BaseModel):
    success: bool
    status: str
    service: str

