# Versions Details

## version 0.9.2 beta

Changes since the last version:

<ul>
    <li>Added Webapp front-end for building json files for tasks</li>
    <li>Added a simple REST api back-end to serve each team members</li>
</ul>

## version 0.8.3 beta

Changes since the last version:

<ul>
    <li>Added public announcement for admin user</li>
    <li>Added public announcement for updating bot for admin user</li>
    <li>Fixed some little but harmful bugs</li>
    <li>Fixed admin users list action too long message by adding pagination</li>
    <li>Improved code maintainability and made it more cleaner by adding some super handlers</li>
</ul>

## version 0.7 beta

Changes since the last version:

<ul>
    <li>Added multiple team support for users</li>
    <li>Fixed CallbackHandler pattern matching</li>
    <li>Added toggle edit info for admin user</li>
    <li>Added adding member from other team for head users</li>
    <li>Added removing member from team for head users</li>
    <li>Added see team members for head users</li>
</ul>

## version 0.5 beta

First public publish of bot

<br>

# How to run bot

### It is much different for development and production so I made two different description

<br>

## Pre Requirements

<ul>
    <li>Docker</li>
    <li>Python(a version with async support)</li>
</ul>

<br>

## Development

First you should make a file called .env which follow instructions of .env.example(copy and paste the fill it with correct info)

Second run below command to run the database with docker compose:

```bash
docker compose -f docker-compose.dev.yml up -d
```

Then you should execute the main.py like:

```bash
python main.py
```

If you are on linux you should use python3 instead on python

<br>

### Alernative way for running python command

<br>

If you want to change the code and see the result constantly follow these commands:

First you should install NodeJS on you computer then run the bellow command

```bash
    npm i -g nodemon
```

Then for running the bot run this:

```bash
    nodemon --w . --exec python main.py
```

With this command the you don't need to rerun the command when you edit code

<br>

## Production

First you need to ssh into your server and clone this repo like this:

```bash
git clone https://github.com/Amir-hossein-Mazaheri/Jarvis.git bot
cd bot
```

<br>

To run this app for production purpose you need to create secrets before you run docker

### List of secrets you need to create:

<ul>
    <li>db.txt</li>
    <li>db_user.txt</li>
    <li>db_pass.txt</li>
    <li>bot_token.txt</li>
    <li>bot_secret.txt</li>
    <li>server_ip.txt</li>
</ul>

<br>

Each of them is a text file that you must create

<br>

To make password or secret you can use following command:

```bash
openssl rand -hex 64
```

<br>

This command will log a 64 character string which is random to make it more fluid you can use this alternative command:

```bash
openssl rand -hex 64 > db_pass.txt
```

You can do the same thing for generating bot_secret.txt

<br>

After making secrets you're ready to run the app with the following command:

```bash
docker compose up -d
```

If you're struggling with compose cache you can use following command too(may or may not fix your problem):

```bash
docker compose up --build -d
```
