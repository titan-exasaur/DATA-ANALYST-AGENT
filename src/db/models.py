from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def utc_now():
    return datetime.now(timezone.utc)


class FileMetadata(BaseModel):
    file_id: str
    session_id: str
    original_filename: str
    local_path: Optional[str] = None
    blob_url: Optional[str] = None
    file_size_bytes: int
    file_extension: str
    created_at: datetime = Field(default_factory=utc_now)


class SessionMetadata(BaseModel):
    session_id: str
    user_query: str
    file_id: str
    status: str = "created"
    agent_logs: List[str] = []
    errors: List[str] = []
    final_report: Optional[str] = None
    chart_titles: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)