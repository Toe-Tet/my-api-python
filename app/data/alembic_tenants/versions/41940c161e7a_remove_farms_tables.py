"""remove farms tables

Revision ID: 41940c161e7a
Revises: 7da9cbef539e
Create Date: 2026-10-06 23:02:53.327277

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "41940c161e7a"
down_revision: Union[str, Sequence[str], None] = "7da9cbef539e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("farms")


def downgrade() -> None:
    # Recreate the farms table here if you need rollback support
    pass
