"""added type to Responsibility

Revision ID: 2fa1bae647c4
Revises: 368c414a735a
Create Date: 2024-02-14 09:20:11.798043

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2fa1bae647c4'
down_revision = '368c414a735a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('responsibilities_with_certs', sa.Column('type', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('responsibilities_with_certs', 'type')
    # ### end Alembic commands ###
