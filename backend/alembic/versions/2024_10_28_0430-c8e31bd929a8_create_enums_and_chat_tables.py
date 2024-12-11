"""create_enums_and_chat_tables

Revision ID: c8e31bd929a8
Revises: cd1084405f2a
Create Date: 2024-10-28 04:30:28.430874+00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c8e31bd929a8'
down_revision: Union[str, None] = 'cd1084405f2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types first
    op.execute("CREATE TYPE file_type AS ENUM ('media', 'document', 'voice')")
    op.execute("CREATE TYPE conversation_status AS ENUM ('active', 'archived', 'deleted')")
    
    # Add status column to conversations table if it exists
    op.add_column('conversations', 
        sa.Column('status', 
            postgresql.ENUM('active', 'archived', 'deleted', name='conversation_status'),
            nullable=False,
            server_default='active'
        )
    )
    
    # Add file_type column to attachments table if it exists
    op.add_column('attachments',
        sa.Column('file_type',
            postgresql.ENUM('media', 'document', 'voice', name='file_type'),
            nullable=False
        )
    )

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
        sa.ForeignKeyConstraint(['parent_message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_id', 'messages', ['id'])

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
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id')
    )
    op.create_index('ix_artifacts_id', 'artifacts', ['id'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('artifacts')
    op.drop_table('messages')
    
    # Remove columns
    op.drop_column('attachments', 'file_type')
    op.drop_column('conversations', 'status')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS file_type')
    op.execute('DROP TYPE IF EXISTS conversation_status')