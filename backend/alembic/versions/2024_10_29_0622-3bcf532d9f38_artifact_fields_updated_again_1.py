"""Artifact Fields Updated again 1

Revision ID: 3bcf532d9f38
Revises: 2031bae14ed7
Create Date: 2024-10-29 06:22:14.640213+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3bcf532d9f38'
down_revision: Union[str, None] = '2031bae14ed7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artifacts', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('artifacts', sa.Column('style', sa.JSON(), nullable=True))
    op.add_column('artifacts', sa.Column('configuration', sa.JSON(), nullable=True))
    op.alter_column('artifacts', 'message_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('artifacts', 'component_type',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=20),
               nullable=False)
    op.alter_column('artifacts', 'data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.alter_column('artifacts', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('artifacts', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.drop_constraint('artifacts_message_id_fkey', 'artifacts', type_='foreignkey')
    op.create_foreign_key(None, 'artifacts', 'messages', ['message_id'], ['id'], ondelete='CASCADE')
    op.drop_column('artifacts', 'status')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artifacts', sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'artifacts', type_='foreignkey')
    op.create_foreign_key('artifacts_message_id_fkey', 'artifacts', 'messages', ['message_id'], ['id'])
    op.alter_column('artifacts', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('artifacts', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=None,
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('artifacts', 'data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('artifacts', 'component_type',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=50),
               nullable=True)
    op.alter_column('artifacts', 'message_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('artifacts', 'configuration')
    op.drop_column('artifacts', 'style')
    op.drop_column('artifacts', 'description')
    # ### end Alembic commands ###
