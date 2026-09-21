from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass
class Task:
    name: str
    description: str
    deadline: date
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "deadline": self.deadline.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            deadline=date.fromisoformat(data["deadline"]),
        )

    def deadline_label(self) -> str:
        return self.deadline.strftime("%d %b %Y")

    def is_overdue(self, today: date | None = None) -> bool:
        return self.deadline < (today or date.today())
