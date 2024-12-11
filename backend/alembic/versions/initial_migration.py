# alembic/versions/initial_migration.py

"""initial_migration

Revision ID: cd1084405f2a
Revises: 
Create Date: 2024-10-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'cd1084405f2a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop existing types first
    op.execute('DROP TYPE IF EXISTS message_role CASCADE;')
    op.execute('DROP TYPE IF EXISTS message_type CASCADE;')
    op.execute('DROP TYPE IF EXISTS file_type CASCADE;')
    op.execute('DROP TYPE IF EXISTS artifact_type CASCADE;')
    op.execute('DROP TYPE IF EXISTS component_type CASCADE;')
    op.execute('DROP TYPE IF EXISTS conversation_status CASCADE;')
    
    # Drop existing tables
    op.execute('DROP TABLE IF EXISTS artifact_metadata CASCADE;')
    op.execute('DROP TABLE IF EXISTS artifacts CASCADE;')
    op.execute('DROP TABLE IF EXISTS messages CASCADE;')
    
    # Create new messages table
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

    # Create new artifacts table
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