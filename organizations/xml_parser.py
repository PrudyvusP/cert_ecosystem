import datetime
import logging
from typing import Optional

import requests
from lxml import etree

from organizations.extentions import db
from organizations.models import (Cert, Contact, Region, Resource,
                                  Responsibility, Organization, Service)
from organizations.utils import (check_response, check_retrieve_response,
                                 convert_from_json_to_dict,
                                 get_api_url)


class XMLValidator:
    def __init__(self, schema, file, logger) -> None:
        self.schema = schema
        self.file = file
        self.logger = logging.getLogger(logger)

    def get_xml_root(self):
        """Возвращает древо элементов XML-файла."""

        return etree.parse(self.file)

    def get_schema_root(self):
        """Возвращает древо элементов XSD-схемы."""

        schema_root = etree.parse(self.schema)
        return etree.XMLSchema(schema_root)

    def check_xml_syntax(self) -> bool:
        """Возвращает результат проверки синтаксиса XML."""

        try:
            etree.parse(self.file)
        except IOError as e:
            self.logger.error(f'Ошибка файловой системы {str(e)}')
            return False
        except etree.XMLSyntaxError as e:
            self.logger.error(f'Ошибка синтаксиса XML {str(e)}')
            return False
        self.logger.info('Синтаксис XML ок')
        return True

    def check_xml_schema(self) -> bool:
        """Возвращает результат соответствия XML схеме."""

        schema = self.get_schema_root()
        xml = self.get_xml_root()

        xml_ok = schema.validate(xml)
        if xml_ok:
            self.logger.info('XML соответствует схеме')
            return True
        self.logger.error('Ошибка соответствия XML-файла XSD-схеме')
        for error in schema.error_log:
            self.logger.error(f'Строка: {error.line}. Ошибка: {error.message}')
        return False

    def validate(self) -> bool:
        """Возвращает результат валидации XML-файла."""

        if self.check_xml_syntax() and self.check_xml_schema():
            self.logger.info('Валидация XML успешно завершена')
            return True
        self.logger.error('Ошибка валидации XML файла. Выход')
        return False


