"""add_password_reset_columns_to_users

Revision ID: f1a2b3c4d5e6
Revises: e7f8a9b0c1d2
Create Date: 2026-09-19 12:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
# pyrefly: ignore [missing-import]
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'e7f8a9b0c1d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('reset_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('last_reset_request', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_users_reset_token'), 'users', ['reset_token'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_reset_token'), table_name='users')
    op.drop_column('users', 'last_reset_request')
    op.drop_column('users', 'reset_expires_at')
    op.drop_column('users', 'reset_token')
