FROM node:10.6-alpine

RUN npm install -g ionic gulp && mkdir -p /usr/src/app/ionicapp
WORKDIR /usr/src/app/ionicapp
COPY src/ionicapp/ /usr/src/app/ionicapp/
RUN npm install -D -E @ionic/v1-toolkit && npm rebuild node-sass

CMD ["ionic", "serve", "--address=172.18.0.5", "--port=8100", "--no-open", "--no-livereload"]

EXPOSE 8100
