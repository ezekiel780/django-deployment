FROM python:3.14-slim
LABEL maintainer="lipschitzappdeveloper.com"

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /requirements.txt
COPY ./api /api

WORKDIR /api
EXPOSE 8000

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev libffi-dev gcc && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip setuptools wheel && \
    /py/bin/pip install -r /requirements.txt && \
    apt-get purge -y --auto-remove build-essential gcc && \
    rm -rf /var/lib/apt/lists/* && \
    adduser --disabled-password --gecos "" app && \
    mkdir -p /home/app/app/staticfiles /home/app/app/mediafiles /vol && \
    chown -R app:app /home/app /vol && \
    chmod -R 755 /vol
ENV PATH="/py/bin:$PATH"

USER app
