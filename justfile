@help:
    just --list

@i:
    chmod +x ./scripts/install
    ./scripts/install

@f:
    ./scripts/format

@t:
    ./scripts/test

@cov:
    ./scripts/coverage

@clean:
    ./scripts/clean

@set-hooks:
    ./scripts/pre-commit
    ./scripts/pre-push

@serve-app:
    uvicorn app.app:app --reload --port=6969

@serve-docs:
    mkdocs serve

@build-docs:
    mkdocs build

@info:
  echo "Running on {{arch()}} machine".
