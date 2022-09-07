import datetime
import random

from data_storage.db_data import (org_data, resource_data, methodics_data,
                                  org_adm_doc_data, messages_data)
from organizations import create_app
from organizations.extentions import db
from organizations.models import (Organization, Resource, Responsibility,
                                  MethodicalDoc, Message, Region, OrgAdmDoc,
                                  Industry)


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
            inn=org.get("inn", '10000000000'),
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

    responsible_resource = db.session.query(Resource).get(1)

    new_resp = Responsibility(
        organization=resource_owner,
        resource=responsible_resource,
        date_start=datetime.datetime(2020, 5, 24),
        date_end=datetime.datetime(2022, 12, 12)
    )
    db.session.add(new_resp)

    lst_with_methods = []

    for method_doc in methodics_data:
        new_method_doc = MethodicalDoc(
            name=method_doc["name"],
            path_prefix=method_doc["path_prefix"],
            is_conf=method_doc["is_conf"],
            is_active=method_doc["is_active"]
        )
        db.session.add(new_method_doc)
        lst_with_methods.append(new_method_doc)

    message = Message(date_approved=datetime.datetime(2022, 1, 1),
                      our_outbox_number='1936',
                      information="Направлены рекомендации")

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
            information=message.get("information")
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
