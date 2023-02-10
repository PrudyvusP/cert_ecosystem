import re
import uuid
from typing import List, Tuple

from fpdf import FPDF
from pytils import translit
from sqlalchemy import func

from .exceptions import ModelAttributeError


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
    pattern = r'[?",.<>|:\/]'
    return re.sub(pattern, ' ', strq)


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
