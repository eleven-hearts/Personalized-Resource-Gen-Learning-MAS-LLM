from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ResourceBase(BaseModel):
    title: str
    resource_type: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        validation_alias=AliasChoices("metadata_json", "metadata"),
    )

    model_config = ConfigDict(populate_by_name=True)


class ResourceCreate(ResourceBase):
    user_id: int


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ResourceInDB(ResourceBase):
    id: int
    user_id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ResourceResponse(ResourceInDB):
    pass
