"""added is_main to OrgAdmDoc

Revision ID: 3ff23da18617
Revises: f4fc4c11eb45
Create Date: 2023-12-18 08:51:42.449037

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '3ff23da18617'
down_revision = 'f4fc4c11eb45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orgadm_docs', sa.Column('is_main', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orgadm_docs', 'is_main')
    # ### end Alembic commands ###