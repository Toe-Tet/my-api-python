from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"

    id: str = Field(
        primary_key=True,
        max_length=255,
    )

    identifier: str = Field(
        sa_column=Column(
            String(255),
            unique=True,
            nullable=False,
        )
    )

    name: str = Field(
        sa_column=Column(
            String(255),
            nullable=False,
        )
    )

    status: str = Field(
        default="active",
        max_length=50,
        nullable=False,
    )

    isolation_strategy: str | None = Field(
        default=None,
        max_length=50,
        nullable=True,
    )

    database_url: str | None = Field(
        default=None,
        sa_column=Column(
            Text,
            nullable=True,
        ),
    )

    schema_name: str | None = Field(
        default=None,
        max_length=255,
        nullable=True,
    )

    tenant_metadata: str = Field(
        default="{}",
        sa_column=Column(
            Text,
            nullable=False,
            server_default="{}",
        ),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
            "nullable": False,
        },
    )
