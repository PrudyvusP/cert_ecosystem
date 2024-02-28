import datetime
import io
import random

from organizations import create_app
from organizations.extentions import db
from organizations.models import (Industry, Message, MethodicalDoc, OrgAdmDoc,
                                  Organization, Region, Resource)

"""Тестовые данные для демонстрации возможностей приложения."""

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
    },
    {
        "full_name": 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ДОМ ТЕСТОВ',
        "short_name": 'ООО "ДОМ ТЕСТОВ"',
        "is_gov": False,
        "is_military": False,
        "is_active": False,
        "ogrn": "1111111111111",
        "inn": "1111111111",
        "kpp": "111111111",
        "region": 77,
        "date_agreement": datetime.datetime(2022, 5, 5),
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
        "short_name": "Регламент антивзаимодейсвтия",
        "path_prefix": "regl_anti",
        "is_conf": False,
        "is_active": True,
        "name_for_letter": "Регламент антивзаимодейсвтия",
        "data_extension": '.txt',
        "data": io.BytesIO(b"We need more interaction")
    },
    {
        "name": "План создания планов создания в Российской Федерации",
        "short_name": "План создания планов",
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


def fill_demo_data() -> None:
    """Заполняет БД данными для демонстрации возможностей сервиса."""

    for org in org_data:
        new_org = Organization(
            full_name=org.get("full_name", 'ООО "ТЕСТ"'),
            short_name=org.get("short_name", 'ООО "ТЕСТ"'),
            is_gov=org.get("is_gov", False),
            is_military=org.get("is_military", False),
            is_active=org.get("is_active", True),
            ogrn=org.get("ogrn", '1000000000000'),
            inn=org.get("inn", '1000000000'),
            kpp=org.get("kpp", '123456789'),
            date_agreement=org.get("date_agreement"),
            agreement_unit=org.get("agreement_unit"),
            contacts=org.get("contacts"),
            region=Region.query.get(org.get("region", 77))
        )
        db.session.add(new_org)

    for resource in resource_data:
        resource_owner = (db.session.query(Organization)
                          .get(random.randint(1, 9))
                          )
        is_okii = resource.get("is_okii", False)
        res_industries = []
        res_regions = []
        if is_okii:
            for i in range(random.randint(1, 3)):
                res_industries.append(
                    db.session.query(Industry).get(random.randint(1, 13))
                )
        for i in range(random.randint(1, 4)):
            res_regions.append(
                db.session.query(Region).get(random.randint(1, 77))
            )
        new_resource = Resource(
            name=resource["name"],
            fstec_reg_number=resource.get("fstec_reg"),
            category=resource.get("category"),
            is_okii=is_okii,
            date_added_to_fstec=resource.get("date_added_to_fstec"),
            resp_worker=resource.get("resp_worker"),
            ip_pool=resource.get("ip_pool"),
            dns_pool=resource.get("dns_pool"),
            org_owner=resource_owner,
            industries=res_industries,
            regions=res_regions
        )
        db.session.add(new_resource)

    lst_with_methods = []

    for method_doc in methodics_data:
        new_method_doc = MethodicalDoc(
            name=method_doc["name"],
            short_name=method_doc["short_name"],
            name_for_letter=method_doc["name_for_letter"],
            path_prefix=method_doc["path_prefix"],
            is_conf=method_doc["is_conf"],
            is_active=method_doc["is_active"],
            data_extension=method_doc["data_extension"],
            data=method_doc.get("data").read()

        )
        db.session.add(new_method_doc)
        lst_with_methods.append(new_method_doc)

    message = Message(date_approved=datetime.datetime(2022, 1, 1),
                      our_outbox_number='1936',
                      information="О направлении методических документов",
                      is_inbox=False)

    db.session.add(message)

    for method in lst_with_methods:
        message.methodical_docs.append(method)

    message.organizations.append(resource_owner)

    for message in messages_data:
        random_id = random.randint(1, 7)
        receiver_sender = db.session.query(Organization).get(random_id)
        new_message = Message(
            date_inbox_approved=message.get("date_inbox_approved"),
            number_inbox_approved=message.get("number_inbox_approved"),
            date_registered=message.get("date_registered"),
            our_inbox_number=message.get("our_inbox_number"),
            date_approved=message.get("date_approved"),
            our_outbox_number=message.get("our_outbox_number"),
            information=message.get("information"),
            is_inbox=message.get("is_inbox", True)
        )
        db.session.add(new_message)
        new_message.organizations.append(receiver_sender)

    for doc in org_adm_doc_data:
        new_doc = OrgAdmDoc(name=doc["name"],
                            name_prefix=doc["name_prefix"])
        db.session.add(new_doc)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        fill_demo_data()
