"""add platform column to chat collections

Revision ID: b06833cbad39
Revises: 9c7f1cdc05c6
Create Date: 2024-12-30 06:12:33.282822+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b06833cbad39'
down_revision: Union[str, None] = '9c7f1cdc05c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_collections', sa.Column('platform', sa.String(length=10), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat_collections', 'platform')
    # ### end Alembic commands ###
