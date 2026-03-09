# AGENTS.md

This file provides guidance to Agents when working with code in this repository.

## Commands

```shell
# Setup
uv sync
source .venv/bin/activate
pre-commit install

# Run the app locally (auto-activates venv via run.py)
python run.py

# Run as a module directly (requires activated venv)
python -m app

# Lint and format
uv run task ruff

# Run with Docker (primary deployment method)
docker compose up --build
```

There are no automated tests in this project.

## Architecture

This tool cleans COD-AB (Common Operational Datasets - Administrative Boundaries) geospatial files. Input files go in `data/inputs/`, outputs in `data/outputs/`, and `data/tmp/` holds intermediates.

**Input convention:** files must be named `{iso3}_admin{level}.gpkg` (e.g. `afg_admin2.gpkg`).

**Processing pipeline** (`app/__main__.py`):

1. `download_admin0()` — fetches the global Admin 0 boundary from UNOCHA ArcGIS Feature Services into `data/tmp/bnda_cty.parquet`
2. For each input file, runs three stages in sequence:
   - `clean_admin(layer)` — topology repair, reprojection to EPSG:4326, dissolves to all parent levels, computes area/centroid, writes to `data/outputs/cod_ab_{iso3}.gdb`
   - `edge_extender(layer)` — fixes boundary gaps/overlaps using PostGIS (runs via an embedded PostgreSQL instance in Docker)
   - `clean_admin_em(layer)` — clips edge-extended output against the Admin 0 boundary, produces `*_em` layers in the GDB

**Module breakdown:**

- `app/config.py` — global config: ArcGIS credentials, GDAL env vars, retry settings, paths, Parquet write options
- `app/download/` — ArcGIS token auth and feature service download
- `app/clean/` — GDAL pipeline wrappers (`pre_cleaning`, `cleaning`, `convert`) and column schema helpers
- `app/edge_extender/` — PostGIS-based edge matching pipeline with sub-steps: `inputs` → `lines` → `attempt` → `merge` → `outputs` → `cleanup`. Each step is a module with a `main(conn, name, file, layer)` function. `topology.py` validates no overlaps/gaps remain.

**Key design patterns:**

- GDAL CLI (`gdal vector pipeline`) is used heavily rather than Python bindings, called via `subprocess.run`
- PostGIS operations use `psycopg` with parameterized `SQL`/`Identifier` for safety
- The edge_extender pipeline runs all steps through `apply_funcs()` which manages a single shared `psycopg` connection
- Docker runs an embedded PostgreSQL/PostGIS instance; the app connects to `dbname=app` (default)

**Environment variables** (via `.env` file):
through `apply_funcs()` which manages a single shared `psycopg` connection

- Docker runs an embedded PostgreSQL/PostGIS instance; the app connects to `dbname=app` (default)

**Environment variables** (via `.env` file):

- `ARCGIS_SERVER`, `ARCGIS_USERNAME`, `ARCGIS_PASSWORD`, `ARCGIS_FOLDER` — ArcGIS credentials
- `DBNAME` — PostgreSQL database name (default: `app`)
- `DISTANCE` — edge extension distance in degrees (default: `0.0002`)
- `NUM_THREADS` — parallelism (default: `1`)
- `QUIET` — suppress topology error logs (default: `YES`)
- `ATTEMPT`, `WAIT`, `TIMEOUT` — retry settings for HTTP requests
