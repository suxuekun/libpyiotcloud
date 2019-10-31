FROM node:10.6-alpine

RUN npm install -g ionic gulp && mkdir -p /usr/src/app/ionicapp
WORKDIR /usr/src/app/ionicapp

ARG config_use_apiurl
RUN cat src/ionicapp/www/js/env.js | sed -i -r "s/'localhost'/'$config_use_apiurl'/" src/ionicapp/www/js/env.js

COPY src/ionicapp/ /usr/src/app/ionicapp/

RUN npm install -D -E @ionic/v1-toolkit && npm rebuild node-sass
CMD ["ionic", "serve", "--address=0.0.0.0", "--port=8100", "--no-open", "--no-livereload"]

EXPOSE 8100
