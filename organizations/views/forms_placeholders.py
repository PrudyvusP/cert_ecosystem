"""Словарь описания полей моделей и подсказок к ним."""
from flask_admin.contrib.sqla import ModelView

MESSAGE_IN_TEXT = '1234'
MESSAGE_INFO_PLACEHOLDER = ("Инициировали взаимодействие,"
                            " запросили Х, прислали Y\n"
                            "Контакт - Иванов Иван Иванович,"
                            " rofel@rofel.rofel")
MESSAGE_INFORMATION_ROWS_CONST = 10
MESSAGE_OUT_TEXT = 'ЛПУ-16'
MESSAGE_OUT_OUR_TEXT = '161-10-11/22'

ORG_ADDRESS_TEXT = "125212, г. Москва, Ленинградское шоссе, д. 23А"
ORG_AGRMNT_UNIT_TEXT = "Департамент физического развития"
ORG_BOSS_FIO_TEXT = "Ромашкин Игорь Евгеньевич"
ORG_BOSS_POS_TEXT = "Генеральный директор"
ORG_CONTACTS_ROWS_CONST = 6
ORG_CONTACTS_TEXT = ("Директор Департамента физического развития\nСпортивный "
                     "Рамзан Игнатьевич\nМоб. 8-800-555-35-35\nemail:"
                     " sport@with.us")
ORG_FULL_NAME_TEXT = "АКЦИОНЕРНОЕ ОБЩЕСТВО \"РОМАШКА\""
ORG_INN_TEXT = "7749000000"
ORG_KPP_TEXT = "123456789"
ORG_OGRN_TEXT = "1234567891234"
ORG_SHORT_NAME_TEXT = "АО \"РОМАШКА\""

RESOURCE_ADDRESS_ROWS_CONST = 8
RESOURCE_ADDRESSES_TEXT = ('Серверная часть:\n428038,'
                           ' Чувашская Республика, г. Чебоксары,'
                           ' ул. Победы, д. 3\n'
                           'Пользовательские АРМ:\n450112,'
                           ' Республика Башкортостан, г. Уфа, ул. Победы,'
                           ' д. 30;\n'
                           '630123, Новосибирская область, г. Новосибирск,'
                           ' ул. Победы, д. 28А')
RESOURCE_DNS_POOL_TEXT = "localhost, rofel.ru"
RESOURCE_IP_POOL_TEXT = "192.168.1.1:0/24, 127.0.0.1"
RESOURCE_NAME_TEXT = "ГАС \"Переправосудие\""
RESOURCE_RESP_WORKER_TEXT = "Рофлеров Р.Р., rofel@rofler.ru"


def get_beautiful_org_formatter(instance: ModelView) -> dict:
    """Возвращает сгруппированный по категориям
    словарь с данными об организации"""
    org_data = {
        'Основные реквизиты организации':
            [
                ('full_name', instance.column_labels['full_name']),
                ('short_name', instance.column_labels['short_name']),
                ('inn', instance.column_labels['inn']),
                ('kpp', instance.column_labels['kpp']),
                ('ogrn', instance.column_labels['ogrn'])
            ],
        'Адресная информация':
            [
                ('factual_address',
                 instance.column_labels['factual_address']),
                ('region', instance.column_labels['region'])
            ],
        'Руководство':
            [
                ('boss_position',
                 instance.column_labels['boss_position']),
                ('boss_fio', instance.column_labels['boss_fio'])
            ],
        'Контактные лица':
            [
                ('contacts', instance.column_labels['contacts'])
            ],
        'Соглашение о сотрудничестве':
            [
                ('date_agreement', instance.column_labels['date_agreement']),
                ('agreement_unit', instance.column_labels['agreement_unit'])
            ],
        'Характеристики':
            [
                ('is_gov', instance.column_labels['is_gov']),
                ('is_military', instance.column_labels['is_military']),
                ('is_subject_kii', instance.column_labels['is_subject_kii'])
            ],
        'Техническая информация':
            [
                ('uuid', 'UUID'),
                ('date_added', instance.column_labels['date_added']),
                ('date_updated', instance.column_labels['date_updated']),
            ],
    }
    return org_data


