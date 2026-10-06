"""add farmer_id in farms table

Revision ID: 7da9cbef539e
Revises: 89b7b91250bf
Create Date: 2026-10-06 21:24:24.110700

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7da9cbef539e"
down_revision: Union[str, Sequence[str], None] = "89b7b91250bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "farms",
        sa.Column("farmer_id", sa.Integer(), nullable=True),
    )

    # Populate farmer_id for existing farms here
    # op.execute(...)

    op.alter_column(
        "farms",
        "farmer_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_foreign_key(
        "fk_farms_farmer_id",
        "farms",
        "farmers",
        ["farmer_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_farms_farmer_id",
        "farms",
        type_="foreignkey",
    )

    op.drop_column("farms", "farmer_id")
