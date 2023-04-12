FROM node:16.17.0-alpine AS deps

WORKDIR /app

RUN npm i -g pnpm

COPY webapp/package.json webapp/pnpm-lock.yaml ./

RUN pnpm install 

COPY webapp ./

RUN pnpm build



FROM python:3.11-slim-bullseye as server

WORKDIR /app

ENV LANG C.UTF-8

ENV LC_ALL C.UTF-8

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONFAULTHANDLER=1

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install

RUN pipenv run pip freeze > requirements.txt

RUN rm -rf Pipfile Pipfile.lock

RUN pip install -r requirements.txt

RUN prisma generate

COPY ./ ./

COPY --from=deps /app/dist ./webapp/dist

RUN chmod +x run_bot.bash

ENV BOT_NAME=Jarvis

ENV MODE=production

EXPOSE 8000

CMD [ "./run_bot.bash" ]