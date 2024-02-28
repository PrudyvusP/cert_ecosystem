import json
import os
import re
import smtplib
import uuid
import zipfile
from datetime import datetime
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from pathlib import Path
from typing import List, Tuple

import requests
from flask import current_app as app
from fpdf import FPDF
from pytils import translit
from requests.exceptions import InvalidJSONError
from sqlalchemy import func

from .exceptions import (EgrulApiWrongFormatError, ModelAttributeError,
                         SMTPAuthError)

INN_PATTERN = re.compile(r'(?<!\d)\d{10}(?!\d)')
OGRN_PATTERN = re.compile(r'(?<!\d)\d{13}(?!\d)')
KPP_PATTERN = re.compile(r'(?<!\d)\d{9}(?!\d)')


def create_pdf(destination: str) -> None:
    """Сохраняет pdf-файл как признак
    конфиденциального документа организации."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    text = "This document is confidential"
    pdf.cell(200, 10, txt=text, ln=1, align='C')
    pdf.output(destination)


def create_prefix(strq: str) -> str:
    """Создает префикс из строки."""
    pattern = r'[\WУуЕеАаОоЭэЯяИиЮюЫы\']*'
    strq = re.sub(pattern, '', strq.lower())
    strq = translit.translify(strq[:18])
    return strq


def create_dot_pdf(name: str) -> str:
    """Добавляет расширение .pdf к строке."""
    return name + '.pdf'


def get_alpha_num_string(strq: str) -> str:
    """Возвращает строку без лишних символов."""
    pattern = r'[^A-zА-яёЁ0-9]'
    return re.sub(pattern, '', strq.lower())


def get_string_wo_special_symbols(strq: str) -> str:
    """Возврощает строку без специальных символов."""
    pattern = r'[?",.<>-«»|:\/]'
    return re.sub(pattern, '', strq)


def generate_uuid() -> str:
    """Возвращает строковое представление UUID."""
    return str(uuid.uuid4())


def get_quick_query_count(query) -> int:
    """Оптимальный способ получение количества
    строк в таблице."""
    count_q = query.statement.with_only_columns(
        [func.count()]
    ).order_by(None)
    count = query.session.execute(count_q).scalar()
    return count


def create_a_href_string(link: str, text: str) -> str:
    """Создает из переданных строк кликабельную ссылку."""
    return f"<a href={link}>{text}</a>"


def get_instance_choices(model,
                         _id: str = "id",
                         _name: str = "name",
                         _name_limiter: int = None,
                         ) -> List[Tuple[int, str]]:
    """Возвращает опции для html-элемента SelectField
    переданной в функцию модели."""
    try:
        _id = getattr(model, _id)
        _name = getattr(model, _name)
    except AttributeError:
        raise ModelAttributeError
    q = model.query.with_entities(_id, _name).order_by(_name).all()
    if not _name_limiter:
        return q
    return [(param[0], param[1][:_name_limiter]) for param in q]


def cast_string_to_non_breaking_space(strq: str,
                                      phrase: str) -> str:
    """Возвращает строку с неразрывными пробелами вместо обычных."""
    return re.sub(phrase, "\xa0".join(phrase.split()), strq)


def send_mail(user: str,
              password: str,
              send_to: list,
              subject: str,
              text: str,
              host: str,
              port: int,
              filename=None,
              file_binary=None,
              file_binary_name=None) -> None:
    """Отправляет электронное письмо в соответствии
    с полученными параметрами."""

    message = MIMEMultipart()
    message['From'] = user
    message['To'] = ', '.join(send_to)
    message['Subject'] = subject
    message.attach(MIMEText(text))
    if filename:
        suffix = Path(filename.filename).suffix
        base_file_name = os.path.basename(filename)
        with open(filename, 'rb') as f:
            attach = MIMEApplication(f.read(), _subtype=suffix)
            attach.add_header(
                'Content-Disposition',
                f'attachment; filename={base_file_name}'
            )
        message.attach(attach)
    if file_binary and file_binary_name:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(file_binary)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % file_binary_name)
        message.attach(part)
    with smtplib.SMTP(host, port) as server:
        try:
            server.login(user, password)
        except Exception:
            raise SMTPAuthError('')
        server.sendmail(user, send_to, message.as_string())


def get_api_url(url_to_go: str) -> str:
    """Создает относительный путь адреса EGRUL-сервиса."""
    base_api_url = app.config['BUSINESS_LOGIC']['EGRUL_SERVICE_URL']
    return base_api_url + url_to_go


def convert_from_json_to_dict(json_data: requests.models.Response) -> dict:
    """Конвертирует ответ из json в dict."""
    try:
        response = json_data.json()
    except json.JSONDecodeError:
        app.logger.error('Ошибка конвертации ответа от EGRUL API!')
        raise InvalidJSONError('Ошибка конвертации ответа от EGRUL API!')
    return response


def check_key_words_in_response(response, key_words):
    """Проверяет наличие ключевых слов в ответе."""

    for key_word in key_words:
        if key_word not in response:
            app.logger.error(
                f'отсутствует {key_word} в структуре ответа от API'
            )
            raise EgrulApiWrongFormatError(
                "В ответе не хватает ключевых слов")
    return response


def check_response(response: dict) -> list:
    """Возвращает список организаций."""

    if not isinstance(response, dict):
        raise TypeError("Должен быть словарь!")

    key_words = ["count", "next", "previous", "results", "date_info"]
    response = check_key_words_in_response(response, key_words=key_words)
    search_results = response["results"]
    if not isinstance(search_results, list):
        raise TypeError('Должен быть список!')
    return search_results


def check_retrieve_response(response: dict) -> dict:
    """Возвращает словарь организации."""

    if not isinstance(response, dict):
        raise TypeError("Должен быть словарь!")

    key_words = ["full_name", "short_name", "inn", "kpp", "ogrn",
                 "factual_address", "region_code"]
    response = check_key_words_in_response(response, key_words=key_words)
    return response


def get_cur_time() -> str:
    """Возвращает текущее время."""

    now = datetime.now()
    return now.strftime('%Y-%m-%d-%H:%M:%S')


def create_zip_archive_mem(files):
    """Возвращает архив в памяти."""

    memory_archive = BytesIO()

    with zipfile.ZipFile(memory_archive, 'a') as zf:
        for file in files:
            data = zipfile.ZipInfo(os.path.basename(file))
            data.compress_type = zipfile.ZIP_DEFLATED
            with open(file, "rb") as f:
                zf.writestr(data, f.read())
    memory_archive.seek(0)
    return memory_archive.getvalue()
