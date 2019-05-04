FROM python:3.7.2-stretch

WORKDIR /app

ADD requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ADD . /app

CMD ["uwsgi", "app.ini"]