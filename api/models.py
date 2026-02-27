from pydantic import BaseModel

class SubmitResponse(BaseModel):
    job_id: str
    message: str
