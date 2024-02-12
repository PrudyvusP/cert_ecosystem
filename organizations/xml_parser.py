import datetime
import re
from typing import Optional

import requests
from lxml import etree

from organizations.extentions import db
from organizations.models import (Cert, Contact, Region, Resource,
                                  Organization)
from organizations.utils import (check_response, check_retrieve_response,
                                 convert_from_json_to_dict,
                                 get_api_url)


class XMLValidator:

    @staticmethod
    def get_xml_root(file):
        """Возвращает древо элементов XML-файла."""

        return etree.parse(file)

    @staticmethod
    def get_schema_root(schema):
        """Возвращает древо элементов XSD-схемы."""

        schema_root = etree.parse(schema)
        return etree.XMLSchema(schema_root)

    @staticmethod
    def check_xml_syntax(file) -> dict:
        """Возвращает результат проверки синтаксиса XML."""

        try:
            etree.parse(file)
        except IOError as e:
            return {
                "status": "error",
                "message": "Ошибка файловой системы",
                "log": str(e)}
        except etree.XMLSyntaxError as e:
            return {
                "status": "error",
                "message": "Ошибка синтаксиса XML",
                "log": str(e)}
        return {
            "status": "ok",
            "message": "Синтаксис XML ок",
            "log": ""}

    def check_xml_schema(self, schema, file) -> dict:
        """Возвращает результат соответствия XML схеме."""

        schema = self.get_schema_root(schema)
        xml = self.get_xml_root(file)

        xml_ok = schema.validate(xml)
        if xml_ok:
            return {
                "status": "ok",
                "message": "XML соответствует схеме",
                "log": ""}
        return {
            "status": "error",
            "message": "Ошибка соответствия XML",
            "log": str(schema.error_log)}

    def validate(self, schema, file):
        if (self.check_xml_syntax(file).get('status') == 'ok' and
                self.check_xml_schema(schema, file).get('status') == 'ok'):
            return True
        return False


