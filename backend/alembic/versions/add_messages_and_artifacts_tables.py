"""add_messages_and_artifacts_tables

Revision ID: d71234567890
Revises: c8e31bd929a8
Create Date: 2024-10-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd71234567890'
down_revision: Union[str, None] = 'c8e31bd929a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Explicitly drop tables if they exist
    op.execute('DROP TABLE IF EXISTS artifacts CASCADE')
    op.execute('DROP TABLE IF EXISTS messages CASCADE')

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=10), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('message_type', sa.String(length=10), nullable=False),
        sa.Column('parent_message_id', sa.Integer(), nullable=True),
        sa.Column('has_artifact', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_id', 'messages', ['id'])

    # Add self-referential foreign key for parent_message_id after table creation
    op.create_foreign_key(
        'fk_messages_parent_id', 'messages', 'messages',
        ['parent_message_id'], ['id'], ondelete='SET NULL'
    )

    # Create artifacts table
    op.create_table(
        'artifacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('component_type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('style', sa.JSON(), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id')
    )
    op.create_index('ix_artifacts_id', 'artifacts', ['id'])

def downgrade() -> None:
    op.drop_table('artifacts')
    op.drop_table('messages')