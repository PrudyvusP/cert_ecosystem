import re
from enum import Enum
from typing import Literal

from petrovich.enums import Case, Gender
from petrovich.main import Petrovich


class Genders(Enum):
    MALE = 'мужской'
    FEMALE = 'женский'


class LingvaMaster(Petrovich):
    """Дополнение класса Petrovich доп функциями."""

    def __init__(self,
                 gender: Literal[Genders.MALE, Genders.FEMALE],
                 fio: str) -> None:
        super().__init__()
        self.gender = gender
        self.fio = fio.title()
        self.last_name = self.fio.split()[0]
        self.first_name = self.fio.split()[1]
        self.third_name = self.fio.split()[2]

    def get_initials(self) -> str:
        return f'{self.first_name[0]}.{self.third_name[0]}.'

    def get_doc_greeting(self) -> str:
        first_and_third_names = self.first_name + ' ' + self.third_name + '!'
        if self.gender == 'мужской':
            return 'Уважаемый' + ' ' + first_and_third_names
        return 'Уважаемая' + ' ' + first_and_third_names

    def get_dative_last_name(self):
        if self.gender == 'мужской':
            if re.search(r'\b\w+я\b', self.last_name):
                name = re.sub(r'\b(\w+)я\b', r'\1е', self.last_name)
            elif re.search(r'\b\w+[иы]х\b', self.last_name):
                name = self.last_name
            else:
                name = super().lastname(self.last_name, Case.DATIVE,
                                        Gender.MALE)
            return name
        return super().lastname(self.last_name, Case.DATIVE, Gender.FEMALE)

    def get_dative_last_name_with_initials(self):
        return self.get_initials() + ' ' + self.get_dative_last_name()


if __name__ == '__main__':

    test_data_male = {
        'иванов иван иванович': ('И.И. Иванову', 'Иван Иванович'),
        'Круглый Геннадий Иванович': ('Г.И. Круглому', 'Геннадий Иванович'),
        'петросян Игорь Валерьевич': ('И.В. Петросяну', 'Игорь Валерьевич'),
        'Лобня Юрий Дмитриевич': ('Ю.Д. Лобне', 'Юрий Дмитриевич'),
        'Чеснаускис Ростов Капралович':
            ('Р.К. Чеснаускису', 'Ростов Капралович'),
        'Жук Жуков Жукович': ('Ж.Ж. Жуку', 'Жуков Жукович')}

    test_data_female = {
        'глушко ирина андреевна': ('И.А. Глушко', 'Ирина Андреевна'),
        'Колыма Анна Геннадьевна': ('А.Г. Колыма', 'Анна Геннадьевна'),
        'Яркая Личность Константиновна': (
            'Л.К. Яркой', 'Личность Константиновна'),
        'Тестова Ирина Лжедмитриевна':
            ('И.Л. Тестовой', 'Ирина Лжедмитриевна'),
        'Жук Жукова Жуковичевна': ('Ж.Ж. Жук', 'Жукова Жуковичевна')}

    for k, v in test_data_male.items():
        p = LingvaMaster('мужской', k)
        assert p.get_dative_last_name_with_initials() == v[0], 'HELP MALE'
        assert p.get_doc_greeting() == f'Уважаемый {v[1]}!'

    for k, v in test_data_female.items():
        p = LingvaMaster('женский', k)
        assert p.get_dative_last_name_with_initials() == v[0], 'HELP FEMALE'
        assert p.get_doc_greeting() == f'Уважаемая {v[1]}!'