def get_beautiful_res_formatter(instance: ModelView) -> dict:
    res_data = {
        'Принадлежность к ОКИИ':
            [
                ('is_okii', instance.column_labels['is_okii']),
                ('fstec_reg_number',
                 instance.column_labels['fstec_reg_number']),
                ('category', instance.column_labels['category']),
                ('date_added_to_fstec',
                 instance.column_labels['date_added_to_fstec']),
                ('date_updated_to_fstec',
                 instance.column_labels['date_updated_to_fstec']),
                ('industries', instance.column_labels['industries']),
            ],
        'Географическая информация':
            [
                ('factual_addresses',
                 instance.column_labels['factual_addresses']),
                ('regions', instance.column_labels['regions']),
            ],
        'Техническая информация':
            [
                ('resp_worker', instance.column_labels['resp_worker']),
                ('ip_pool', instance.column_labels['ip_pool']),
                ('dns_pool', instance.column_labels['dns_pool']),
            ],
        'Владелец':
            [
                ('org_owner', instance.column_labels['org_owner']),
            ]
    }
    return res_data


organization_fields_descriptions = dict(
    full_name='Полное наименование организации',
    short_name='Сокращенное наименование организации',
    inn='Идентификационный номер налогоплательщика (организации)',
    kpp='Код причины постановки на учет (организации)',
    ogrn='Основной государственный регистрационный номер (организации)',
    factual_address='Адрес местонахождения (организации)',
    boss_position='Должность руководителя (организации)',
    boss_fio='Фамилия Имя Отчество руководителя (организации)',
    contacts='Контакты (ФИО, телефоны, электронные почты)',
    date_agreement='Дата заключения соглашения о сотрудничестве',
    agreement_unit='Главное подразделение'
                   ' в соответствии с соглашением о сотрудничестве',
    is_gov='Является ли организация государственной',
    is_military='Является ли организация военной',
    region='Регион, в котором зарегистрирована организация',
    is_subject_kii='Является ли организация субъектом КИИ',
    is_active='Статус организации (Существующая или ликвидирована)'
)

organization_fields_labels = dict(
    full_name='Полное наименование',
    short_name='Сокращенное наименование',
    inn='ИНН', ogrn='ОГРН', kpp='КПП',
    factual_address='Адрес местонахождения',
    boss_position='Должность руководителя',
    boss_fio='ФИО руководителя',
    contacts='Контакты',
    date_agreement='Дата подписания соглашения',
    agreement_unit='Главное подразделение',
    is_gov='ГОС', is_military='ВОЕН',
    db_name='Название организации', region='Регион',
    is_subject_kii='СКИИ',
    date_added='Дата внесения в БД',
    date_updated='Дата обновления сведений об организации в БД',
    is_active='АКТВ'
)

organization_fields_placeholders = dict(
    full_name={'placeholder': ORG_FULL_NAME_TEXT},
    short_name={'placeholder': ORG_SHORT_NAME_TEXT},
    inn={'placeholder': ORG_INN_TEXT},
    kpp={'placeholder': ORG_KPP_TEXT},
    ogrn={'placeholder': ORG_OGRN_TEXT},
    factual_address={'placeholder': ORG_ADDRESS_TEXT},
    boss_position={'placeholder': ORG_BOSS_POS_TEXT},
    boss_fio={'placeholder': ORG_BOSS_FIO_TEXT},
    contacts={'placeholder': ORG_CONTACTS_TEXT,
              'rows': ORG_CONTACTS_ROWS_CONST},
    agreement_unit={'placeholder': ORG_AGRMNT_UNIT_TEXT}
)

message_fields_descriptions = dict(
    date_inbox_approved='Дата подписи входящего письма',
    number_inbox_approved='Подписной номер входящего письма',
    date_registered='Дата регистрации входящего письма',
    our_inbox_number='Номер зарегистрированного входящего письма',
    date_approved='Дата подписи исходящего письма',
    our_outbox_number='Подписной номер исходящего письма',
    information='Краткое описание документа, контакты исполнителя и т.д.',
    datetime_created='Дата создания письма в базе',
    datetime_updated='Дата обновления письма в базе',
    is_outgoing='Письмо является исходящим?',
    organizations='Отправитель(-и) или получатель(-и) письма'
)

message_fields_labels = dict(
    date_inbox_approved='Дата подписи вх-го',
    number_inbox_approved='Подписной № вх-го',
    date_registered='Дата рег-ии вх-го',
    our_inbox_number='Наш № вх-го',
    date_approved='Дата подписи исх-го',
    our_outbox_number='Наш № исх-го',
    information='О чем',
    datetime_created='Дата создания письма в базе',
    datetime_updated='Дата обновления письма в базе',
    is_outgoing='Исх',
    organizations='Отправители/Получатели',
    parent='Основание',
    children='Исполнения')

message_fields_placeholders = dict(
    information={
        'rows': MESSAGE_INFORMATION_ROWS_CONST,
        'placeholder': MESSAGE_INFO_PLACEHOLDER
    },
    our_outbox_number={'placeholder': MESSAGE_OUT_OUR_TEXT,
                       'disabled': True},
    our_inbox_number={'placeholder': MESSAGE_IN_TEXT},
    number_inbox_approved={'placeholder': MESSAGE_OUT_TEXT}
)

resource_fields_labels = dict(
    is_okii='ОКИИ',
    fstec_reg_number='Рег №',
    name='Наименование',
    category='Категория',
    date_added_to_fstec='Дата внесения в реестр',
    date_updated_to_fstec='Дата обновления в реестре',
    date_added='Дата внесения в БД',
    date_updated='Дата обновления в БД',
    factual_addresses='Адреса размещения',
    resp_worker='Ответственный',
    is_active='АКТВ',
    ip_pool='IP-адреса',
    dns_pool='DNS-имена',
    org_owner='Владелец',
    industries='Сферы',
    regions='Регионы'
)

resource_fields_description = dict(
    is_okii='Является ли ресурс ОКИИ',
    fstec_reg_number='Регистрационный номер, присвоенный ФСТЭК России',
    name='Наименование ресурса',
    category='Категория значимости ОКИИ',
    date_added_to_fstec='Дата внесения информации об ОКИИ в реестр',
    date_updated_to_fstec='Дата обновления информации об ОКИИ в реестре',
    date_added='Дата внесения информации о ресурсе в БД',
    date_updated='Дата обновления информации о ресурсе в БД',
    factual_addresses='Адреса размещения ресурса (элементов ресурса)',
    resp_worker='Ответственная за ресурс персона (при наличии)',
    is_active='Является ли ресурс действующим',
    ip_pool='Диапазон IP-адресов ресурса (при наличии)',
    dns_pool='Диапазон доменных имен (при наличии)',
    org_owner='Владелец ресурса (организация)',
    industries='Сферы деятельности ОКИИ (по ФЗ-187)',
    regions='Регионы размещения элементов ресурса'
)

resource_fields_placeholders = dict(
    name={'placeholder': RESOURCE_NAME_TEXT},
    factual_addresses={
        'rows': RESOURCE_ADDRESS_ROWS_CONST,
        'placeholder': RESOURCE_ADDRESSES_TEXT
    },
    resp_worker={'placeholder': RESOURCE_RESP_WORKER_TEXT},
    ip_pool={'placeholder': RESOURCE_IP_POOL_TEXT},
    dns_pool={'placeholder': RESOURCE_DNS_POOL_TEXT}
)

orgadmdoc_fields_labels = dict(
    name="Название вида документа"
)

orgadmdoc_fields_descriptions = dict(
    name="Полное название вида организационно-распорядительного документа"
)

methoddoc_fields_labels = dict(
    name="Полное название",
    short_name="Сокращенное название",
    date_approved="Дата утверждения",
    props="Реквизиты",
    path_prefix="Служебное наименование",
    is_conf="Конфиденциальный?",
    is_active="Актуальный?",
    date_added="Дата добавления в БД",
    date_updated="Дата актуализации в БД"
)

methoddoc_fields_descriptions = dict(
    name="Полное название вида методического документа",
    short_name="Сокращенное название вида методического документа",
    date_approved="Дата утверждения методического документа",
    props="Реквизиты методического документа",
    path_prefix="Служебное наименование (для хранения в файловой структуре)",
    is_conf="Признак конфеднециальности документа",
    is_active="Признак актуальности документа",
    date_added="Дата внесение информации о документе в БД",
    date_updated="Дата актуализации информации о документе в БД"
)
