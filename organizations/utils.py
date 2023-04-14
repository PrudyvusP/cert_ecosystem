import os
import re
import smtplib
import uuid
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Tuple

from fpdf import FPDF
from pytils import translit
from sqlalchemy import func

from .exceptions import ModelAttributeError, SMTPAuthError


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
    "Возвращает строку с неразрывными пробелами вместо обычных."
    return re.sub(phrase, "\xa0".join(phrase.split()), strq)


def send_mail(user: str,
              password: str,
              send_to: list,
              subject: str,
              text: str,
              host: str,
              port: int,
              filename=None) -> None:
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
    with smtplib.SMTP(host, port) as server:
        try:
            server.login(user, password)
        except Exception:
            raise SMTPAuthError('')
        server.sendmail(user, send_to, message.as_string())
