FROM alpine:edge

WORKDIR /srv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

RUN --mount=type=bind,source=uv.lock,target=/srv/uv.lock \
    apk add --no-cache \
        gdal-driver-parquet \
        gdal-driver-pg \
        gdal-tools \
        postgis \
        postgresql18-client \
        python3 && \
    python -m venv /opt/venv && \
    apk add --no-cache --virtual .build-deps \
        build-base \
        gdal-dev \
        python3-dev \
        uv && \
    uv sync --frozen --no-dev --no-editable && \
    apk del .build-deps && \
    mkdir -p /run/postgresql && \
    chown -R postgres:postgres /run/postgresql

USER postgres

RUN initdb -D /var/lib/postgresql/data && \
    pg_ctl start -D /var/lib/postgresql/data && \
    createdb app && \
    psql -d app -c "CREATE EXTENSION postgis;"

COPY docker-entrypoint.sh /usr/local/bin/
COPY app ./app

ENTRYPOINT ["docker-entrypoint.sh", "python", "-m", "app"]
