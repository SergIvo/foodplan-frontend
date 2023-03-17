FROM python:3.11.1-alpine3.17
LABEL maintainer="foodplan.tech"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python3 -m venv venv /py && \
    /py/bin/pip3 install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache build-base && \
    apk add --update --no-cache postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip3 install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip3 install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

ENV PATH="scripts:/py/bin:$PATH"

USER django-user

CMD ["run.sh"]