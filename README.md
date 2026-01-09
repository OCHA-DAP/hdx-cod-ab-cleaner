# Cleaner for COD-AB Datasets

## Development

### Environment

[uv](https://github.com/astral-sh/uv) is used for package management with development done using Python >=3.13. Pre-commit formatting follows [ruff](https://docs.astral.sh/ruff/) guidelines. To get set up:

```shell
    uv sync
    source .venv/bin/activate
    pre-commit install
```

### Running

Add files to be processed into `data/inputs`. Files here must start with a country ISO-3 code and end with the admin level, for example: `afg_admin2.gpkg`.

To run with Docker:

```shell
    docker compose up --build
```
