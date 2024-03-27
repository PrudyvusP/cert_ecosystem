FROM python:3.8-slim
LABEL author="vgolosyandriya@yandex.ru" version=0.1
WORKDIR /app
RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
ENTRYPOINT ["gunicorn", "app:app", "--bind", "0:5000" ]