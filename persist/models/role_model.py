from sqlmodel import Field, SQLModel, String

from datetime import datetime


class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, description="角色ID")
    name: str = Field(sa_type=String(length=50), nullable=False, description="角色名")
    description: str = Field(sa_type=String(length=255), nullable=True, description="角色描述")
    created_at: datetime = Field(default=datetime.now(), description="创建时间")
    updated_at: datetime = Field(default=datetime.now(), description="更新时间")
    

    def __repr__(self):
        return f"<Role {self.name}>"

    def __str__(self):
        return self.name