from datetime import datetime
from sqlmodel import Field, SQLModel, String


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, description="用户ID")
    username: str = Field(sa_type=String(length=50), nullable=False, description="用户名")
    email: str = Field(sa_type=String(length=100), nullable=True, description="邮箱")
    password: str = Field(sa_type=String(length=255), nullable=False, description="密码")
    created_at: datetime = Field(default=datetime.now(), description="创建时间")
    updated_at: datetime = Field(default=datetime.now(), description="更新时间")

    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return self.username