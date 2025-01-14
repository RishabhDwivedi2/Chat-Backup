"""is platform changed column added in chat collections table

Revision ID: af7ac4824ad9
Revises: cd005f679f53
Create Date: 2025-01-03 05:36:45.675250+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af7ac4824ad9'
down_revision: Union[str, None] = 'cd005f679f53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_collections', sa.Column('is_platform_changed', sa.Boolean(), nullable=True))
    op.drop_column('chat_collections', 'chat_continue_notification')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_collections', sa.Column('chat_continue_notification', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('chat_collections', 'is_platform_changed')
    # ### end Alembic commands ###
