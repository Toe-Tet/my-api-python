from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field

from app.data.models.tenants.base import TenantSQLModel


class Farm(TenantSQLModel, table=True):
    __tablename__ = "farms"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    name: str = Field(
        sa_column=Column(
            String(100),
            nullable=False,
        )
    )

    is_active: bool = Field(
        default=True,
        nullable=False,
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
