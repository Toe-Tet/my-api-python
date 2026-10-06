from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    username: str = Field(
        sa_column=Column(
            String(100),
            nullable=False,
        )
    )

    email: str = Field(
        sa_column=Column(
            String(255),
            unique=True,
            nullable=False,
        )
    )

    phone: str = Field(
        sa_column=Column(
            String(255),
            nullable=False,
        )
    )

    password: str = Field(
        max_length=255,
        nullable=False,
    )

    is_active: bool = Field(
        default=True,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    updated_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )
