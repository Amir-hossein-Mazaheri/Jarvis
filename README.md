# How to run bot

### it is much different for development and production so I made two different description

<br>

## Pre Requirements

<ul>
    <li>Docker</li>
    <li>Python(a version with async support)</li>
</ul>

<br>

## Development

first you should make a file called .env which follow instructions of .env.example(copy and paste the fill it with correct info)

second run below command to run the database with docker compose:

```bash
docker compose -f docker-compose.dev.yml up -d
```

then you should execute the main.py like:

```bash
python main.py
```

if you are on linux you should use python3 instead on python

<br>

### Alernative way for running python command

<br>

if you want to change the code and see the result constantly follow these commands:

first you should install NodeJS on you computer then run the bellow command

```bash
    npm i -g nodemon
```

then for running the bot run this:

```bash
    nodemon --w . --exec python main.py
```

with this command the you don't need to rerun the command when you edit code

## Production

comming soon
