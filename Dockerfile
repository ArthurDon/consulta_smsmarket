FROM python:3.7-alpine

WORKDIR /status-pin-api/
COPY . /status-pin-api/
RUN apk update && apk add --no-cache --update bash libxslt libxslt-dev libffi-dev linux-headers alpine-sdk build-base gcc mariadb-dev
RUN adduser -D px
USER px
COPY --chown=px:px . .
COPY --chown=px:px requirements.txt requirements.txt
ENV PATH=/home/px/.local/bin:${PATH}
RUN pip install --trusted-host pypi.python.org --user -r requirements.txt
CMD gunicorn -b 0.0.0.0:8080 main:app --workers=1 --threads=1 --log-level warning