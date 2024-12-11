"""Artifact Fields Updated again

Revision ID: 2031bae14ed7
Revises: 0ddb8165e788
Create Date: 2024-10-29 06:20:10.626104+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2031bae14ed7'
down_revision: Union[str, None] = '0ddb8165e788'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artifacts', sa.Column('status', sa.String(length=20), nullable=True))
    op.alter_column('artifacts', 'message_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('artifacts', 'component_type',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=50),
               nullable=True)
    op.alter_column('artifacts', 'data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('artifacts', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               server_default=None,
               type_=sa.DateTime(),
               existing_nullable=True)
    op.alter_column('artifacts', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=True)
    op.drop_constraint('artifacts_message_id_fkey', 'artifacts', type_='foreignkey')
    op.create_foreign_key(None, 'artifacts', 'messages', ['message_id'], ['id'])
    op.drop_column('artifacts', 'configuration')
    op.drop_column('artifacts', 'style')
    op.drop_column('artifacts', 'description')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artifacts', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('artifacts', sa.Column('style', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('artifacts', sa.Column('configuration', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'artifacts', type_='foreignkey')
    op.create_foreign_key('artifacts_message_id_fkey', 'artifacts', 'messages', ['message_id'], ['id'], ondelete='CASCADE')
    op.alter_column('artifacts', 'updated_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('artifacts', 'created_at',
               existing_type=sa.DateTime(),
               server_default=sa.text('now()'),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('artifacts', 'data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.alter_column('artifacts', 'component_type',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=20),
               nullable=False)
    op.alter_column('artifacts', 'message_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('artifacts', 'status')
    # ### end Alembic commands ###
