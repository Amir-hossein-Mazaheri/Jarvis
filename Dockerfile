FROM python:3.11-slim-bullseye

WORKDIR /app

ENV LANG C.UTF-8

ENV LC_ALL C.UTF-8

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONFAULTHANDLER 1

RUN pip install pipenv

COPY requirements.txt ./

# RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
RUN pip install -r requirements.txt

COPY ./ ./

RUN chmod +x run_bot.bash

CMD [ "./run_bot.bash" ]