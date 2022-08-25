from dbfread import DBF

from .extentions import db
from .models import Region, Address


def cast_reg_pochta_to_constitute(region_name: str) -> str:
    """Преобразует название региона
     в соответствии со ст. 65 Конституцией РФ."""
    region = region_name.lower()
    if region == 'кемеровская область':
        return 'Кемеровская область - Кузбасс'
    elif region in ('южная осетия', 'казахстан', 'германия'):
        return 'Иные территории, включая город и космодром Байконур'
    elif region == 'чувашия республика':
        return 'Чувашская Республика - Чувашия'
    elif region == 'ханты-мансийский-югра автономный округ':
        return 'Ханты-Мансийский автономный округ - Югра'
    elif region == 'ямало-ненецкий автономный округ':
        return 'Ямало-Ненецкий автономный округ'
    if 'область' in region or 'край' in region:
        return region.capitalize()
    if 'автономный' in region and 'округ' in region:
        return region.capitalize()
    region = region.title()
    if 'Республика' in region:
        if region.split()[0].endswith('кая'):
            return region
        else:
            return f'Республика {region.split("Республика")[0].rstrip()}'
    return region


def find_db_indexes(filename: str) -> set:
    """Возвращает разницу между количеством почтовых индексов
    в БД и переданном файле."""
    db_indexes = set(i for i, in db.session.query(Address.index))
    file_indexes = set(int(i.get('INDEX')) for i in DBF(filename))
    new_indexes = file_indexes - db_indexes
    return new_indexes


def fill_db_with_addresses_delta(filename: str) -> None:
    """Заполняет БД данными о почтовых адресах базы
    АО \"Почты России\"."""
    new_indexes = find_db_indexes(filename)
    addresses = DBF(filename)
    addresses_list = []
    regions = {item.name: item.region_id for item in Region.query.all()}
    for address in addresses:
        try:
            index = int(address.get('INDEX'))
            if index in new_indexes:
                if address.get('REGION'):
                    dbf_region = address.get('REGION')
                else:
                    dbf_region = address.get('AUTONOM')

                region_id = regions[cast_reg_pochta_to_constitute(dbf_region)]
                new_address = Address(index=index,
                                      area=address.get('AREA'),
                                      locality=address.get('CITY'),
                                      region_id=region_id)
                addresses_list.append(new_address)
        except ValueError:
            print('Вместо индекса что-то странное, пропускаю строку')
    db.session.bulk_save_objects(addresses_list)
    db.session.commit()
