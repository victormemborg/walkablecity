FROM python:3.12-slim

RUN pip install \
    dagster \
    dagster-graphql \
    dagster-webserver \
    dagster-postgres \
    dagster-docker

ARG DAGSTER_HOME
ENV DAGSTER_HOME=${DAGSTER_HOME}

WORKDIR ${DAGSTER_HOME}

COPY dagster.yaml workspace.yaml ./

