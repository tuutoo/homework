FROM ghcr.io/nginxinc/nginx-unprivileged:1.25.0-alpine3.17@sha256:e57300e9f60e521c5af3ec8fdc710285a371647e8033bcb8a36020c4394db3e3 AS base

FROM base AS dev
COPY templates/default.conf.template /etc/nginx/templates

FROM base AS prod
COPY templates/prod.conf.template /etc/nginx/templates