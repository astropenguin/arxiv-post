FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=$PATH:/root/.local/bin
ENV POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update \
    && apt-get install -y curl git python3 python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -
