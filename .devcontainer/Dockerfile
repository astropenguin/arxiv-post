FROM mcr.microsoft.com/playwright:focal

COPY poetry.lock pyproject.toml ./
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry \
    && poetry install \
    && playwright install chromium \
    && yes | poetry cache clear --all pypi
