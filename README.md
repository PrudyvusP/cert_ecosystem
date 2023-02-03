# cert_ecosystem

CERT_ecosystem - это сервис учета взаимодействия с юридическими лицами (организациями).
Основная бизнес-логика:
* с организацией может вестись рабочая переписка (Message);
* у организации могут быть информационные ресурсы (Resource), у которых может быть сфера(-ы) функционирования (Industry),
* организация может иметь организационно-распорядительные документы (OrgAdmDoc).
* организацию можно добавлять как вручную, так и с помощью 
[Единого государственного реестра юридических лиц (ЕГРЮЛ)](https://ru.wikipedia.org/wiki/%D0%95%D0%B4%D0%B8%D0%BD%D1%8B%D0%B9_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9_%D1%80%D0%B5%D0%B5%D1%81%D1%82%D1%80_%D1%8E%D1%80%D0%B8%D0%B4%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D1%85_%D0%BB%D0%B8%D1%86). 
* для использования сведений из ЕГРЮЛ в работе предусмотрено взаимодействие
с микро-сервисом [egrul_fts_api](https://github.com/PrudyvusP/egrul_fts_api) по API через форму поиска.  
* каждая организация и ее информационные ресурсы имеют географический адрес расположения (Address).
* любой адрес относится к определенному региону (Region) и округу (Okrug) соответственно.
Географические данные регионов и округов заполняются с помощью миграции данных, а данные адресов берутся из 
[Эталонного справочника почтовых индексов объектов почтовой связи АО "Почта России"](https://www.pochta.ru/support/database/ops)

Сервис написан на Flask с использованием [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/)
в целях получения большей функциональности при минимальной вёрстке. В качестве БД используется PostgreSQL.


## Установка

Клонировать проект:
```bash
git clone https://github.com/PrudyvusP/cert_ecosystem.git && cd "$(basename "$_" .git)"
```

Создать виртуальное окружение и активировать его:
```bash
python3 -m venv venv && source venv/bin/activate
```

Установить зависимости:
```bash
pip3 install -r requirements.txt
```

### Режимы работы

**production** - основной режим работы. DEBUG-режим выключен, в качестве БД используется PostgreSQL.  
**development** - режим работы для разработки. DEBUG-режим включен, все ошибки имеют подробное описание.
В качестве БД используется SQLite.  
**testing** - режим работы для отладки. DEBUG-режим выключен, БД - SQLite.  

В случае использования режима **production** необходимо предварительно подготовить PostgreSQL.  
Запустить консольную утилиту `psql`:

```bash
sudo -iu postgres psql
```

Cоздать базу данных, создать пользователя и дать ему права:
```psql
CREATE DATABASE <db_name>;
CREATE USER <db_user> WITH PASSWORD '<db_password>';
GRANT ALL PRIVILEGES ON DATABASE <db_name> TO <db_user>;
```

### Переменные окружения


В корне основной директории проекта должен быть создан файл с названием `.env`, в котором обязательно необходимо
указать следующие переменные окружения:  
**SECRET_KEY**=<ключ для защиты от CSRF-атак (любая строка)>  
**FLASK_ENV**=<среда использования (принимает значения development/testing/production)>  

#### Сведения из ЕГРЮЛ в форме поиска


Если дополнительно развернуть в докере [данный сервис](https://github.com/PrudyvusP/egrul_fts_api),
то возможно добавлять организации из ЕГРЮЛ в рабочее пространство через форму поиска.  
Для получения соответствующего функционала нужно задать следующую переменную окружения:  
**EGRUL_SERVICE_URL**=<url на котором расположен сервис с ЕГРЮЛ>

#### Режим production


Для использования возможностей сервиса в режиме **production** также нужно указать следующие
переменные окружения в файле `.env`:

**DB_NAME**=<название базы данных>  
**DB_HOST**=<доменное имя или ip-адрес, на котором вращается PostreSQL>  
**DB_PORT**=<порт, на котором слушает запросы PostreSQL>  
**POSTGRES_USER**=<пользователь, под которым будет работать сервис>  
**POSTGRES_PASSWORD**=<пароль, который использует пользователь для подключения>  

#### Пример файла, содержащего переменные окружения


```bash
SECRET_KEY=indonesia_Xena
FLASK_ENV=production
DB_NAME=cert_db
DB_HOST=127.0.0.1
DB_PORT=5432
POSTGRES_USER=cert_db_user
POSTGRES_PASSWORD=1q2w3e4r
EGRUL_SERVICE_URL=http://localhost:28961
```

### Настройка 


Для создания схемы БД необходимо применить подготовленные миграции:
```bash
flask db upgrade
```

#### Management-команды

Команда `flask index <path_to_file>` обрабатывает информацию о почтовых индексах. 
На вход хочет получать файл вида ```PIndx*.dbf```, 
который загружается [отсюда](https://www.pochta.ru/support/database/ops).

```bash
flask index -f <path_to_file> check
flask index -f <path_to_file> update
```
`check` - сравнивает данные в БД с файлом `<path_to_file>`;  
`update` - заполняет БД актуальными данными из `<path_to_file>`.

Таким образом, для первого использования необходимо выполнить команду `flask index <path_to_file> update`.

В консоли `psql` можно проверить результат применения миграций и залива сведений о регионах, например:
```psql
\c <db_name>;
SELECT COUNT(*) FROM regions;
```
Если вывод команды != 0, то миграции успешно применены, а сведения корректно залиты.


### Развертывание

Один из вариантов развертывания сервиса - это создание соответствующей службы.
Представим, что сервис должен вращаться от имени пользователя *debian* в домашней 
директории */home/debian/* и быть доступным по адресу *http://localhost:8000*.
В таком случае необходимо создать файл `/etc/systemd/system/cert_ecosystem.service`
как минимум следующего содержания:

```bash
[Unit]
Description=Cert Ecosystem Web Service
After=network.target
 
[Service]
User=debian
WorkingDirectory=/home/debian/cert_ecosystem/
ExecStart=/home/debian/cert_ecosystem/venv/bin/gunicorn -b localhost:8000 -w 3 app:app --access-logfile -
Restart=always

[Install]
WantedBy=multi-user.target
```

После заполнения файла `/etc/systemd/system/cert_ecosystem.service`
нужно создать символическую ссылку на сервис для автоматического поднятия службы, 
перезапустить конфигуратор служб и запустить *cert_ecosystem*:
```bash
sudo systemctl enable cert_ecosystem.service
sudo systemctl daemon-reload
sudo systemctl start cert_ecosystem
```

Убедиться в том, что сервис работает корректно можно переходом в браузере на адрес
http://localhost:8000.

### Дополнительно


В качестве статического сервера можно и нужно использовать либо Nginx либо Apache.
Данный сервис используется разработчиком в паре с Apache.


### Трудности бытия


Проблема:
*в pg_hba.conf нет записи для компьютера "<db_host>", пользователя "<db_user>",
базы "<db_name>", SSL выкл.*  
Решение:  
Открыть конфиг postgresql:
```bash
sudo vim /etc/postgresql/12/main/pg_hba.conf
```
Добавить строчку вида: `host  <db_name>  <db_user>  <db_host>:<db_port>   md5`

Перезапустить postresql:
```bash
sudo serivce postgresql reload
```

### Резервное копирование сведений

Для создания резервной копии БД можно использовать команду `pg_dump` в паре с `cron`.

Для формирования дампа из PostgreSQL может использоваться команда:
```bash
pg_dump -U <POSTGRES_USER> -h <DB_HOST> -p <DB_PORT> -d <DB_NAME> > <dump_name>.sql
```
Подробнее о бэкапе можно почитать [тут](https://habr.com/ru/post/595641/).

Для резервного копирования файлов организации может использоваться команда:
```bash
tar -zcf <path_to_dir_for_backups>.cert_org_files_backup-$(date +"%d-%m-%Y_%H-%M").tar.gz -C <path_to_dir_with_service>/cert_ecosystem/organizations/static/organizations .  
```
### Демонстрация бизнес-логики

Для быстрого развертывания предусмотрен скрипт **setup.sh**, который создаст виртуальное
окружение, загрузит необходимые зависимости, добавит необходимые переменные окружения (режим **testing**), 
сделает миграции БД (дополнительно добавив сведения о регионах и округах РФ), а также
зальет тестовые данные для демонстрации логики работы сервиса:

```bash
bash setup.sh
```