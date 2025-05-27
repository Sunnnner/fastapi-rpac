from sqlmodel import Field, SQLModel

from datetime import datetime


class UserRole(SQLModel, table=True):
    
    user_id: int = Field(primary_key=True, foreign_key="user.id", description="用户ID")
    role_id: int = Field(primary_key=True, foreign_key="role.id", description="角色ID")
    created_at: datetime = Field(default=datetime.now(), description="创建时间")
    updated_at: datetime = Field(default=datetime.now(), description="更新时间")
    
    def __repr__(self):
        return f"<UserRole {self.user_id} {self.role_id}>"

    def __str__(self):
        return f"{self.user_id} {self.role_id}"