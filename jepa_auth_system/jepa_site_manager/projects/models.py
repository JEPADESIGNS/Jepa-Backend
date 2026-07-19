"""Data models for the Project Management module."""

from dataclasses import dataclass


@dataclass
class ProjectRecord:
    project_name: str
    client: str | None = None
    location: str | None = None
    budget: float = 0.0
    start_date: str | None = None
    end_date: str | None = None
    status: str = "Planning"
    created_by: int | None = None
