import datetime

from flask_wtf import FlaskForm
from wtforms import (DateField, FileField, MultipleFileField, RadioField,
                     SelectField, SelectMultipleField, StringField,
                     SubmitField, TextAreaField, widgets)
from wtforms.validators import (InputRequired, Optional, Regexp,
                                StopValidation, ValidationError)

from .views.forms_placeholders import message_fields_descriptions as mfd

MESSAGE_DATE_TODAY_TEXT = "Дата подписи должна быть не позднее сегодня"
EMAIL_NOT_CORRECT_TEXT = "Введите корректный email"
ORG_INN_NOT_CORRECT_TEXT = "Введите корректный ИНН"
ORG_OGRN_NOT_CORRECT_TEXT = "Введите корректный ОГРН"
ORG_KPP_NOT_CORRECT_TEXT = "Введите корректный КПП"

ATTACH_ORG_DOCUMENT_COMMENT_TEXTAREA_ROWS = 4

SEND_METHOD_DOC_FIO_REGEX_TEXT = 'Три слова кириллицы, разделенных пробелом'
SEND_METHOD_DOC_RECIPIENT_POSITION_TEXT = (
    'Руководителю Департамента заклинаний '
    'Министерства магии '
    'Российской Федерации')
SEND_METHOD_DOC_RECIPIENT_ADDRESS_TEXT = 'ул. Ясная, д. 39А, г. Москва, 125212'
SEND_METHOD_DOC_RECIPIENT_FIO_TEXT = 'Скайуокер Энакин Юрьевич'
SEND_METHOD_DOC_CHECKBOX_SIZE = 14

gender_choices = [('мужской', 'мужской'),
                  ('женский', 'женский')]

disk_type_choices = [('CD-R', 'CD-R'),
                     ('DVD-R', 'DVD-R')]

sender_choices = {
    'Генеральный директор': 'А.А. Рофлеров',
    'Исполнительный директор': 'М.М. Дирижабль',
    'Главный конструктор': 'Л.А. Самолётов'
}

sender_form_choices = [(k, v) for k, v in sender_choices.items()]

fio_regex = r'\w+\s\w+\s\w+'
without_symb_num_regex = r'[^№]+'
from_one_to_thousand_regex = r'[1-9]\d{0,3}$'
email_regex = r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)'


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MultiCheckboxAtLeastOne():
    def __init__(self, message=None):
        if not message:
            message = 'Выберете хотя бы один документ'
        self.message = message

    def __call__(self, form, field):
        if len(field.data) == 0:
            raise StopValidation(self.message)


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


def validate_email(form, field):
    """Проверяет почту на соответствие шаблону e-mail."""

    if '@' not in field.data:
        raise ValidationError(EMAIL_NOT_CORRECT_TEXT)


class CustomInputRequired(InputRequired):
    """Сообщение о необходимости заполнения поля формы."""

    def __init__(self):
        self.message = "Заполните поле"
        super(CustomInputRequired, self).__init__()


class BaseFormWithSubmit(FlaskForm):
    """Форма с кнопкой подтверждения действий."""

    submit = SubmitField()


class BaseMessageForm(FlaskForm):
    """Форма с реквизитами письма."""

    organization_name = StringField("Наименование организации",
                                    render_kw={"disabled": True})

    our_inbox_number = StringField(mfd['our_inbox_number'],
                                   validators=[Optional()],
                                   render_kw={
                                       "placeholder": "1111"})

    date_registered = DateField(mfd['date_registered'],
                                validators=[Optional(),
                                            validate_future_date]
                                )
    number_inbox_approved = StringField(mfd['number_inbox_approved'],
                                        validators=[Optional()],
                                        render_kw={
                                            "placeholder": "ЛПУ-16"})

    date_inbox_approved = DateField(mfd['date_inbox_approved'],
                                    validators=[Optional(),
                                                validate_future_date]
                                    )


class AddSubjectDocumentForm(BaseMessageForm, BaseFormWithSubmit):
    """Форма для учета документов организаций."""

    org_documents = SelectField("Выберете тип документа",
                                choices=[],
                                coerce=int,
                                validators=[CustomInputRequired()])
    date_approved = DateField("Дата подписи документа",
                              validators=[CustomInputRequired(),
                                          validate_future_date])
    props = StringField("Подписной номер документа",
                        validators=[Optional()],
                        render_kw={
                            "placeholder": "Может отсутствовать"}
                        )

    comment = TextAreaField(
        "Комментарий к документу",
        validators=[Optional()],
        render_kw={
            "placeholder": "Дополнительная информация",
            "rows": ATTACH_ORG_DOCUMENT_COMMENT_TEXTAREA_ROWS}
    )

    doc_file = FileField('Образ документа',
                         validators=[Optional()])


class SendMethodDocsToOrgForm(BaseMessageForm):
    """Форма для отправки методических документов в организацию."""

    org_address = StringField(
        'Адрес получателя',
        validators=[CustomInputRequired()],
        render_kw={"placeholder": SEND_METHOD_DOC_RECIPIENT_ADDRESS_TEXT}
    )
    recipient_position = StringField(
        'Должность получателя в дательном падеже (кому?/чему?)',
        validators=[CustomInputRequired()],
        render_kw={"placeholder": SEND_METHOD_DOC_RECIPIENT_POSITION_TEXT}
    )

    recipient_fio = StringField(
        'ФИО получателя в именительном падеже (кто?/что?)',
        validators=[CustomInputRequired(),
                    Regexp(
                        fio_regex,
                        message=SEND_METHOD_DOC_FIO_REGEX_TEXT)
                    ],
        render_kw={"placeholder": SEND_METHOD_DOC_RECIPIENT_FIO_TEXT}

    )

    recipient_gender = RadioField('Пол получателя',
                                  choices=gender_choices,
                                  default=gender_choices[0][0])

    disk = RadioField('Тип диска',
                      choices=disk_type_choices,
                      default=disk_type_choices[0][0])

    method_docs = MultiCheckboxField('Выберете методические документы',
                                     choices=[],
                                     coerce=int,
                                     validators=[MultiCheckboxAtLeastOne()],
                                     render_kw={
                                         "size": SEND_METHOD_DOC_CHECKBOX_SIZE
                                     }
                                     )
    sender = SelectField('Отправитель письма',
                         choices=sender_form_choices,
                         default=sender_form_choices[0][0])

    submit = SubmitField(render_kw={"disabled": True})


class AddXMLForm(BaseFormWithSubmit):
    """Форма для загрузки XML-файлов с зоной ответственности."""

    files = MultipleFileField('XML-файлы',
                              [InputRequired()])
    email = StringField('E-mail',
                        [InputRequired(),
                         Regexp(email_regex,
                                message='Введите корректный email')],
                        render_kw={
                            "placeholder": "rofel@mail.local"}
                        )
