FROM python:3.11-slim-bullseye

WORKDIR /app

ENV LANG C.UTF-8

ENV LC_ALL C.UTF-8

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONFAULTHANDLER 1

RUN pip install pipenv

COPY Pipfile Pipfile.lock

RUN pipenv run pip freeze > requirements.txt

RUN rm -f Pipfile Pipfile.lock

RUN pip install -r requirements.txt

RUN prisma generate

COPY ./ ./

RUN chmod +x run_bot.bash

CMD [ "./run_bot.bash" ]