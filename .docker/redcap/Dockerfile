FROM python:alpine

RUN apk update
RUN apk add --upgrade gcc make wget supervisor postgresql-dev postgresql-contrib python3-dev libffi-dev musl-dev 

ADD requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ADD config/supervisor/* /etc/supervisor.d/

RUN apk del gcc make wget postgresql-dev  python3-dev libffi-dev musl-dev

CMD supervisord -n
