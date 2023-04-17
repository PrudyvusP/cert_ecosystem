# https://www.pochta.ru/support/database/ops
import click
from flask.cli import with_appcontext

from .pindex_to_db import find_db_indexes, fill_db_with_addresses_delta
from .send_email_msg_report import send_notify_email

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
@click.pass_context
@with_appcontext
def notify(ctx):
    """Отправляет e-mail начальнику, содержащие
    письма с методическими документами,
    реквизиты которых не внесены в сервис."""
    send_notify_email()
