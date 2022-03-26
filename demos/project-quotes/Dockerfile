FROM python:3.9.9-slim-buster AS compile-image

ARG APP_VER
ARG DEMO_QUOTES_VER

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc libpq5 libpq-dev

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN pip install -U pip

COPY /demos/project-quotes/requirements*.txt .
RUN pip install -r requirements-docker.txt

COPY /demos/project-quotes/dist/dcx-project-quotes-${DEMO_QUOTES_VER}.tar.gz .
RUN tar -xzf dcx-project-quotes-${DEMO_QUOTES_VER}.tar.gz

COPY /dist/django-comments-xtd-${APP_VER}.tar.gz .
RUN tar -xzf django-comments-xtd-${APP_VER}.tar.gz
RUN cd django-comments-xtd-${APP_VER} && pip install .


FROM python:3.9.9-slim-buster AS build-image

ARG DEMO_QUOTES_VER

RUN apt-get update
RUN apt-get install -y --no-install-recommends libpq5

COPY --from=compile-image /opt/venv /opt/venv
COPY --from=compile-image /dcx-project-quotes-${DEMO_QUOTES_VER} /dcx-project-quotes-${DEMO_QUOTES_VER}
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /dcx-project-quotes-${DEMO_QUOTES_VER}/project_quotes

EXPOSE 8048

CMD ./docker-entrypoint.sh
