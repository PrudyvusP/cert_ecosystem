"""added is_250 column to org

Revision ID: 1c1219b5fd17
Revises: ac48bbb7e973
Create Date: 2024-05-07 12:58:48.522776

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1c1219b5fd17'
down_revision = 'ac48bbb7e973'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('organizations', sa.Column('is_250', sa.Boolean(),
                                             server_default=sa.text('false'),
                                             nullable=True))


def downgrade():
    op.drop_column('organizations', 'is_250')
