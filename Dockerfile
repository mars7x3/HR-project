FROM python:3.8

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./rex.txt /usr/src/rex.txt
RUN pip install -r /usr/src/rex.txt

COPY . /usr/src/app
