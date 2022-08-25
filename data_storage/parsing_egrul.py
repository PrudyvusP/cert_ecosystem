import os
import xml.etree.cElementTree as el_tree

from organizations import create_app
from organizations.extentions import db
from organizations.models import Organization, Region
from organizations.utils import get_alpha_num_string


def get_geography_string(data_info, _type, name):
    if data_info is not None:
        data_info = data_info.attrib
        data_type = data_info.get(_type, '')
        data_name = data_info.get(name, '')
        if data_name.lower() == 'город':
            return f'{data_name} {data_type}, '
        return f'{data_type} {data_name}, '
    return ''


counter_norm = 0
counter_likv = 0
app = create_app()
counter = 0
with app.app_context():

    for root, dirs, files in os.walk('EGRUL_DATA'):
        for file in files:
            counter += 1
            print(f'Working with {file}')
            tree = el_tree.parse(root + '/' + file)
            elements = tree.findall('СвЮЛ')
            for element in elements:
                main_info = element.attrib

                if element.find('СвПрекрЮЛ'):
                    counter_likv += 1
                else:
                    counter_norm += 1
                    name_info = element.find('СвНаимЮЛ').attrib
                    main_address_info = element.find('СвАдресЮЛ/АдресРФ').attrib

                    region_code = int(main_address_info.get('КодРегион', 0))
                    index = int(main_address_info.get('Индекс', 0))

                    house = main_address_info.get('Дом', '')
                    house = house.replace('-', '')
                    if house:
                        house += ', '
                    building = main_address_info.get('Корпус', '')
                    building = building.replace('-', '')
                    if building:
                        building += ', '
                    flat = main_address_info.get('Кварт', '')
                    flat = flat.replace('-', '')
                    if flat:
                        flat += ', '

                    street_info = element.find('СвАдресЮЛ/АдресРФ/Улица')
                    street = get_geography_string(street_info,
                                                  'ТипУлица',
                                                  'НаимУлица')

                    region_info = element.find('СвАдресЮЛ/АдресРФ/Регион')
                    region = get_geography_string(region_info,
                                                  'НаимРегион',
                                                  'ТипРегион')
                    city_info = element.find('СвАдресЮЛ/АдресРФ/Город')
                    city = get_geography_string(city_info,
                                                'ТипГород',
                                                'НаимГород')
                    locality_info = element.find('СвАдресЮЛ/АдресРФ/НаселПункт')
                    locality = get_geography_string(locality_info,
                                                    'ТипНаселПункт',
                                                    'НаимНаселПункт')

                    factual_address = (f'{street}{house}{building}{flat}'
                                       f'{region}{city}{locality}{index}')
                    #print(factual_address)
                    if name_info.get('НаимЮЛСокр') and len(name_info.get('НаимЮЛСокр')) < 4:
                        short_name = None
                    else:
                        short_name = name_info.get('НаимЮЛСокр', name_info['НаимЮЛПолн']).strip()

                    region = Region.query.get(region_code)
                    # print(main_info, name_info, main_address_info, region_info)
                    # gorod_info = element.find('СвАдресЮЛ/АдресРФ/Город').attrib

                    full_name = name_info['НаимЮЛПолн'].strip()

                    org = Organization(full_name=full_name,
                                       short_name=short_name,
                                       inn=main_info.get('ИНН', None),
                                       ogrn=main_info['ОГРН'],
                                       factual_address=factual_address,
                                       region=region
                                       )
                    db.session.add(org)

    db.session.commit()
print(counter_norm, counter_likv)
print(counter, '- files')

words = ['Индекс', 'КодРегион', 'НаимЮЛПолн', 'НаимЮЛСокр', 'ТипРегион', 'НаимРегион', 'НаимГород']
full_words = ['ОГРН', 'ИНН', 'КПП', 'Индекс', 'КодРегион', 'НаимЮЛПолн', 'НаимЮЛСокр', 'ТипРегион', 'НаимРегион',
              'НаимГород']
