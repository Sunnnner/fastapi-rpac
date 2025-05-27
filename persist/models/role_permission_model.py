from sqlmodel import Field, SQLModel

from datetime import datetime


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permission"
    role_id: int = Field(primary_key=True, foreign_key="role.id", description="角色ID")
    permission_id: int = Field(primary_key=True, foreign_key="permission.id", description="权限ID")
    created_at: datetime = Field(default=datetime.now(), description="创建时间")
    updated_at: datetime = Field(default=datetime.now(), description="更新时间")
    
    def __repr__(self):
        return f"<RolePermission {self.role_id} {self.permission_id}>"

    def __str__(self):
        return f"{self.role_id} {self.permission_id}"