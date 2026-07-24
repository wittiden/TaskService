from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FullTaskInfoDTO(BaseModel):
    """DTO для передачи полных данных о задаче"""

    task_id: UUID
    user_id: UUID
    created_at: datetime
    closed_at: datetime | None
    completed_at: datetime | None
    updated_at: datetime | None
