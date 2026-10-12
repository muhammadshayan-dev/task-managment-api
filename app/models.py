from app.database import Base


class BaseModel(Base):
    __abstract__ = True

from datetime import datetime , timezone
from sqlalchemy import Boolean , DateTime , Integer , String , ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    email: Mapped[str] = mapped_column(String(255) , unique = True , index = True, nullable = False)
    full_name : Mapped[str] = mapped_column(String(255) , nullable = False)
    hashed_password : Mapped[str] = mapped_column(String(255) , nullable = False)
    is_active: Mapped[bool] = mapped_column(Boolean , default = True , nullable = False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime , default = lambda: datetime.now(timezone.utc),)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime , default = lambda: datetime.now(timezone.utc),
                                                  onupdate= lambda: datetime.now(timezone.utc),)

class Task(BaseModel):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        default="medium",
        nullable=False,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )