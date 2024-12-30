"""Add thread_id to conversations

Revision ID: e5ccf64dffa3
Revises: b06833cbad39
Create Date: 2024-12-30 08:55:26.205473+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5ccf64dffa3'
down_revision: Union[str, None] = 'b06833cbad39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conversations', sa.Column('thread_id', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('conversations', 'thread_id')
    # ### end Alembic commands ###