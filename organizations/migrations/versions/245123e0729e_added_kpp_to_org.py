"""added kpp to org

Revision ID: 245123e0729e
Revises: 9b21fc22c8d7
Create Date: 2023-01-06 14:18:06.349178

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '245123e0729e'
down_revision = '9b21fc22c8d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organizations', sa.Column('kpp', sa.String(length=9), nullable=True))
    op.create_index(op.f('ix_organizations_kpp'), 'organizations', ['kpp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_organizations_kpp'), table_name='organizations')
    op.drop_column('organizations', 'kpp')
    # ### end Alembic commands ###