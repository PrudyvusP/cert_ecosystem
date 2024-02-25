"""added services

Revision ID: 478ed1cd575a
Revises: 2fa1bae647c4
Create Date: 2024-02-14 10:56:46.436626

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '478ed1cd575a'
down_revision = '2fa1bae647c4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO services VALUES"
               " (1, 'ВЗАИМОДЕЙСТВИЕ С НКЦКИ'),"
               " (2, 'РАЗРАБОТКА ДОКУМЕНТОВ ОПКА'),"
               " (3, 'ЭКСПЛУАТАЦИЯ СРЕДСТВ ГОССОПКА'),"
               " (4, 'ПРИЕМ СООБЩЕНИЙ ОБ ИНЦИДЕНТАХ'),"
               " (5, 'РЕГИСТРАЦИЯ КА И КИ'),"
               " (6, 'АНАЛИЗ СОБЫТИЙ ИБ'),"
               " (7, 'ИНВЕНТАРИЗАЦИЯ ИР'),"
               " (8, 'АНАЛИЗ УГРОЗ ИБ'),"
               " (9, 'СОСТАВЛЕНИЕ И АКТУАЛИЗАЦИЯ ПЕРЕЧНЯ УГРОЗ ИБ'),"
               " (10, 'ВЫЯВЛЕНИЕ УЯЗВИМОСТЕЙ ИР'),"
               " (11, 'ФОРМИРОВАНИЕ ПРЕДЛОЖЕНИЙ ПО ПОВЫШЕНИЮ УРОВНЯ ЗАЩИЩЕННОСТИ ИР'),"
               " (12, 'СОСТАВЛЕНИЕ ПЕРЕЧНЯ КИ'),"
               " (13, 'ЛИКВИДАЦИЯ ПОСЛЕДСТВИЙ КИ'),"
               " (14, 'АНАЛИЗ РЕЗУЛЬТАТОВ ЛИКВИДАЦИИ ПОСЛЕДСТВИЙ КИ'),"
               " (15, 'УСТАНОВЛЕНИЕ ПРИЧИН КИ');")


def downgrade():
    op.execute("DELETE FROM services")
