import datetime
from typing import List, Tuple

from flask import current_app as app

from .extentions import db
from .models import Message, methodicaldocs_messages, Organization
from .utils import send_mail
from .views.organization import METHOD_DOC_OUTPUT_NUMBER_TEXT


def get_unexecuted_messages() -> List[Tuple[datetime.datetime, str]]:
    """Возвращает дату подписи (генерации) письма с методичками
     и название адресата, исполнение которого не внесено в сервис."""
    message_subquery = (
        db.session
        .query(Message.message_id.distinct())
        .join(
            methodicaldocs_messages,
            methodicaldocs_messages.c.message_id == Message.message_id
        )
        .filter(~methodicaldocs_messages.c.method_id.is_(None))
        .filter(Message.our_outbox_number == METHOD_DOC_OUTPUT_NUMBER_TEXT)
        .all()
    )
    message_subquery = [i for i, in message_subquery]
    return (db.session
            .query(Message.date_approved, Organization.full_name)
            .join(Organization, Message.organizations)
            .filter(Message.message_id.in_(message_subquery))
            .all()
            )


def get_notify_text(messages: List[Tuple[datetime.datetime, str]]):
    """Возвращает строку с невнесенными в сервис письмами."""
    results = []
    if messages:
        for message in messages:
            strq = f'Письмо в организацию {message[1]}, созданное {message[0]}'
            results.append(strq)
    return ';\n'.join(results)


def send_notify_email():
    """Отправляет email-письмо, содержащее реквизиты
    писем, исполнение которых не отражено в сервисе."""
    text = get_notify_text(get_unexecuted_messages())
    subject = ('CERT-ECOSYSTEM - Информация об'
               ' имеющихся в работе неисполненных письмах')
    send_to = app.config['BOSS_EMAIL_FOR_NOTIFY']
    text = ('По состоянию на сегодняшний день в работе имеются следующие'
            ' письма, исполнение которых отсутствует в сервисе:\n') + text
    user = app.config['SMTP_USER']
    password = app.config['SMTP_PASSWORD']
    send_mail(user=user,
              password=password,
              send_to=send_to,
              subject=subject,
              text=text,
              host=app.config['SMTP_HOST'],
              port=app.config['SMTP_PORT']
              )
