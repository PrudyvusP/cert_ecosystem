import re
import uuid

from fpdf import FPDF
from pytils import translit
from sqlalchemy import func


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


def get_alpha_num_string(name: str) -> str:
    """Возвращает строку без лишних символов."""
    pattern = r'[^A-zА-яёЁ0-9]'
    return re.sub(pattern, '', name.lower())


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
