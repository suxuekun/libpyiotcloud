FROM jenkinsci/blueocean

USER root

RUN apk add openrc && apk update && apk add docker && apk add py-pip && apk add python-dev libffi-dev openssl-dev gcc libc-dev make && pip install docker-compose && rc-update add docker boot

EXPOSE 8080
EXPOSE 50000
