# kss-docker

proof-of-concept

## Installation

The follwing was performed on a clean Debian 10.5 install

```bash
sudo apt install -y curl pipenv
```

### Pyenv

```bash
sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

curl https://pyenv.run | bash
```

don't forget to add pyenv to your path

```bash
pyenv install 3.8.5
```

### Docker

https://docs.docker.com/engine/install/debian/

```bash
sudo usermod -aG docker $(whoami)
```

You will likely have to restart before docker will actually work

Pull the container(s)
```bash
docker pull nginx
```

### App

```bash
pipenv install
pipenv run alembic upgrade head
```

#### Generate secret key

idgaf how you do it, here's an example:

```bash
python3 -c 'from secrets import token_urlsafe;print(token_urlsafe(128))'
```

move .env.example to .env and put this in `SECRET_KEY`

## Run dev server

```bash
pipenv run uvicorn app:app --reload
```

There are 2 demo users, `admin:admin` and `user:user`, very creative and secure

## Useful shit

https://docs.sqlalchemy.org/en/13/orm/
https://docs.sqlalchemy.org/en/13/core/dml.html
https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script
https://alembic.sqlalchemy.org/en/latest/autogenerate.html
https://fastapi.tiangolo.com/advanced/async-sql-databases/

https://pypi.org/project/Starlette-WTF/
