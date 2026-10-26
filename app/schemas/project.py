from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class ProjectCreate(ProjectBase):
    owner_id: int


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> "ProjectUpdate":
        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name cannot be null")
        return self


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
