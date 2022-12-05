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

Сервис написан на Flask с использованием Flask-admin в целях получения большей функциональности при минимальной вёрстке.
В качестве БД используется PostgreSQL.

### Переменные окружения
В директории  `organizations` проекта должен быть предусмотрен файл `.env`, в котором должны быть определены
обязательно следующие переменные окружения:
```bash
SECRET_KEY=<secret_key>
FLASK_ENV=<development/testing/production>
```

В режиме **production** в качестве БД используется PostgreSQL, которая хочет видеть 
такие переменные окружения для подключения:
```bash
DB_HOST=<db_host>
DB_NAME=<db_name>
DB_PORT=<db_port>
POSTGRES_USER=<db_user>
POSTGRES_PASSWORD=<db_password>
```

### Использование

Клонировать проект:
```bash
git clone https://github.com/PrudyvusP/cert_ecosystem.git && cd "$(basename "$_" .git)"
```

Для быстрого развертывания предусмотрен скрипт **setup.sh**, который создаст виртуальное
окружение, загрузит необходимые зависимости, добавит необходимые переменные окружения (режим **testing**), 
осуществит миграции БД (дополнительно добавив сведения о регионах и округах РФ), а также
зальет тестовые данные для демонстрации логики работы сервиса:

```bash
bash setup.sh
```

Backend-сервером выступает gunicorn:
```bash
venv/bin/gunicorn -b localhost:8000 -w 3 app:app --access-logfile -
```

#### Сведения из ЕГРЮЛ в форме поиска

Если дополнительно развернуть в докере [данный сервис](https://github.com/PrudyvusP/egrul_fts_api)
на http://localhost:28961, то возможно добавлять организации из ЕГРЮЛ в рабочее пространство через форму поиска.  
В файле с переменными окружения *.env* нужно указать соответствующий URL. 
```
EGRUL_SERVICE_URL=http://127.0.0.1:28961/
```

P.S. порт **28961** занят Call of Duty 4, поэтому на боевом сервере можно смело его использовать.  

### Deploy

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
После создания перезапустим службы и запустим *cert_ecosystem*:
```bash
sudo systemctl daemon-reload
sudo systemctl start cert_ecosystem
```


### PostgreSQL пример набора команд

Создать базу данных, создать пользователя, дать ему права, использовать созданную базу,
убедиться в том, что в таблице **regions** есть записи о регинонах:
```bash
sudo -iu postgres psql
CREATE DATABASE cert_db;
CREATE USER cert_user WITH PASSWORD '1q2w3e4r';
GRANT ALL PRIVILEGES ON DATABASE cert_db TO cert_user;
\c cert_db;
SELECT COUNT(*) FROM regions;
```

### Management-команды

Команда index проверяет наличие обновления или обновляет БД сведениями
о почтовых индексах. На вход хочет получать файл вида ```PIndx*.dbf```, 
который загружается [отсюда](https://www.pochta.ru/support/database/ops).
```bash
flask index -f <path_to_file> check
flask index -f <path_to_file> update
```

### Вместо заключения

В сервисе отсутствует модуль аутентификации, так как сервис эксплуатируется
в настоящее время в режиме "все пользователи равны", а для всего остального есть
~~MasterCard~~ pg_dump :)
