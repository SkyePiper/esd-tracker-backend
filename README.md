## Setup

To run this application, you will need python 3.12 and poetry
- [ ] [Python 3.12](https://www.python.org/downloads/)
- [ ] [poetry](https://python-poetry.org/)

Do note that the poetry environment will not work if you are using a python version older than 3.12, nor will it work 
with 3.13 and above

## Installing Packages
```bash
poetry shell
poetry install
```

## Running

Make sure you are in the poetry environment
```bash
poetry shell
```

You can then run it with default host and port:
```bash
py main.py
```

Or you can supply a host and port:
```bash
uvicorn --host {host} --port {port} main:app
```

To see the API docs, navigate to the relevant host and port, and add `/docs` for the path.
For instance, the default is [http://localhost:8000/docs](http://localhost:8000/docs)