# README #

This blog-like backend is done as part of an [assignment](ASSIGNMENT.md)!

## Notes on local installation for dev environment ##

**IMPORTANT** Create .env file based on .env.example!

## How to run ##

Run

```bash
docker-compose up -d --build
```

OR, if you do not need pgadmin:

```bash
docker-compose up -d postgres app --build
```

Then go to <http://127.0.0.1:8000/docs> to view **OpenAPI docs**!

## Alternative: Run in local virtual environment ##

### Install python prerequisites on Ubuntu 20.04 LTS ###

```bash
sudo apt install virtualenv python3.10 python3.10-dev python3.10-venv pkg-config gcc libpq-dev
virtualenv -p python3.10 venv
```

### Activate virtual environment, update, install requirements ###

```bash
source venv/bin/activate
# Update PIP
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
pip install --upgrade pip
pip install -r requirements.txt
```

### Run other components and application ###

Bring up everything except the main service through docker:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres pgadmin
```

Run the application locally:

```bash
source activate_venv # If not already active
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then go to <http://127.0.0.1:8000/docs>! That is where the **OpenAPI docs** are at!

## Dev: Generate DB migrations ##

With the database running, generating migrations (in online mode), is done via:

**Important note**: Follow the directions in app.models `__init__.py` whenever making changes to models!

```bash
source activate_venv # If not already active
alembic revision --autogenerate -m "Migration Message"
```

## Dev: Project structure ##

The entire application is in the `app` directory, which is also the main module.

Its submodules are:

- `models`: The database models, based on the SQLalchemy ORM.
- `routers`: The routers / controllers of the application, based on FastAPI and Pydantic.
- `schemas`: The schemas / DTOs of the app, based on Pydantic.
- `utils`: The utilities / service facade of the app, based on FastAPI and SQLalchemy.
- `tests`: Tests for the project, based on pytest. Refer to [TESTING.md](./TESTING.md) for more.

The database.py file prepares the database configuration based on the set environment.
The main.py is the entrypoint of the application.

The database migrations are all at the `db_migrations` directory.

## Dev: Extra tools ##

The [scripts](./scripts/) directory includes all shell scripts that can help with different tasks.

**Recommended**: Use ./scripts/update_requirements.sh so as to keep the requirements file clean whenever installing. Also add any development-only dependency on it as an exception.

## Dev: Debugger attachment ##

For vs-code, add this object to .vscode/launch.json configurations array:

```json

{
    "name": "Python: FastAPI",
    "type": "python",
    "request": "launch",
    "module": "uvicorn",
    "args": [
        "app.main:app",
        "--reload"
    ],
    "console": "integratedTerminal",
    "justMyCode": true
}
```
