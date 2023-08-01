"""Add image_url column to events

Revision ID: 80479114018c
Revises: cf75f3e5513d
Create Date: 2023-08-01 22:15:30.171039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80479114018c'
down_revision = 'cf75f3e5513d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('events', sa.Column('image_url', sa.String(length=200), nullable=True))


def downgrade():
    op.drop_column('events', 'image_url')