class XMLParser:
    def __init__(self, schema, file, validator=XMLValidator()):
        self.schema = schema
        self.file = file
        self.validator = validator

    def get_xml_root(self):
        """Возвращает древо элементов XML-файла."""

        return etree.parse(self.file)

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

    @staticmethod
    def parse_address(tag) -> dict:
        """Возвращает словарь гео данных из XML-элемента <tag>."""

        region_code = tag.find('КодРегион').text
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
        return {
            'region_code': region_code,
            'address': re.sub(r';', ',', address)
        }

    @staticmethod
    def parse_contact(tag) -> dict:
        """Возвращает словарь контактов из XML-элемента <tag>."""

        fio = tag.find('ФИО').text
        dep = None
        if tag.find('Подразд') is not None:
            dep = tag.find('Подразд').text
        pos = None
        if tag.find('Должн') is not None:
            pos = tag.find('Должн').text
        mob_phone = None
        if tag.find('МобТел') is not None:
            mob_phone = tag.find('МобТел').text
        work_phone = tag.find('РабТел').text
        email = tag.find('ЭлПоч').text

        return {
            "fio": fio,
            "dep": dep,
            "pos": pos,
            "mob_phone": mob_phone,
            "work_phone": work_phone,
            "email": email
        }

    def create_contacts(self, root, tag, org) -> list:
        """Возвращает список объектов типа Contact."""

        center_contacts = []
        for contact in root.findall(tag):
            cur_contact = self.parse_contact(contact)
            center_contacts.append(Contact(org_id=org, **cur_contact))
        return center_contacts

    @staticmethod
    def get_org_from_db(inn: str,
                        kpp: str,
                        ogrn: str) -> Optional[Organization]:
        """Возвращает из БД организацию по переданным ИНН, КПП, ОГРН. """
        return (db.session
                .query(Organization)
                .filter(Organization.inn == inn,
                        Organization.kpp == kpp,
                        Organization.ogrn == ogrn)
                .first())

    @staticmethod
    def get_from_db_or_create_cert(name: str, owner: int) -> Cert:
        """Возвращает Центр мониторинга из БД или создает его."""

        cert = (
            db.session
            .query(Cert)
            .filter(Cert.name == name, Cert.org_owner == owner)
            .first()
        )
        if cert:
            return cert
        return Cert(name=name, org_owner=owner)

    @staticmethod
    def get_org_from_egrul(inn: str) -> Optional[Organization]:
        """Возвращает объект организации из ЕГРЮЛ API или None."""

        url = get_api_url('api/organizations/')
        params = {"inn": inn, "is_main": True}

        try:
            _request = requests.get(url, params=params)

        except requests.exceptions.RequestException:

            # TODO EGRUL nedostupen, write to log
            return None

        response = convert_from_json_to_dict(_request)
        if response:
            orgs = check_response(response)
            if orgs:

                url = get_api_url(orgs[0]['relative_addr'].lstrip('/'))

                try:
                    _request = requests.get(url)

                except requests.exceptions.RequestException:

                    # TODO EGRUL nedostupen, write to log
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
            return org
        org_from_egrul = self.get_org_from_egrul(inn=inn)
        if org_from_egrul:
            return org_from_egrul
        return None

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

    def parse(self):
        if not self.validator.validate(self.schema, self.file):
            return 'ERROR'
        tree = self.get_xml_root()
        root = tree.getroot()
        center_info = root.attrib
        date_form = datetime.date.fromisoformat(center_info['ДатаФорм'])
        center_name = center_info['НаимЦентр']
        center_klass = center_info['КлассЦентр']

        owner_info = self.get_org_issues(root.find('СвЮЛ'))

        owner = self.get_org_from_db(
            inn=owner_info['inn'],
            kpp=owner_info['kpp'],
            ogrn=owner_info['ogrn']
        )

        if not owner:
            # TODO log
            # TODO выход
            pass

        if not owner.date_agreement:
            # TODO log
            # TODO выход
            pass

        center_address_info = self.parse_address(root.find('СвЦентрАдр'))
        center_mailing_address = center_address_info['address']
        owner.mailing_address = center_mailing_address

        owner.com_contacts.delete()

        center_contacts = self.create_contacts(
            root=root, tag='СвЦентрКонт', org=owner)
        owner.com_contacts = center_contacts

        db.session.add(owner)

        cert = self.get_from_db_or_create_cert(center_name, owner)
        cert.date_actual_resp, cert.type = date_form, center_klass
        db.session.add(cert)

        zone_root = root.find('СвЗонаОтв')
        if zone_root.find('ЕдЗО') is None:
            # TODO log
            # TODO сохранить данные
            # TODO выход
            return -1

        zones = zone_root.findall('ЕдЗО')

        for zone in zones:
            zone_org_from_xml = self.get_org_issues(zone.find('СвЗОЮЛ'))
            org_inn, org_kpp, org_ogrn, org_name = zone_org_from_xml.values()
            zone_org = self.find_org_from_db_or_egrul(
                inn=org_inn,
                kpp=org_kpp,
                ogrn=org_ogrn)

            if not zone_org:
                # TODO пишем лог, что организация не найдена и идем дальше
                continue

            org_contacts = self.create_contacts(
                root=zone, tag='СвЗОКонтЮЛ', org=zone_org)

            if zone_org == owner:
                owner.com_contacts.extend(org_contacts)
            else:
                zone_org.com_contacts.delete()
                zone_org.com_contacts = org_contacts

            resources = zone.find('СвЗООбктЮЛ')
            res_roots = resources.findall('СвОбкт')
            # Ошибка схемы СвОбкт должен быть мин 1
            if res_roots is None:
                pass
                # TODO лог
                # TODO сохраняем данные
                # TODO выход
            for res_root in res_roots:
                res_name = res_root.attrib['Наим']
                #res_db = db.session.query(Resource).filter(
                #    Resource.name == res_name)

                kii_info = self.parse_kii(res_root.find('СвКИИ'))

                print(kii_info)
                res_formatted_address = []
                res_addresses = res_root.findall('СвАдрРазм/АдрРазмОбкт')
                for res_address in res_addresses:
                    res_address_info = self.parse_address(res_address)
                    res_formatted_address.append(res_address_info['address'])
                res_formatted_address = "; ".join(res_formatted_address)

                cur_res = Resource(**kii_info,
                                   factual_addresses=res_formatted_address,
                                   name=res_name,
                                   org_owner=zone_org)

                print(cur_res)
        db.session.commit()

        return -1
