import click
from flask.cli import with_appcontext

from .pindex_to_db import fill_db_with_addresses_delta, find_db_indexes
from .utils import get_cur_time
from .xml_parser import XMLHandler

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-f", "--file-name", "path_to_file", required=True,
              type=click.Path(exists=True),
              help="Путь до файла базы индексов.")
@click.pass_context
def index(ctx, path_to_file):
    """Работает с почтовыми индексами."""

    if not path_to_file.endswith(".dbf"):
        raise click.UsageError("Файл должен иметь формат .dbf")
    ctx.ensure_object(dict)
    ctx.obj['FILE_NAME'] = path_to_file
    click.echo(f"Начинаю работу с {path_to_file}")


@index.command()
@click.pass_context
@with_appcontext
def check(ctx):
    """Определяет разницу между индексами из БД и <file-name>."""

    file_name = ctx.obj.get('FILE_NAME')
    new_indexes = find_db_indexes(file_name)
    click.echo(f"Количество новых индексов: {len(new_indexes)}")


@index.command()
@click.confirmation_option(
    prompt='Вы точно хотите залить новые индексы в БД?')
@click.pass_context
@with_appcontext
def update(ctx):
    """Обновляет БД новыми адресами из <file-name>."""

    file_name = ctx.obj.get('FILE_NAME')
    fill_db_with_addresses_delta(file_name)
    click.echo("Успех")


@click.command()
@click.option("-s", "--schema", "schema", required=True,
              type=click.Path(exists=True),
              help="Путь до файла со схемой.")
@click.option("-f", "--file", "file", required=True,
              type=click.Path(exists=True),
              help="Путь до файла с файлом.")
@click.pass_context
@with_appcontext
def parse(ctx, schema, file):
    """Парсит XML-файл."""

    cur_time = get_cur_time()
    log_file_name = f'{file}-{cur_time}.log'
    handler = XMLHandler(file=file, schema=schema, logger_name='xml_parser',
                         logger_file=log_file_name)
    if handler.handle():
        click.echo("Успех")
    else:
        click.echo("Неудача. Смотри лог")
