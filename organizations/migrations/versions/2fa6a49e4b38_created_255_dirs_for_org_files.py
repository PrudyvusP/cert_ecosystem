"""created 255 dirs for org files

Revision ID: 2fa6a49e4b38
Revises: d5113edd64af
Create Date: 2022-09-06 14:35:23.633753

"""
import os
import shutil
import uuid

basedir = os.path.abspath(
    os.path.dirname(
        (os.path.dirname(
            os.path.dirname(__file__)
        )
        )
    )
)
main_dir_name = os.path.join(basedir,
                             'organizations',
                             'static',
                             'organizations')

# revision identifiers, used by Alembic.
revision = '2fa6a49e4b38'
down_revision = 'd5113edd64af'
branch_labels = None
depends_on = None


def upgrade():
    os.makedirs(main_dir_name, exist_ok=True)
    prefixes = set([str(uuid.uuid4())[:2].upper() for _ in range(100000)])
    for prefix in prefixes:
        os.makedirs(os.path.join(main_dir_name, prefix), exist_ok=True)


def downgrade():
    shutil.rmtree(main_dir_name)
