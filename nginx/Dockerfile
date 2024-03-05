FROM ghcr.io/nginxinc/nginx-unprivileged:1.25.0-alpine3.17 AS base

FROM base AS dev
COPY templates/default.conf.template /etc/nginx/templates/default.conf.template

FROM base AS prod
COPY templates/prod.conf.template /etc/nginx/templates/default.conf.template