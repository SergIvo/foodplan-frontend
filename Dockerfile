FROM python:3.11.1-alpine3.17
LABEL maintainer="foodplan.tech"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python3 -m venv venv /py && \
    /py/bin/pip3 install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache build-base && \
    apk add --update --no-cache postgresql-dev && \
    apk add --update --no-cache musl-dev && \
    /py/bin/pip3 install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip3 install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"

USER django-user