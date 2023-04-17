"""Тестовые данные для демонстрации возможностей приложения."""

import datetime
import io

org_data = [
    {
        "full_name": 'ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ'
                     ' УНИТАРНОЕ ПРЕДПРИЯТЕ "ДВАДЦАТЬ ДВА ВОИНА"',
        "short_name": 'ФГУП "22 ВОИНА"',
        "is_gov": True,
        "is_military": True,
        "ogrn": "3622410887447",
        "inn": "1401377231",
        "kpp": "123456789",
        "region": 77,
        "date_agreement": datetime.datetime(2020, 1, 1),
        "contacts": "Начальник отдела\nОлегов О.О.,\nooo@ooo.ru",
        "agreement_unit": "Департамент магии и чудес"
    },
    {
        "full_name": 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ТИК-ТАК"',
        "short_name": 'ООО "ТИК-ТАК"',
        "is_gov": False,
        "is_military": False,
        "ogrn": "5794445676829",
        "inn": "4298649448",
        "kpp": "123356789",
        "region": 77,
        "date_agreement": datetime.datetime(2021, 1, 1),
        "contacts": "Начальник отдела\nТик-таков Т.Т.,\ntik@tak.ru",
        "agreement_unit": "Отдел импортозамещения"
    },
    {
        "full_name": 'ПРАВИТЕЛЬСТВО ТРОЯНСКОЙ ОБЛАСТИ',
        "short_name": 'ПРАВИТЕЛЬСТВО ТРОЯНСКОЙ ОБЛАСТИ',
        "is_gov": True,
        "is_military": False,
        "ogrn": "7606818427875",
        "inn": "4351715328",
        "kpp": "223456789",
        "region": 50,
        "contacts": "Троянский конь\ntrojan@troja.troja",
    },
    {
        "full_name": 'ФУТБОЛЬНЫЙ КЛУБ "ЛОКОМОТИВ-МОСКВА"',
        "short_name": 'ФК "ЛОКОМОТИВ"',
        "is_gov": False,
        "is_military": False,
        "ogrn": "2689941093029",
        "inn": "9271285151",
        "kpp": "323456789",
        "region": 5,
        "date_agreement": datetime.datetime(2019, 1, 1),
        "agreement_unit": "Штаб вратарей",
        "contacts": "Главный тренер\nСёмин Ю.П.,\nups@fclm.ru",
    },
    {
        "full_name": 'АКЦИОНЕРНОЕ ОБЩЕСТВО "ПИРОЖОК"',
        "short_name": 'АО "ПИРОЖОК"',
        "is_gov": False,
        "is_military": True,
        "ogrn": "8712084940549",
        "inn": "7278837449",
        "kpp": "423456789",
        "region": 21,
        "contacts": "Главный пекарь\nПоваров П.П.,\npovar@ravop",
    },
    {
        "full_name": 'ФЕДЕРАЛЬНОЕ КАЗЕНОЕ ПРЕДПРИЯТИЕ "РОФЛЫ В РОФЛАХ"',
        "short_name": 'ФКП "РИФЛЫ"',
        "is_gov": True,
        "is_military": False,
        "ogrn": "1615058931275",
        "inn": "7729672826",
        "kpp": "533456789",
        "region": 44,
        "contacts": "Вагнер Силва ди Соуза,\nvagner@cska.com",
    },
    {
        "full_name": 'ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО "ПОМОГИ КУШАКАМ"',
        "short_name": 'ПАО "ПК"',
        "is_gov": False,
        "is_military": False,
        "ogrn": "2260215146233",
        "inn": "5330740968",
        "kpp": "981456789",
        "region": 30,
        "date_agreement": datetime.datetime(2019, 5, 5),
        "agreement_unit": "Департамент по чипированию сфинксов",
        "contacts": "Доброволец\nШариков П.П.,\nsharik@dogheart.ru"
    },
    {
        "full_name": 'НЕКОММЕРЧЕСКАЯ ОРГАНИЗАЦИЯ "ТУНДРА"',
        "short_name": 'НО "ТУНДРА"',
        "is_gov": False,
        "is_military": False,
        "ogrn": "3259834499125",
        "inn": "8045231691",
        "kpp": "322456789",
        "region": 73,
        "contacts": "Главный егерь\nКолбаскина А.А.,\nshare@kolbaska.net"
    },
    {
        "full_name": 'ГРУППА КОМПАНИЙ "НИ ДАТЬ НИ ВЗЯТЬ"',
        "short_name": 'ГК "НДНВ"',
        "is_gov": True,
        "is_military": False,
        "ogrn": "7319811095635",
        "inn": "0645334852",
        "kpp": "772456789",
        "region": 3,
        "contacts": "Председатель\nУрожайкин Р.Р.,\nurojay@rojay.pl"
    },
    {
        "full_name": 'ООО "ЛИКВИДИРОВАНО"',
        "short_name": 'ООО "ЛИКВИДИРОВАНО"',
        "is_gov": False,
        "is_military": False,
        "is_active": False,
        "ogrn": "8064811036972",
        "inn": "5862554836",
        "kpp": "102456789",
        "region": 10,
        "contacts": "Ликвидатор\nСантехничкин Ч.У.,\nsan4@taro.uk"
    }
]

