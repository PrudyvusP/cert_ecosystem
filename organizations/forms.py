import datetime
import re

import wtforms
from flask_wtf import FlaskForm
from wtforms.validators import (InputRequired, Optional,
                                ValidationError)

MESSAGE_DATE_TODAY_TEXT = "Дата подписи должна быть не позднее сегодня"
ORG_INN_NOT_CORRECT_TEXT = "Введите корректный ИНН"
ORG_OGRN_NOT_CORRECT_TEXT = "Введите корректный ОГРН"
ORG_KPP_NOT_CORRECT_TEXT = "Введите корректный КПП"


def validate_future_date(form, field):
    """Проверяет дату на предмет ее адекватности относительно
    сегодняшнего дня."""
    if field.data and field.data > datetime.date.today():
        raise ValidationError(MESSAGE_DATE_TODAY_TEXT)


def validate_inn(form, field):
    """Проверяет строку на соответствие шаблону ИНН (10 цифр)."""
    if len(field.data) != 10:
        raise ValidationError(ORG_INN_NOT_CORRECT_TEXT)


def validate_ogrn(form, field):
    """Проверяет строку на соответствие шаблону ОГРН (13 цифр)."""
    if len(field.data) != 13:
        raise ValidationError(ORG_OGRN_NOT_CORRECT_TEXT)


def validate_kpp(form, field):
    """Проверяет строку на соответствие шаблону КПП (9 цифр)."""
    if len(field.data) != 9:
        raise ValidationError(ORG_KPP_NOT_CORRECT_TEXT)


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

    organization_name = wtforms.StringField("Наименование организации:")

    org_documents = wtforms.SelectField("Выберете тип документа:",
                                        choices=[],
                                        coerce=int,
                                        validators=[CustomInputRequired()])
    date_approved = wtforms.DateField("Дата подписи документа",
                                      validators=[CustomInputRequired(),
                                                  validate_future_date],
                                      format="%Y-%m-%d")
    props = wtforms.StringField("Подписной номер документа:",
                                validators=[Optional()],
                                render_kw={
                                    "placeholder": "Может отсутствовать"}
                                )

    comment = wtforms.TextAreaField("Комментарий к документу:",
                                    validators=[Optional()],
                                    render_kw={
                                        "placeholder": "Дополнительная информация",
                                        "rows": 4}
                                    )

    doc_file = wtforms.FileField('Образ документа',
                                 validators=[Optional()])

    our_inbox_number = wtforms.StringField("Наш номер входящего письма:",
                                           validators=[CustomInputRequired()],
                                           render_kw={
                                               "placeholder": "1111"})

    date_registered = wtforms.DateField("Дата регистрации входящего письма:",
                                        validators=[CustomInputRequired(),
                                                    validate_future_date]
                                        )
    number_inbox_approved = wtforms.StringField("Подписной номер входящего письма:",
                                                validators=[CustomInputRequired()],
                                                render_kw={
                                                    "placeholder": "ЛПУ-16"})
    date_inbox_approved = wtforms.DateField("Дата подписи входящего письма:",
                                            validators=[CustomInputRequired(),
                                                        validate_future_date]
                                            )
