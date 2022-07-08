FROM python:3.8-slim

WORKDIR /usr/ticket_scoring_api

RUN mkdir -pv /var/{log,run}/gunicorn/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .