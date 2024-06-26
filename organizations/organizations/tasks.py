import copy
import datetime
from typing import List, Tuple

from celery import shared_task
from flask import current_app as app

from .extentions import db
from .models import Message, Organization, methodicaldocs_messages
from .utils import create_zip_archive_mem, get_cur_time, send_mail
from .views.organization import METHOD_DOC_OUTPUT_NUMBER_TEXT
from .xml_parser import XMLHandler


@shared_task(ignore_results=True)
def aparse_xml(file_paths, email):
    log_names = []
    cur_time = get_cur_time()

    for file in file_paths:
        log_file_name = f'{file[0]}-{cur_time}.log'
        handler = XMLHandler(
            file=file[0], logger_file=log_file_name,
            schema=app.config['BUSINESS_LOGIC']['XSD_SCHEMA_PATH'],
            logger_name=file[1])
        handler.handle()
        log_names.append(log_file_name)

    archive = create_zip_archive_mem(log_names)
    archive_name = f'{cur_time}-results.zip'

    email_settings = app.config['EMAIL']
    to = copy.deepcopy(email_settings['BOSS_EMAIL_FOR_NOTIFY'])
    if email not in to:
        to.append(email)
    send_mail(
        user=email_settings['USER'],
        password=email_settings['PASSWORD'],
        send_to=to,
        subject='CERT-ECOSYSTEM - результаты загрузки XML-файла',
        text='Направляю результаты загрузки XML-файла',
        host=email_settings['HOST'],
        port=email_settings['PORT'],
        file_binary=archive,
        file_binary_name=archive_name)


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


@shared_task
def send_notify_email():
    """Отправляет email-письмо, содержащее реквизиты
    писем, исполнение которых не отражено в сервисе."""

    text = get_notify_text(get_unexecuted_messages())
    text = ('По состоянию на сегодняшний день в работе имеются следующие'
            ' письма, исполнение которых отсутствует в сервисе:\n') + text
    email_settings = app.config['EMAIL']
    send_mail(user=email_settings['USER'],
              password=email_settings['PASSWORD'],
              send_to=email_settings['BOSS_EMAIL_FOR_NOTIFY'],
              subject='CERT-ECOSYSTEM - Информация об'
                      ' имеющихся в работе неисполненных письмах',
              text=text,
              host=email_settings['HOST'],
              port=email_settings['PORT'])
