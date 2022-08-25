import datetime
import re

import wtforms
from flask_wtf import FlaskForm
from wtforms.validators import (InputRequired, Optional,
                                ValidationError)

MESSAGE_DATE_TODAY_TEXT = "Дата подписи должна быть не позднее сегодня"
ORG_INN_NOT_CORRECT_TEXT = "Введите корректный ИНН"
ORG_OGRN_NOT_CORRECT_TEXT = "Введите корректный ОГРН"
INN_MAX_CONST = 9999999999999
INN_MIN_CONST = 1000000000000


def validate_future_date(form, field):
    """Проверяет дату на предмет ее адекватности относительно
    сегодняшнего дня."""
    if field.data and field.data > datetime.date.today():
        raise ValidationError(MESSAGE_DATE_TODAY_TEXT)


def validate_inn(form, field):
    """Проверяет строку на соответствие шаблону ИНН (10 или 12 цифр)."""
    pattern = r"^[\d+]{10,12}$"
    if not re.match(pattern, str(field.data)):
        raise ValidationError(ORG_INN_NOT_CORRECT_TEXT)


def validate_ogrn(form, field):
    """Проверяет строку на соответствие шаблону ОГРН (13 цифр)."""
    if field.data > INN_MAX_CONST or field.data < INN_MIN_CONST:
        raise ValidationError(ORG_OGRN_NOT_CORRECT_TEXT)


class CustomInputRequired(InputRequired):
    """Сообщение о необходимости заполнения поля формы."""

    def __init__(self):
        self.message = "Заполните поле"
        super(CustomInputRequired, self).__init__()


class BaseFormWithSubmit(FlaskForm):
    """Форма с кнопкой подтверждения действий."""

    submit = wtforms.SubmitField()


class AddSubjectDocumentForm(BaseFormWithSubmit):
    """Форма для учета документов организаций."""

    org_documents = wtforms.SelectField("Выберете тип документа:",
                                        choices=[],
                                        coerce=int,
                                        validators=[CustomInputRequired()])
    date_approved = wtforms.DateField("Дата подписи",
                                      validators=[CustomInputRequired(),
                                                  validate_future_date],
                                      format="%Y-%m-%d")
    props = wtforms.StringField("Реквизиты документа:",
                                validators=[Optional()],
                                render_kw={
                                    "placeholder": "Могут отстутствовать"}
                                )
    our_inbox_number = wtforms.StringField("Номер входящего письма",
                                           validators=[CustomInputRequired()])
    doc_file = wtforms.FileField('Образ документа',
                                 validators=[Optional()])
    organization_name = wtforms.StringField("Наименование организации:")