resource_data = [
    {
        "fstec_reg": "123456",
        "name": 'АСУ ТП Печеньем',
        "category": 3,
        "is_okii": True,
        "date_added_to_fstec": datetime.datetime(2020, 1, 1),
        "resp_worker": "Печенькин Олег Ахметович"
    },
    {
        "fstec_reg": "654321",
        "name": 'АСУ ТП Сушками',
        "category": 3,
        "is_okii": True,
        "date_added_to_fstec": datetime.datetime(2021, 1, 1),
        "resp_worker": "Сушкин Олег Ахметович"
    },
    {
        "name": 'Локалка',
        "ip_pool": "192.168.1.1:0/28",
        "dns_pool": "abc.localhost, cba.localhost",
        "resp_worker": "tigr@root"
    },
    {
        "fstec_reg": "894123",
        "name": 'АСУ ТП Шоколадками',
        "category": 2,
        "is_okii": True,
        "date_added_to_fstec": datetime.datetime(2022, 1, 1),
        "resp_worker": "Шоколадкин Олег Ахметович"
    },
    {
        "name": 'Официальный сайт пекарни',
        "dns_pool": "pe4ka.ya.ru",
    },
    {
        "fstec_reg": "114488",
        "name": 'АСУ ТП Пряниками',
        "category": 0,
        "is_okii": True,
        "date_added_to_fstec": datetime.datetime(2022, 1, 5),
        "resp_worker": "Пряничкин Бурмат Тандырович"
    },
    {
        "fstec_reg": "7",
        "name": 'АСУ ТП Халвой',
        "category": 1,
        "is_okii": True,
        "date_added_to_fstec": datetime.datetime(2022, 1, 10),
        "resp_worker": "Халва Халва Халва"
    },
    {
        "name": 'Тематический портал Ёжик',
        "resp_worker": "Колючий Ёж Ёжович"
    },
    {
        "name": 'Духовой шкаф Витязь-101110',
        "resp_worker": "Двоичный Код Фуркадович"
    },
    {
        "name": 'Стоматологическая система отрывания зубов',
        "ip_pool": "192.168.5.1:0/29",
        "dns_pool": "zdorov.rf",
        "resp_worker": "korenoy_zub@zdorov.rf"
    },
]

methodics_data = [
    {
        "name": ("Методические рекомендации по поеданию тонких"
                 " ломтиков картофеля"),
        "short_name": "Методические рекомендации по поеданию чипсов",
        "path_prefix": "mr_crisps",
        "is_conf": True,
        "is_active": True,
        "name_for_letter": "Методические рекомендации по поеданию чипсов",
        "data_extension": '.txt',
        "data": io.BytesIO(b"Open chips and eat them")

    },
    {
        "name": "Регламент антивзаимодействия подразделений земли и воды",
        "short_name":"Регламент антивзаимодейсвтия",
        "path_prefix": "regl_anti",
        "is_conf": False,
        "is_active": True,
        "name_for_letter": "Регламент антивзаимодейсвтия",
        "data_extension": '.txt',
        "data": io.BytesIO(b"We need more interaction")
    },
    {
        "name": "План создания планов создания в Российской Федерации",
        "short_name":"План создания планов",
        "path_prefix": "plan_planov",
        "is_conf": True,
        "is_active": True,
        "name_for_letter": "План создания планов",
        "data_extension": '.txt',
        "data": io.BytesIO(b"We need more plans of plans")
    }
]

org_adm_doc_data = [
    {
        "name": "Соглашение о соглашении с соглашением",
        "name_prefix": "test_prefix1"
    },
    {
        "name": "Методические рекомендации по созданию пирожков",
        "name_prefix": "test_prefix2"
    },
    {
        "name": "Регламент взаимодействия земли и воды",
        "name_prefix": "test_prefix3"
    },
    {
        "name": "Порядок реагирования на повышение в должности",
        "name_prefix": "test_prefix4"
    },
]

messages_data = [
    {
        "date_inbox_approved": datetime.datetime(2022, 4, 22),
        "number_inbox_approved": 'ППА-11.144',
        "date_registered": datetime.datetime(2022, 4, 23),
        "our_inbox_number": '1А',
        "information": ('Назначено рабочее совещание, '
                        'необходимо прибыть в гавайской рубашке'
                        ' в Лапландию')
    },
    {
        "date_inbox_approved": datetime.datetime(2022, 3, 11),
        "number_inbox_approved": '48-хрн',
        "date_registered": datetime.datetime(2022, 3, 28),
        "our_inbox_number": '9Б',
        "information": ('Направлен отчет по учету отчета '
                        'в отчете на справку о справке')
    },
    {
        "date_inbox_approved": datetime.datetime(2022, 2, 14),
        "number_inbox_approved": '<3_322',
        "date_registered": datetime.datetime(2022, 2, 17),
        "our_inbox_number": '14Ф',
        "information": ('Поздравления\nс\nднем\nСвятого\n'
                        'Валентина\n')
    },
    {
        "date_inbox_approved": datetime.datetime(2022, 4, 25),
        "number_inbox_approved": 'ЖЖ-11-ЖЖ',
        "date_registered": datetime.datetime(2022, 4, 30),
        "our_inbox_number": '1Ж',
        "information": ('Запрос коммерческого предложения '
                        'на покупку фибронабрызгбетона')
    },
    {
        "date_approved": datetime.datetime(2022, 4, 25),
        "our_outbox_number": '11',
        "information": 'Направлен чек за покупку 10 кг огурцов',
        "is_inbox": False
    },
    {
        "date_approved": datetime.datetime(2022, 2, 1),
        "our_outbox_number": '1',
        "information": f'Текст сообщения: {"тест " * 35}',
        "is_inbox": False
    },
    {
        "date_approved": datetime.datetime(2022, 5, 1),
        "our_outbox_number": '17',
        "information": ('Я мог бы выпить море, я мог бы стать другим '
                        'вечно молодым, вечно пьяным'),
        "is_inbox": False
    },
]
