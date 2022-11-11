FROM python:3.11

ENV HOME = /usr/src/ws_chat

WORKDIR $HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip
RUN pip install poetry 
RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-root

COPY . $HOME

WORKDIR $HOME

CMD python3.11 chat/main.py