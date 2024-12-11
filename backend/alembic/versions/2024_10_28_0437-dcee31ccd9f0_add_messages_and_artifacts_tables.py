"""add_messages_and_artifacts_tables

Revision ID: dcee31ccd9f0
Revises: d71234567890
Create Date: 2024-10-28 04:37:39.569859+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcee31ccd9f0'
down_revision: Union[str, None] = 'd71234567890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
