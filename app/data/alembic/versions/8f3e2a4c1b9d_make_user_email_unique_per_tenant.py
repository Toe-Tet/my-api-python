"""make user email unique per tenant

Revision ID: 8f3e2a4c1b9d
Revises: 388345455bab
Create Date: 2026-10-07 10:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f3e2a4c1b9d"
down_revision: Union[str, Sequence[str], None] = "388345455bab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_unique_constraint_for_columns(
    table_name: str,
    target_columns: list[str],
) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for constraint in inspector.get_unique_constraints(table_name):
        column_names = constraint.get("column_names") or []
        constraint_name = constraint.get("name")

        if column_names == target_columns and constraint_name:
            op.drop_constraint(constraint_name, table_name, type_="unique")


def upgrade() -> None:
    """Upgrade schema."""
    _drop_unique_constraint_for_columns("users", ["email"])
    op.create_unique_constraint(
        "uq_users_email_tenant_id",
        "users",
        ["email", "tenant_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    _drop_unique_constraint_for_columns("users", ["email", "tenant_id"])
    op.create_unique_constraint(
        "users_email_key",
        "users",
        ["email"],
    )
