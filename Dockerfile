FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG PROJECT_DIR
WORKDIR ${PROJECT_DIR}
COPY Pipfile ${PROJECT_DIR}
RUN apt-get update && apt-get -y install libpq-dev gcc python3-dev musl-dev netcat \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pipenv \
    && pipenv lock \
    && pipenv requirements > requirements.txt \
    && pip install --no-cache-dir -r requirements.txt
COPY . ${PROJECT_DIR}
RUN chmod 777 -R ./shell_scripts
ENTRYPOINT /bin/bash ./shell_scripts/entrypoint.sh
