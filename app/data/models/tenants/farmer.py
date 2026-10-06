from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlmodel import Field

from app.data.models.tenants.base import TenantSQLModel


class Farmer(TenantSQLModel, table=True):
    __tablename__ = "farmers"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    farm_id: int = Field(
        sa_column=Column(
            ForeignKey("farms.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )

    full_name: str = Field(
        sa_column=Column(
            String(100),
            nullable=False,
        )
    )

    phone: str | None = Field(
        default=None,
        sa_column=Column(
            String(50),
            nullable=True,
        ),
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
