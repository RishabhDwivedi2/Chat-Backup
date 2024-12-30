"""Sub type column added in Artifact Table

Revision ID: 4b25c760e0d5
Revises: a6b0628db0fc
Create Date: 2024-12-21 06:29:01.491503+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b25c760e0d5'
down_revision: Union[str, None] = 'a6b0628db0fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artifacts', sa.Column('sub_type', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artifacts', 'sub_type')
    # ### end Alembic commands ###