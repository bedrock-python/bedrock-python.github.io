FROM postgres:17
ARG PG_PARTMAN_VERSION=5.5.0
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl make postgresql-server-dev-17 \
    && curl --fail --location --retry 3 "https://github.com/pgpartman/pg_partman/archive/refs/tags/v${PG_PARTMAN_VERSION}.tar.gz" -o /tmp/pg_partman.tar.gz \
    && tar -xzf /tmp/pg_partman.tar.gz -C /tmp \
    && make -C "/tmp/pg_partman-${PG_PARTMAN_VERSION}" NO_BGW=1 install \
    && rm -rf /tmp/pg_partman* \
    && rm -rf /var/lib/apt/lists/*
