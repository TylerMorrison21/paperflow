from pydantic import BaseModel

class UploadResponse(BaseModel):
    paper_id: str
    status: str

class PaperStatus(BaseModel):
    paper_id: str
    status: str
    error: str | None = None

class TOCItem(BaseModel):
    id: str
    title: str
    level: int
    anchor: str

class Section(BaseModel):
    id: str
    heading: str
    level: int
    markdown: str
    page_start: int | None = None
    page_end: int | None = None

class PaperData(BaseModel):
    title: str
    toc: list[TOCItem]
    sections: list[Section]
    images: dict[str, str]
    metadata: dict