class XMLParser:

    def __init__(self, schema, file, logger) -> None:
        self.schema = schema
        self.file = file
        self.regions = self.get_regions()
        self.logger = logging.getLogger(logger)

    def get_xml_root(self):
        """Возвращает древо элементов XML-файла."""

        return etree.parse(self.file)

    @staticmethod
    def get_regions():
        # session.scalars(query).all()
        return [code for code, in db.session.query(Region.region_id).all()]

    @staticmethod
    def get_org_issues(tag) -> dict:
        """Возвращает словарь организации из переданного XML-элемента <tag>."""

        owner_info = tag.attrib
        return {
            'inn': owner_info['ИНН'],
            'kpp': owner_info['КПП'],
            'ogrn': owner_info['ОГРН'],
            'full_name': owner_info['НаимЮЛПолн']
        }

    def parse_address(self, tag) -> dict:
        """Возвращает словарь гео данных из XML-элемента <tag>."""

        self.logger.info(f'Запускаю парсер адреса тега <{tag.tag}>')

        region_code = tag.find('КодРегион').text

        if int(region_code) not in self.regions:
            self.logger.warning(f'Код региона {region_code} не найден в БД. '
                                f'Присваиваю код региона = 99')
            region_code = '99'

        region_name = tag.find('НаимРегион').text
        address = tag.find('Адрес').text
        index = ''
        city_name = ''
        if tag.find('Индекс') is not None:
            index = ', ' + tag.find('Индекс').text
        if tag.find('НаимГор') is not None:
            city_name = tag.find('НаимГор').text
            city_name_lower = city_name.lower()
            if (
                    'москва' in city_name_lower
                    or 'санкт-петербург' in city_name_lower
                    or 'севастополь' in city_name_lower):
                city_name = ''
            else:
                city_name += ', '
        address = f'{address}, {city_name}{region_name}{index}'
        self.logger.info(f'Адрес {address} успешно обработан')
        self.logger.info(f'Код региона {region_code} успешно обработан')
        return {
            'region_code': region_code,
            'address': address.replace(';', ',')
        }

    @staticmethod
    def parse_contact(root) -> dict:
        """Возвращает словарь контактов из XML-элемента <root>."""

        fio = root.find('ФИО').text
        dep = None
        if root.find('Подразд') is not None:
            dep = root.find('Подразд').text
        pos = None
        if root.find('Должн') is not None:
            pos = root.find('Должн').text
        mob_phone = None
        if root.find('МобТел') is not None:
            mob_phone = root.find('МобТел').text
        work_phone = root.find('РабТел').text
        email = None
        if root.find('ЭлПоч') is not None:
            email = root.find('ЭлПоч').text

        return {
            "fio": fio,
            "dep": dep,
            "pos": pos,
            "mob_phone": mob_phone,
            "work_phone": work_phone,
            "email": email
        }

    def parse_document(self, root) -> dict:
        """Возвращает словарь документов из XML-элемента <root>."""

        self.logger.info('Обрабатываю реквизиты документа')
        date_start = datetime.date.fromisoformat(root.find('ДатаСтарт').text)
        date_end = datetime.date.fromisoformat(root.find('ДатаФиниш').text)
        if date_end <= date_start:
            self.logger.error(f'Дата окончания документа {date_end} меньше, '
                              f'чем дата начала действия {date_start}')
        comment = None
        if root.find('Ком') is not None:
            comment = root.find('Ком').text

        return {
            "type": root.find('Наим').text,
            "props": root.find('Рекв').text,
            "date_start": date_start,
            "date_end": date_end,
            "comment": comment
        }

    def create_contacts(self, root, tag, org) -> list:
        """Возвращает список объектов типа Contact."""

        self.logger.info(f'Запускаю парсер тега с контактами <{tag}>')

        center_contacts = []
        for contact in root.findall(tag):
            cur_contact = self.parse_contact(contact)
            center_contacts.append(Contact(org_id=org, **cur_contact))

        self.logger.info(f'Найдено контактов: {len(center_contacts)}')
        return center_contacts

    def get_org_from_db(self,
                        inn: str,
                        kpp: str,
                        ogrn: str) -> Optional[Organization]:
        """Возвращает из БД организацию по переданным ИНН, КПП, ОГРН."""

        self.logger.info(f'Ищу юридическое лицо (ИНН {inn}) в БД')
        return (db.session
                .query(Organization)
                .filter(Organization.inn == inn,
                        Organization.kpp == kpp,
                        Organization.ogrn == ogrn)
                .first())

    def get_instance_from_db_or_create(self, model, **kwargs):
        """Возвращает сущность из БД или создает ее."""
        name = kwargs.get('name')

        self.logger.info(f'Ищу {model.__name__} {name} в БД')

        instance = (
            db.session
            .query(model)
            .filter_by(**kwargs)
            .first()
        )
        if instance:
            self.logger.info(f'{model.__name__} {name} найден в БД')
            return instance
        self.logger.info(f'{model.__name__} {name} не найден в БД')
        self.logger.info(f'Создаю сущность {model.__name__} {name}')
        return model(**kwargs)

    def get_org_from_egrul(self, inn: str) -> Optional[Organization]:
        """Возвращает объект организации из ЕГРЮЛ API или None."""

        self.logger.info(f'Ищу юр. лицо (ИНН {inn}) в ЕГРЮЛ')

        url = get_api_url('api/organizations/')
        params = {"inn": inn, "is_main": True}

        try:
            self.logger.info(f'Отправляю поисковый запрос на {url} с '
                             f'параметрами {params}')
            _request = requests.get(url, params=params)

        except requests.exceptions.RequestException:
            self.logger.warning('ЕГРЮЛ недоступен')
            return None

        response = convert_from_json_to_dict(_request)
        if response:
            orgs = check_response(response)
            if orgs:

                url = get_api_url(orgs[0]['relative_addr'].lstrip('/'))

                try:
                    _request = requests.get(url)

                except requests.exceptions.RequestException:
                    self.logger.warning('ЕГРЮЛ недоступен')
                    return None

                response = convert_from_json_to_dict(_request)
                response = check_retrieve_response(response)

                new_org = Organization(
                    inn=response['inn'],
                    kpp=response['kpp'],
                    ogrn=response['ogrn'],
                    full_name=response['full_name'],
                    short_name=response.get("short_name") or response[
                        "full_name"],
                    factual_address=response['factual_address'],
                    region=db.session.query(Region).get(
                        response['region_code'])
                )
                return new_org

        return None

    def find_org_from_db_or_egrul(
            self,
            inn: str,
            ogrn: str,
            kpp: str) -> Optional[Organization]:
        """Возвращает организацию либо из БД, либо из ЕГРЮЛ."""

        org = self.get_org_from_db(inn=inn,
                                   ogrn=ogrn,
                                   kpp=kpp)
        if org:
            self.logger.info(f'Юр. лицо (ИНН {inn}) обнаружено в БД ')
            return org

        self.logger.info(f'Не удалось найти юр. лицо (ИНН {inn}) в БД ')

        org_from_egrul = self.get_org_from_egrul(inn=inn)
        if org_from_egrul:
            return org_from_egrul
        self.logger.info(f'Не удалось найти юр. лицо (ИНН {inn}) в ЕГРЮЛ ')
        return None

    @staticmethod
    def get_regions_from_xml(region_codes: list) -> list:
        """Возвращает список объектов типа Region."""

        regions = []
        for region_code in region_codes:
            cur_region = db.session.query(Region).get(region_code)
            if cur_region:
                regions.append(cur_region)
        return regions

    def get_services_from_xml(self, services) -> list:
        """Возвращает список объектов типа Service."""

        new_services = []
        for service in services:
            cur_service = db.session.query(Service).filter(
                Service.name == service.text).first()
            if cur_service:
                new_services.append(cur_service)

        self.logger.info(f'Найдено услуг: {len(new_services)}')
        return new_services

    @staticmethod
    def parse_kii(tag) -> dict:
        """Возвращает словарь с реквизитами КИИ."""

        fstec_reg_number = None
        category = None
        is_okii = False
        if tag is not None:
            if tag.find('РегНом') is not None:
                is_okii = True
                fstec_reg_number = tag.find('РегНом').text
            if tag.find('КатЗнач') is not None:
                is_okii = True
                category = tag.find('КатЗнач').text
        return {
            "fstec_reg_number": fstec_reg_number,
            "category": category,
            "is_okii": is_okii
        }

    def parse(self) -> bool:
        """Основной метод класса. Парсит XML-файл."""

        tree = self.get_xml_root()
        root = tree.getroot()
        cent_info = root.attrib
        date_form = datetime.date.fromisoformat(cent_info['ДатаФорм'])
        cent_name, cent_klass = cent_info['НаимЦентр'], cent_info['КлассЦентр']
        self.logger.info(f'Начинаю работу с файлом центра {cent_name}')
        owner_org = self.get_org_issues(root.find('СвЮЛ'))
        owner = self.get_org_from_db(
            inn=owner_org['inn'], kpp=owner_org['kpp'], ogrn=owner_org['ogrn'])

        if not owner:
            self.logger.error(f'Юр. лицо центра не найдено. Выход')
            return False

        if not owner.date_agreement:
            self.logger.error(f'У юр. лица центра отсутствует соглашение. '
                              f'Выход')
            return False

        cent_address_info = self.parse_address(root.find('СвЦентрАдр'))
        cent_mailing_address = cent_address_info['address']
        owner.mailing_address = cent_mailing_address
        owner.com_contacts.delete()
        cent_contacts = self.create_contacts(root=root, tag='СвЦентрКонт',
                                             org=owner)
        owner.com_contacts = cent_contacts
        db.session.add(owner)
        cert = self.get_instance_from_db_or_create(
            Cert, name=cent_name, org_owner=owner)
        cert.date_actual_resp, cert.type = date_form, cent_klass
        db.session.add(cert)

        zone_root = root.find('СвЗонаОтв')
        if zone_root.find('ЕдЗО') is None:
            self.logger.info('Зона ответственности отсутствует. Штатный выход')
            db.session.commit()
            return True

        zones = zone_root.findall('ЕдЗО')
        self.logger.info('Начинаю парсинг тега <ЕдЗО>')
        for zone in zones:
            zone_org_from_xml = self.get_org_issues(zone.find('СвЗОЮЛ'))
            org_inn, org_kpp, org_ogrn, org_name = zone_org_from_xml.values()
            zone_org = self.find_org_from_db_or_egrul(
                inn=org_inn,
                kpp=org_kpp,
                ogrn=org_ogrn)

            if not zone_org:
                self.logger.error(
                    f'Не удалось найти юр. лицо {org_name} (ИНН/КПП {org_inn}'
                    f'/{org_kpp}). Перехожу к следующему тегу <ЕдЗО>')
                continue

            org_contacts = self.create_contacts(
                root=zone, tag='СвЗОКонтЮЛ', org=zone_org)

            if zone_org == owner:
                owner.com_contacts.extend(org_contacts)
            else:
                zone_org.com_contacts.delete()
                zone_org.com_contacts = org_contacts

            self.logger.info('Начинаю парсинг ресурсов')

            resources = zone.find('СвЗООбктЮЛ')
            res_roots = resources.findall('СвОбкт')

            # Ошибка схемы СвОбкт должен быть мин 1
            if res_roots is None:
                self.logger.error('Тег <СвОбкт> пустой. Перехожу к следующему '
                                  'тегу <ЕдЗО>')
                continue

            for res_root in res_roots:
                res_name = res_root.attrib['Наим']
                kii_info = self.parse_kii(res_root.find('СвКИИ'))

                res_formatted_address = []
                res_codes = []
                res_addresses = res_root.findall('СвАдрРазм/АдрРазмОбкт')
                for res_address in res_addresses:
                    res_address_info = self.parse_address(res_address)
                    res_formatted_address.append(res_address_info['address'])
                    res_codes.append(res_address_info['region_code'])
                res_formatted_address = "; ".join(res_formatted_address)
                res_fstec_reg_number = kii_info['fstec_reg_number']
                res_category = kii_info['category']
                res_is_okii = kii_info['is_okii']

                res = self.get_instance_from_db_or_create(
                    Resource, name=res_name, org_owner=zone_org,
                    factual_addresses=res_formatted_address,
                    fstec_reg_number=res_fstec_reg_number,
                    category=res_category,
                    is_okii=res_is_okii)

                res.regions = self.get_regions_from_xml(region_codes=res_codes)
                db.session.add(res)
                self.logger.info(f'Ресурс {res_name} успешно обработан')

                doc_info = self.parse_document(res_root.find('СвДокумент'))
                self.logger.info('Реквизиты документа успешно обработаны')
                type, props, date_start, date_end, comment, = doc_info.values()

                self.logger.info('Ищу в БД единицу зоны ответственности')
                resp_exists = (
                    db.session
                    .query(Responsibility)
                    .filter(Responsibility.date_start == date_start,
                            Responsibility.date_end == date_end,
                            Responsibility.resource_id == res.resource_id,
                            Responsibility.cert == cert)
                    .first()
                )

                if not resp_exists:
                    self.logger.info('В БД отсутствует информация о зоне '
                                     'ответственности. Создаю новую единицу')
                    new_resp = Responsibility(**doc_info,
                                              resource_id=res.resource_id,
                                              cert=cert)
                    db.session.add(new_resp)

                    self.logger.info('Начинаю парсинг функций (услуг)')
                    services = self.get_services_from_xml(
                        res_root.findall('СвФункции/Функция'))
                    new_resp.services = services
                    db.session.add(new_resp)
                else:
                    self.logger.warning('Единица зоны ответственности уже '
                                        'имеется в БД. Пропускаю')
        self.logger.info('Начинаю выполнение транзакции в БД')
        db.session.commit()
        self.logger.info('Транзакция выполнилась. Выход')
        return True


class XMLHandler:
    def __init__(self, file, schema, logger_name, logger_file) -> None:
        self.file = file
        self.schema = schema
        self.logger_name = logger_name
        self.logger_file = logger_file
        self.log_level = logging.INFO

    def handle(self) -> bool:
        """Основной метод класса. Возвращает результат обработки."""

        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.log_level)
        fh = logging.FileHandler(self.logger_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(funcName)s() - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        validator = XMLValidator(self.schema, self.file, self.logger_name)
        if not validator.validate():
            return False
        parser = XMLParser(self.schema, self.file, self.logger_name)
        if parser.parse():
            return True
        return False
