from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict, model_validator

from app.core import messages


class BaseSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class UpdateSchema(BaseSchema):
    non_nullable_fields: ClassVar[tuple[str, ...]] = ()

    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> Self:
        for field in self.non_nullable_fields:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(messages.FIELD_CANNOT_BE_NULL.format(field=field))
        return self
