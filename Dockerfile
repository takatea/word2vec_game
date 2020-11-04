FROM python:3.6.12

WORKDIR /usr/src/app
COPY requirements.txt .

RUN pip install -r requirements.txt