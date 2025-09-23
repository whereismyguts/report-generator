from pydantic import BaseModel, Field
from typing import List, Optional


class Task(BaseModel):
    task: str
    duration: int
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    type: Optional[str] = Field(None, description="'task' or 'meeting'")


class Day(BaseModel):
    date: str
    done: List[Task] = []


class ReportData(BaseModel):
    days: List[Day] = []
    not_mentioned_days: Optional[List[str]] = []
