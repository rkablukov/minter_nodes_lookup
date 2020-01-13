FROM python:3.6-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk add --update alpine-sdk

COPY ./requirements.txt /usr/src/app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY ./ /usr/src/app

ENV FLASK_DEBUG False

EXPOSE 80

CMD ["./manage.py", "runserver", "--host=0.0.0.0", "--port=80"]