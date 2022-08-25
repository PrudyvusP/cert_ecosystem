from organizations.fill_data import cast_reg_pochta_to_constitute


def test_casting_region_name() -> None:
    """Функция для тестов функции cast_reg_pochta_to_constitute."""
    assert cast_reg_pochta_to_constitute('КЕМЕРОВСКАЯ ОБЛАСТЬ') == (
        'Кемеровская область - Кузбасс')
    assert cast_reg_pochta_to_constitute('КАЗАХСТАН') == (
        'Иные территории, включая город и космодром Байконур')
    assert cast_reg_pochta_to_constitute('ЧУВАШИЯ РЕСПУБЛИКА') == (
        'Чувашская Республика - Чувашия')
    assert cast_reg_pochta_to_constitute('ПЕРМСКИЙ КРАЙ') == 'Пермский край'
    assert cast_reg_pochta_to_constitute('АРХАНГЕЛЬСКАЯ ОБЛАСТЬ') == (
        'Архангельская область')
    assert cast_reg_pochta_to_constitute('БУРЯТИЯ РЕСПУБЛИКА') == (
        'Республика Бурятия')
    assert cast_reg_pochta_to_constitute('СОВЕТСКАЯ РЕСПУБЛИКА') == (
        'Советская Республика')
    assert cast_reg_pochta_to_constitute('МОСКВА') == 'Москва'
    assert cast_reg_pochta_to_constitute('ЧУКОТСКИЙ АВТОНОМНЫЙ ОКРУГ') == (
        'Чукотский автономный округ')
