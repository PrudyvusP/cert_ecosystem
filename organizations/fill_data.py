import os
import shutil
import uuid

from config import basedir
from data_storage.geography import geography
from data_storage.industries import industries
from organizations import create_app
from organizations.exceptions import (DirNotCreatedError,
                                      MainOrgDirNotCreatedError,
                                      MainOrgDirNotDeletedError,
                                      IndustriesNotAddedError,
                                      OkrugsNotAddedError,
                                      RegionsNotAddedError)
from organizations.extentions import db
from organizations.models import (Region, Okrug, Industry)

main_dir_name = os.path.join(basedir,
                             'organizations',
                             'static',
                             'organizations')


def create_main_dir() -> None:
    """Создает корневую директорию для хранения древа файлов организаций."""

    try:
        os.makedirs(main_dir_name, exist_ok=True)
    except OSError:
        raise MainOrgDirNotCreatedError()


def create_255dirs() -> None:
    """Создает 255 директорий для хранения файлов организаций."""

    prefixes = set([str(uuid.uuid4())[:2].upper() for _ in range(100000)])
    for prefix in prefixes:
        try:
            os.makedirs(os.path.join(main_dir_name, prefix), exist_ok=True)
        except OSError:
            raise DirNotCreatedError


def delete_255dirs() -> None:
    """Удаляет основную директорию рекурсивно."""

    try:
        shutil.rmtree(main_dir_name)
    except OSError:
        raise MainOrgDirNotDeletedError


def commit_or_raise_error(exception=Exception):
    """Осуществляет COMMIT данных сессии."""

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise exception
    finally:
        db.session.close()


def fill_db_with_industries(industries_data: dict) -> None:
    """Заполняет БД данными о сферах деятельности ресурсов."""

    industries = [
        Industry(
            industry_id=industry,
            name=industries_data[industry])
        for industry in industries_data
    ]
    db.session.bulk_save_objects(industries)
    commit_or_raise_error(IndustriesNotAddedError)


def fill_db_with_okrugs(districts_data: dict) -> None:
    """Заполняет БД данными об округах РФ."""

    okrugs = [
        Okrug(okrug_id=district[0],
              name=district[1])
        for district in districts_data
    ]
    db.session.bulk_save_objects(okrugs)
    commit_or_raise_error(OkrugsNotAddedError)


def fill_db_with_regions(districts_regions: dict) -> None:
    """Заполняет БД данными о регионах РФ."""

    regions_to_db = []

    for okrug, regions in districts_regions.items():
        for region in regions:
            new_region = Region(region_id=region[1],
                                name=region[0],
                                okrug_id=okrug[0])
            regions_to_db.append(new_region)

    other_region = Region(
        region_id=99,
        name='Иные территории, включая город и космодром Байконур',
        okrug_id=None
    )
    regions_to_db.append(other_region)
    db.session.bulk_save_objects(regions_to_db)
    commit_or_raise_error(RegionsNotAddedError)


def fill_real_data() -> None:
    """Заполняет БД географическими данными."""

    app = create_app()
    delete_255dirs()
    create_255dirs()

    with app.app_context():
        fill_db_with_okrugs(geography)
        fill_db_with_regions(geography)
        fill_db_with_industries(industries)


if __name__ == '__main__':
    fill_real_data()
