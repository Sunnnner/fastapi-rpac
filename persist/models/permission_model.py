from sqlmodel import Field, SQLModel, String

from datetime import datetime


class Permission(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, description="权限ID")
    name: str = Field(sa_type=String(length=50), nullable=False, description="权限名")
    description: str = Field(sa_type=String(length=255), nullable=True, description="权限描述")
    created_at: datetime = Field(default=datetime.now(), description="创建时间")
    updated_at: datetime = Field(default=datetime.now(), description="更新时间")